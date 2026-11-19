#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GIỌNG RIÊNG: mẫu giọng của bạn (và người đã đồng thuận) trong kho, đăng ký với dịch vụ đám mây.

Hồ sơ giọng nằm ở kho: giong-noi/giong-noi.json, tệp mẫu ở giong-noi/<hồ sơ>/. Xưởng không giữ bản chép nào.
Máy đọc tại máy (VieNeu, Drama 3, Higgs v3) nhân bản tức thì từ mẫu chính mỗi lần đọc; Gemini và ElevenLabs cần
đăng ký một lần để có mã giọng. Chỉ nhân bản giọng của chính chủ, hoặc người đã đồng thuận bằng văn bản.

    # tạo hồ sơ (một lần cho mỗi người): ghi rõ ai đồng thuận, cho việc gì, ngày nào
    python3 tools/giong_rieng.py tao an --ho-ten "Họ và tên" --dong-thuan "Chủ giọng tự yêu cầu ... (ngày)"

    # trích đoạn mẫu ứng viên từ bản ghi sẵn có (cần transcript dạng xưởng phim: [{start, end, text}])
    python3 tools/giong_rieng.py trich <tệp âm thanh hay video> --transcript <x.transcript.json> --ra <thư mục> [--so 5]
    # đưa một mẫu vào kho (mặc định trạng thái "tam": dùng thử, chưa duyệt)
    python3 tools/giong_rieng.py them-mau an <tệp.wav> --loi "lời đúng như trong mẫu" --ngon-ngu vi [--chinh] [--duyet]
    python3 tools/giong_rieng.py them-dong-thuan an <tệp.wav> --ngon-ngu vi      # câu đồng thuận cho Gemini
    python3 tools/giong_rieng.py chon-chinh an <mã mẫu> --ngon-ngu vi
    python3 tools/giong_rieng.py dang-ky an --may gemini|elevenlabs [--mau <mã mẫu>]   # xếp việc, chạy trên máy thật
    python3 tools/giong_rieng.py xem [an]
"""
import argparse
import base64
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import am_thanh as A  # noqa: E402
import kho_tu_lieu  # noqa: E402

CAU_DONG_THUAN = {
    "vi": "Tôi là chủ sở hữu giọng nói này và tôi đồng ý cho Google sử dụng giọng nói này để tạo mô hình giọng nói tổng hợp.",
    "en": "I am the owner of this voice and I consent to Google using this voice to create a synthetic voice model.",
}


HUONG_DAN = ("Hồ sơ giọng nói dùng cho xưởng lồng tiếng. Mỗi khoá là một hồ sơ, xưởng gọi bằng @<khoá> (vd @an; "
             "@an#vi-02 để chọn đúng một mẫu). Chỉ ghi giọng của chính chủ, hoặc của người đã đồng thuận bằng văn bản "
             "(ghi ở 'dongThuan'). 'mau': đoạn mẫu 10-30 giây kèm lời khớp từng chữ; trangThai 'tam' (dùng thử) hoặc "
             "'duyet' (đã nghe và ưng). 'mauChinh': mẫu dùng mặc định theo ngôn ngữ. 'dongThuanGhiAm': câu đồng thuận "
             "đọc đúng nguyên văn, Gemini cần khi đăng ký giọng. 'dangKy': mã giọng trên dịch vụ đám mây, xưởng tự ghi. "
             "Sửa bằng tools/giong_rieng.py của xưởng lồng tiếng.")


def kho():
    import cau_hinh as CH
    k = kho_tu_lieu.tim()
    if not k:
        sys.exit("Không tìm thấy kho giọng. " + CH.LOI_KHO)
    return k


def p_ho_so():
    return os.path.join(kho(), "giong-noi", "giong-noi.json")


def doc_ho_so():
    if not os.path.isfile(p_ho_so()):
        return {"_huong-dan": HUONG_DAN}
    with open(p_ho_so(), encoding="utf-8") as f:
        return json.load(f)


def ghi_ho_so(d):
    os.makedirs(os.path.dirname(p_ho_so()), exist_ok=True)
    tmp = p_ho_so() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, p_ho_so())


def hom_nay():
    return dt.date.today().isoformat()


# ----------------------------------------------------------------------------- trích mẫu ứng viên
def trich(tep, transcript, ra, so=5, tu=12.0, den=25.0):
    with open(transcript, encoding="utf-8") as f:
        seg = json.load(f)
    seg = seg.get("segments", seg) if isinstance(seg, dict) else seg
    seg = [s for s in seg if s.get("text", "").strip() and s["end"] > s["start"]]
    sr = 16000
    print("Đang đọc âm thanh...", flush=True)
    mau = A.doc_pcm(tep, sr)
    db = A.muc_khung(mau, sr, 20)
    nguong = max(-55.0, sorted(db)[int(len(db) * 0.98)] - 40) if db else -50
    xen_khung = [sum(1 for x in mau[i:i + 320] if abs(x) >= 32700) for i in range(0, len(mau), 320)]
    ung = []
    for i in range(len(seg)):
        for j in range(i, len(seg)):
            if j > i and seg[j]["start"] - seg[j - 1]["end"] > 0.8:
                break
            dai = seg[j]["end"] - seg[i]["start"]
            if dai > den:
                break
            if dai < tu:
                continue
            a, b = int(seg[i]["start"] / 0.02), int(seg[j]["end"] / 0.02)
            k = sorted(db[a:b])
            if len(k) < 50:
                continue
            on = k[int(len(k) * 0.10)]
            noi = k[int(len(k) * 0.80)]
            tieng = [x for x in db[a:b] if x > nguong]
            ty_noi = len(tieng) / (b - a)
            tb = sum(tieng) / max(1, len(tieng))
            lech = (sum((x - tb) ** 2 for x in tieng) / max(1, len(tieng))) ** 0.5
            xen = sum(xen_khung[a:b])
            chu = " ".join(s["text"].strip() for s in seg[i:j + 1])
            diem = (noi - on) + 10 * ty_noi - 0.3 * lech - 0.5 * xen + (2 if chu.rstrip()[-1:] in ".!?" else 0)
            ung.append({"batDau": round(seg[i]["start"], 2), "ketThuc": round(seg[j]["end"], 2), "loi": chu,
                        "snr": round(noi - on, 1), "tyLeNoi": round(ty_noi, 2), "xen": xen, "diem": round(diem, 2)})
    ung.sort(key=lambda x: -x["diem"])
    chon = []
    for u in ung:
        if all(u["ketThuc"] <= c["batDau"] or u["batDau"] >= c["ketThuc"] for c in chon):
            chon.append(u)
        if len(chon) >= so:
            break
    os.makedirs(ra, exist_ok=True)
    goc = os.path.splitext(os.path.basename(tep))[0]
    for n, u in enumerate(chon, 1):
        u["tep"] = os.path.join(ra, f"{goc}-mau-{n:02d}.wav")
        subprocess.run([A.ffmpeg(), "-v", "error", "-y", "-ss", str(max(0, u["batDau"] - 0.1)),
                        "-to", str(u["ketThuc"] + 0.2), "-i", tep, "-ac", "1", "-ar", "48000",
                        "-af", "highpass=f=60", "-c:a", "pcm_s16le", u["tep"]], check=True)
        u["nguon"] = os.path.basename(tep)
        print(f"  {n}. {u['batDau']:.1f}-{u['ketThuc']:.1f}s  SNR {u['snr']} dB  điểm {u['diem']}: {u['loi'][:90]}")
    with open(os.path.join(ra, f"{goc}-mau.json"), "w", encoding="utf-8") as f:
        json.dump(chon, f, ensure_ascii=False, indent=1)
    return chon


# ----------------------------------------------------------------------------- hồ sơ trong kho
def ho_so(d, ten):
    if ten not in d:
        sys.exit(f"Kho chưa có hồ sơ giọng '{ten}'")
    return d[ten]


def tao(ten, ho_ten, dong_thuan):
    import re
    if not re.match(r"^[a-z0-9][a-z0-9-]{0,30}$", ten):
        sys.exit("Tên hồ sơ: chữ thường không dấu, số, gạch nối (vd an, minh-anh)")
    if not dong_thuan.strip():
        sys.exit("Cần ghi đồng thuận: ai cho phép dùng giọng, cho việc gì, ngày nào")
    d = doc_ho_so()
    if ten in d:
        sys.exit(f"Đã có hồ sơ {ten}")
    d[ten] = {"ten": ho_ten.strip(), "dongThuan": dong_thuan.strip(), "mau": [], "mauChinh": {},
              "dongThuanGhiAm": {}, "dangKy": {}}
    ghi_ho_so(d)
    print(f"Đã tạo hồ sơ giọng @{ten} ({ho_ten}) ở {p_ho_so()}")


def them_mau(ten, tep, loi, nn, ma=None, nguon=None, chinh=False, duyet=False):
    d = doc_ho_so()
    hs = ho_so(d, ten)
    ma = ma or f"{nn}-{len(hs.setdefault('mau', [])) + 1:02d}"
    if any(m["id"] == ma for m in hs["mau"]):
        sys.exit(f"Mã mẫu {ma} đã có")
    rel = f"giong-noi/{ten}/{ma}.wav"
    dich = os.path.join(kho(), rel)
    os.makedirs(os.path.dirname(dich), exist_ok=True)
    subprocess.run([A.ffmpeg(), "-v", "error", "-y", "-i", tep, "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le",
                    dich], check=True)
    hs["mau"].append({"id": ma, "tep": rel, "loi": loi.strip(), "ngonNgu": nn, "thoiLuong": round(
        len(A.doc_pcm(dich, 16000)) / 16000, 1), "nguon": nguon or os.path.basename(tep), "them": hom_nay(),
        "trangThai": "duyet" if duyet else "tam"})
    if chinh or not (hs.get("mauChinh") or {}).get(nn):
        hs.setdefault("mauChinh", {})[nn] = ma
    ghi_ho_so(d)
    print(f"Đã thêm mẫu {ma} vào hồ sơ {ten} ({rel})")


def them_dong_thuan(ten, tep, nn):
    d = doc_ho_so()
    hs = ho_so(d, ten)
    rel = f"giong-noi/{ten}/dong-thuan-{nn}.wav"
    os.makedirs(os.path.join(kho(), "giong-noi", ten), exist_ok=True)
    subprocess.run([A.ffmpeg(), "-v", "error", "-y", "-i", tep, "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le",
                    os.path.join(kho(), rel)], check=True)
    hs.setdefault("dongThuanGhiAm", {})[nn] = {"tep": rel, "cau": CAU_DONG_THUAN[nn], "them": hom_nay()}
    ghi_ho_so(d)
    print(f"Đã lưu câu đồng thuận {nn}: {rel}")


def chon_chinh(ten, ma, nn):
    d = doc_ho_so()
    hs = ho_so(d, ten)
    if not any(m["id"] == ma for m in hs.get("mau", [])):
        sys.exit(f"Không có mẫu {ma}")
    hs.setdefault("mauChinh", {})[nn] = ma
    ghi_ho_so(d)
    print(f"Mẫu chính {nn} của {ten}: {ma}")


# ----------------------------------------------------------------------------- đăng ký (chạy trên máy thật)
def _wav_24k(tep, tmp):
    ra = os.path.join(tmp, os.path.basename(tep))
    subprocess.run([A.ffmpeg(), "-v", "error", "-y", "-i", tep, "-ac", "1", "-ar", "24000", "-c:a", "pcm_s16le", ra],
                   check=True)
    return ra


def _goi(url, du_lieu, headers):
    rq = urllib.request.Request(url, data=du_lieu, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(rq, timeout=300) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"lỗi {e.code}: {e.read().decode('utf-8', 'replace')[:800]}")


def dang_ky_tren_mac(ten, may, ma_mau, khoa):
    if not khoa:
        raise RuntimeError(f"chưa có khóa {may}: chạy tệp 'Them khoa API' của xưởng trên máy thật")
    d = doc_ho_so()
    hs = ho_so(d, ten)
    nn_chinh = "vi"
    ma_mau = ma_mau or (hs.get("mauChinh") or {}).get(nn_chinh)
    mau = next((m for m in hs.get("mau", []) if m["id"] == ma_mau), None)
    if not mau:
        raise RuntimeError("chưa có mẫu chính để đăng ký")
    tep_mau = os.path.join(kho(), mau["tep"])
    with tempfile.TemporaryDirectory() as tmp:
        if may == "gemini":
            dt_ = hs.get("dongThuanGhiAm") or {}
            dt_mau = dt_.get(mau["ngonNgu"]) or dt_.get("vi") or dt_.get("en")
            if not dt_mau:
                raise RuntimeError("Gemini cần bản ghi câu đồng thuận (giong_rieng.py them-dong-thuan)")
            b64 = lambda p: base64.b64encode(open(_wav_24k(p, tmp), "rb").read()).decode()  # noqa: E731
            than = {"store": True, "voice": {"model": "gemini-3.8-flash-tts", "type": "replicated",
                                             "display_name": f"{hs.get('ten', ten)} ({mau['id']})",
                                             "replicated": {
                                                 "source_audio": {"mime_type": "audio/wav", "data": b64(tep_mau)},
                                                 "consent_audio": {"mime_type": "audio/wav",
                                                                   "data": b64(os.path.join(kho(), dt_mau["tep"]))}}}}
            kq = _goi("https://generativelanguage.googleapis.com/v1beta/voices", json.dumps(than).encode(),
                      {"x-goog-api-key": khoa, "Content-Type": "application/json"})
            ma = kq.get("id") or kq.get("name", "").split("/")[-1]
        elif may == "elevenlabs":
            ranh = uuid.uuid4().hex
            cac = [os.path.join(kho(), m["tep"]) for m in hs.get("mau", []) if m.get("trangThai") != "bo"][:5]
            phan = []
            for k, v in (("name", f"{hs.get('ten', ten)}"), ("remove_background_noise", "false"),
                         ("description", "Giọng riêng, dùng cho sản phẩm của chính chủ giọng")):
                phan.append(f"--{ranh}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
            for p in cac:
                phan.append(f"--{ranh}\r\nContent-Disposition: form-data; name=\"files\"; "
                            f"filename=\"{os.path.basename(p)}\"\r\nContent-Type: audio/wav\r\n\r\n".encode()
                            + open(p, "rb").read() + b"\r\n")
            phan.append(f"--{ranh}--\r\n".encode())
            kq = _goi("https://api.elevenlabs.io/v1/voices/add", b"".join(phan),
                      {"xi-api-key": khoa, "Content-Type": f"multipart/form-data; boundary={ranh}"})
            ma = kq.get("voice_id")
        else:
            raise RuntimeError(f"máy {may} không cần đăng ký")
    if not ma:
        raise RuntimeError("dịch vụ không trả mã giọng: " + json.dumps(kq, ensure_ascii=False)[:400])
    d = doc_ho_so()
    d[ten].setdefault("dangKy", {})[may] = {"id": ma, "mau": mau["id"], "luc": time.strftime("%Y-%m-%d")}
    ghi_ho_so(d)
    return ma


def xem(ten=None):
    d = doc_ho_so()
    for k, hs in d.items():
        if k.startswith("_") or (ten and k != ten):
            continue
        print(f"{k}: {hs.get('ten')}  mẫu chính {hs.get('mauChinh')}  đăng ký {hs.get('dangKy')}")
        for m in hs.get("mau", []):
            print(f"   {m['id']:10} {m['ngonNgu']} {m.get('thoiLuong')}s {m['trangThai']:5} {m['loi'][:70]}")
        print("   đồng thuận:", {k2: v['tep'] for k2, v in (hs.get('dongThuanGhiAm') or {}).items() if v})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="lenh", required=True)
    a = sp.add_parser("trich")
    a.add_argument("tep")
    a.add_argument("--transcript", required=True)
    a.add_argument("--ra", required=True)
    a.add_argument("--so", type=int, default=5)
    a = sp.add_parser("tao")
    a.add_argument("ten")
    a.add_argument("--ho-ten", required=True)
    a.add_argument("--dong-thuan", required=True)
    a = sp.add_parser("them-mau")
    a.add_argument("ten")
    a.add_argument("tep")
    a.add_argument("--loi", required=True)
    a.add_argument("--ngon-ngu", default="vi")
    a.add_argument("--ma")
    a.add_argument("--nguon")
    a.add_argument("--chinh", action="store_true")
    a.add_argument("--duyet", action="store_true")
    a = sp.add_parser("them-dong-thuan")
    a.add_argument("ten")
    a.add_argument("tep")
    a.add_argument("--ngon-ngu", default="vi")
    a = sp.add_parser("chon-chinh")
    a.add_argument("ten")
    a.add_argument("ma")
    a.add_argument("--ngon-ngu", default="vi")
    a = sp.add_parser("dang-ky")
    a.add_argument("ten")
    a.add_argument("--may", required=True, choices=["gemini", "elevenlabs"])
    a.add_argument("--mau")
    a = sp.add_parser("xem")
    a.add_argument("ten", nargs="?")
    a = ap.parse_args()
    if a.lenh == "tao":
        tao(a.ten, a.ho_ten, a.dong_thuan)
    elif a.lenh == "trich":
        trich(a.tep, a.transcript, a.ra, a.so)
    elif a.lenh == "them-mau":
        them_mau(a.ten, a.tep, a.loi, a.ngon_ngu, a.ma, a.nguon, a.chinh, a.duyet)
    elif a.lenh == "them-dong-thuan":
        them_dong_thuan(a.ten, a.tep, a.ngon_ngu)
    elif a.lenh == "chon-chinh":
        chon_chinh(a.ten, a.ma, a.ngon_ngu)
    elif a.lenh == "dang-ky":
        import hang_doi
        hang_doi.them_dang_ky(a.ten, a.may, a.mau)
    elif a.lenh == "xem":
        xem(a.ten)


if __name__ == "__main__":
    main()
