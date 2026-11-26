#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GHÉP TIẾNG: nối lượt đọc đã chọn của từng đoạn thành một bản lồng tiếng hoàn chỉnh.

    python3 tools/ghep_tieng.py "../Du an/<dự án>"                  # bản chính theo chon.json (thiếu thì lượt tốt nhất)
    python3 tools/ghep_tieng.py "../Du an/<dự án>" --ban-nhap       # bản nháp (cho phép thiếu đoạn)
    python3 tools/ghep_tieng.py "../Du an/<dự án>" --giao-phim "2026-11 Ten du an phim" [--ghi-de]

Thứ tự đoạn theo loi-doc.md hiện tại. Lượt cho mỗi đoạn: chon.json > "chon" (bạn chọn ở Bàn nghe), không có thì
lượt có điểm kiểm tốt nhất trong mọi lượt có cùng lời đọc. Mỗi lượt được cắt lặng đầu, cuối (giữ hơi thở mở 60 ms,
đuôi 150 ms), nối bằng quãng lặng nghiGiuaDoan cộng {ngừng x} và quãng sau tiêu đề mục, rồi chuẩn âm lượng về
-16 LUFS, đỉnh thật -1,5 dBTP, WAV 48 kHz 24-bit. Kèm phụ đề .srt (theo bản viết, chia câu) và mốc .moc.json.
--giao-phim chép bản chính sang "Du an/<dự án phim>/nguon/voice.wav" của xưởng phim (lối vào của infomotion, hoạt hình).

Ba khóa làm bản chỉ giọng nghe như người ngồi nói trong phòng (đặt ở đầu loi-doc.md, hoặc cờ dòng lệnh để thử):
    nenPhong: co        lót tiếng nền phòng thu của chủ giọng suốt bài (hồ sơ giọng > nenPhong), thay quãng 0 tuyệt đối;
                        số âm (vd -64) là mức RMS dBFS đích; mặc định lấy mức ồn nền đo thật của phòng
    coGianNghi: 0.1     quãng nghỉ giữa đoạn dao động ±10% quanh nghiGiuaDoan (cố định theo dự án, ghép lại vẫn y nguyên);
                        thẻ {ngừng x} và quãng sau tiêu đề mục giữ đúng như viết
    hoiTho: co          lót một hơi thở (hồ sơ giọng > hoiTho) trong quãng nghỉ trước đoạn dài;
                        hoiThoTu: 25 (số chữ tối thiểu), hoiThoCach: 20 (giây tối thiểu giữa hai hơi thở)
    python3 tools/ghep_tieng.py "../Du an/<dự án>" --nen-phong --co-gian 0.1 --hoi-tho --ten "B nen phong"   # bản thử
"""
import argparse
import array
import json
import os
import random
import re
import shutil
import sys
import tempfile
import zlib

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import am_thanh as A  # noqa: E402
import cau_hinh as CH  # noqa: E402
import loi_doc as L  # noqa: E402
import nen_phong as NP  # noqa: E402

SR = 48000
DEM_DAU, DEM_CUOI, MO_DAU, KET = 0.06, 0.15, 0.3, 0.6
THO_DINH = -40.0        # khung 10 ms to nhất của hơi thở (dBFS, trước chuẩn âm lượng)
THO_SAT = 0.10          # hơi thở dứt trước chữ đầu bao lâu (giây)
THO_LANG_TRUOC = 0.35   # quãng lặng tối thiểu còn lại trước hơi thở; không đủ thì bỏ hơi thở ở chỗ đó


def _bat(v):
    """Giá trị khóa đầu tệp -> (bật?, số nếu có)."""
    if v is None or v is False:
        return False, None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return True, float(v)
    s = str(v).strip().lower()
    if s in ("", "0", "khong", "không", "tat", "tắt", "false", "no", "off"):
        return False, None
    try:
        return True, float(s.replace(",", "."))
    except ValueError:
        return True, None


def _ho_so(tt):
    try:
        return CH.giong(tt.get("giong")) or {}
    except SystemExit:
        return {}


def _tep_kho(rel):
    return rel if os.path.isabs(rel) else CH.giai("@kho/" + rel)


def nap_hoi_tho(ds, dinh=THO_DINH):
    """Các hơi thở đã chỉnh về cùng độ to (array 'h')."""
    ra = []
    for rel in ds:
        p = _tep_kho(rel)
        if not os.path.isfile(p):
            continue
        m = A.doc_pcm(p, SR)
        db = A.muc_khung(m, SR, 10)
        if not db:
            continue
        g = 10 ** ((dinh - max(db)) / 20)
        ra.append(array.array("h", (max(-32768, min(32767, int(x * g))) for x in m)))
    return ra


def cac_luot(du_an):
    d = os.path.join(du_an, "luot")
    if not os.path.isdir(d):
        return []
    ra = []
    for ten in sorted(os.listdir(d)):
        p = os.path.join(d, ten, "luot.json")
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as f:
                lt = json.load(f)
            k = os.path.join(d, ten, "kiem.json")
            lt["_kiem"] = json.load(open(k, encoding="utf-8")) if os.path.isfile(k) else {}
            ra.append(lt)
    return ra


def chon_tep(du_an, kb, chi_luot=None, dung_chon=True):
    """{doan_id: tệp tương đối trong dự án}."""
    chon = {}
    p = os.path.join(du_an, "chon.json")
    if os.path.isfile(p) and not chi_luot and dung_chon:
        with open(p, encoding="utf-8") as f:
            chon = json.load(f).get("chon", {})
    luots = [lt for lt in cac_luot(du_an) if not chi_luot or lt["luot"] == chi_luot]
    ra = {}
    for d in kb["doan"]:
        if d["id"] in chon and os.path.isfile(os.path.join(du_an, chon[d["id"]])):
            ra[d["id"]] = chon[d["id"]]
            continue
        tot = None
        for lt in luots:
            cung = next((x for x in lt["doan"] if x["id"] == d["id"] and x["docTrungTinh"] == d["docTrungTinh"]), None)
            if not cung:
                continue
            km = lt["_kiem"].get("muc", {})
            ung = [m for m in lt["muc"] if m["doan"] == d["id"]
                   and os.path.isfile(CH.tuyet_doi(m["ra"]))]
            if not ung:
                continue
            m = min(ung, key=lambda x: (km.get(x["id"], {}).get("diem", 50), x["lan"]))
            diem = km.get(m["id"], {}).get("diem", 50)
            if tot is None or diem <= tot[0]:   # bằng điểm thì lấy lượt mới hơn
                tot = (diem, os.path.relpath(CH.tuyet_doi(m["ra"]), du_an))
        if tot:
            ra[d["id"]] = tot[1]
    return ra


def cat_lang(mau):
    db = A.muc_khung(mau, SR, 10)
    b = A.bien_tieng(db)
    if not b:
        return mau[:0]
    dau = max(0, int((b[0] * 0.01 - DEM_DAU) * SR))
    cuoi = min(len(mau), int(((b[1] + 1) * 0.01 + DEM_CUOI) * SR))
    return mau[dau:cuoi]


def chia_cau(chu, toi_da=90):
    cau = [c.strip() for c in re.split(r"(?<=[.!?…])\s+", chu) if c.strip()]
    ra = []
    for c in cau:
        while len(c) > toi_da and "," in c[:toi_da]:
            i = c.rfind(",", 0, toi_da)
            ra.append(c[:i + 1].strip())
            c = c[i + 1:].strip()
        ra.append(c)
    return ra


def gio_srt(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def ghep(du_an, ban_nhap=False, chi_luot=None, ten=None, giao_phim=None, ghi_de=False, ghi_khoa=None):
    if chi_luot:   # ghép riêng một lượt (thi nghe): theo lời của chính lượt đó, có thể là một biến thể kịch bản
        with open(os.path.join(du_an, "luot", chi_luot, "luot.json"), encoding="utf-8") as f:
            lt = json.load(f)
        kb = {"thongTin": lt.get("thongTin", {}), "doan": lt["doan"]}
    else:
        kb = L.doc_kich_ban(os.path.join(du_an, "loi-doc.md"), tu_dien=CH.tu_dien())
    tt = dict(kb["thongTin"])
    tt.update(ghi_khoa or {})   # cờ dòng lệnh đè khóa đầu tệp (dùng khi thử)
    tep = chon_tep(du_an, kb, chi_luot)
    may_cua = {lt["luot"]: (lt["may"], lt.get("giong")) for lt in cac_luot(du_an)}
    thieu = [d["id"] for d in kb["doan"] if d["id"] not in tep]
    if thieu and not ban_nhap:
        sys.exit(f"Thiếu lượt đọc cho {', '.join(thieu)}: sinh thêm hoặc ghép bản nháp (--ban-nhap)")
    am = array.array("h", bytes(int(MO_DAU * SR) * 2))
    moc, cue = [], []
    nghi = float(tt.get("nghiGiuaDoan", 0.6))
    hs = _ho_so(tt)
    co_gian = _bat(tt.get("coGianNghi"))
    co_gian = min(0.3, abs(co_gian[1])) if co_gian[0] and co_gian[1] else (0.1 if co_gian[0] else 0.0)
    ngau = random.Random(zlib.crc32(os.path.basename(os.path.normpath(du_an)).encode("utf-8")))
    bat_tho, dinh_tho = _bat(tt.get("hoiTho"))
    ds_tho = nap_hoi_tho((hs.get("hoiTho") or {}).get("tep", []), dinh_tho or THO_DINH) if bat_tho else []
    if bat_tho and not ds_tho:
        print("   (hoiTho bật nhưng hồ sơ giọng chưa có hơi thở: bỏ qua)")
    tho_tu, tho_cach = int(tt.get("hoiThoTu", 25)), float(tt.get("hoiThoCach", 20))
    tho_cuoi, tho_so, ghi_tho, ghi_nghi = -1e9, 0, [], []
    dau_tien = True
    for d in kb["doan"]:
        if d["id"] not in tep:
            continue
        if not dau_tien:
            q = nghi * (1 + ngau.uniform(-co_gian, co_gian)) if co_gian else nghi
            q += d["nghiTruoc"]
            ghi_nghi.append(round(q, 2))
            t_nay = len(am) / SR
            if (ds_tho and len(d["chu"].split()) >= tho_tu and t_nay - tho_cuoi >= tho_cach):
                th = ds_tho[tho_so % len(ds_tho)]
                truoc = q - len(th) / SR - THO_SAT + DEM_DAU
                if truoc >= THO_LANG_TRUOC:
                    am.extend(array.array("h", bytes(int(truoc * SR) * 2)))
                    ghi_tho.append({"doan": d["id"], "luc": round(len(am) / SR, 2), "tho": tho_so % len(ds_tho) + 1})
                    am.extend(th)
                    con = int(q * SR) - int(truoc * SR) - len(th)
                    am.extend(array.array("h", bytes(max(0, con) * 2)))
                    tho_so += 1
                    tho_cuoi = len(am) / SR
                else:
                    am.extend(array.array("h", bytes(int(q * SR) * 2)))
            else:
                am.extend(array.array("h", bytes(int(q * SR) * 2)))
        dau_tien = False
        m = cat_lang(A.doc_pcm(os.path.join(du_an, tep[d["id"]]), SR))
        bd = len(am) / SR
        am.extend(m)
        kt = len(am) / SR
        lt_ten = tep[d["id"]].split("/")[1] if tep[d["id"]].startswith("luot/") else None
        may, giong = may_cua.get(lt_ten, (None, None))
        moc.append({"doan": d["id"], "tep": tep[d["id"]], "may": may, "giong": giong, "batDau": round(bd, 3),
                    "ketThuc": round(kt, 3), "chu": d["chu"]})
        cau = chia_cau(d["chu"])
        tong = sum(max(1, len(c.split())) for c in cau)
        t = bd + DEM_DAU
        doan_noi = (kt - DEM_CUOI) - t
        for c in cau:
            dai = doan_noi * max(1, len(c.split())) / tong
            cue.append((t, t + dai, c))
            t += dai
    am.extend(array.array("h", bytes(int(KET * SR) * 2)))
    if ten:
        ra_dir, goc_ten = os.path.join(du_an, "thi-nghe"), ten
    else:
        ra_dir = os.path.join(du_an, "thanh-pham")
        goc_ten = re.sub(r"^\d{4}-\d{2}\s+", "", os.path.basename(du_an)) + ("-ban-nhap" if ban_nhap else "")
    os.makedirs(ra_dir, exist_ok=True)
    ra = os.path.join(ra_dir, goc_ten + ".wav")
    bat_nen, muc_nen = _bat(tt.get("nenPhong"))
    nen = hs.get("nenPhong") or {}
    nen_tep = _tep_kho(nen["tep"]) if nen.get("tep") else None
    if bat_nen and not (nen_tep and os.path.isfile(nen_tep)):
        print("   (nenPhong bật nhưng hồ sơ giọng chưa có tiếng nền phòng: bỏ qua; xem tools/nen_phong.py trich)")
        bat_nen = False
    if bat_nen and muc_nen is None:
        muc_nen = float(nen.get("muc", NP.MUC_MAC_DINH))
    with tempfile.TemporaryDirectory() as tmp:
        tho = os.path.join(tmp, "tho.wav")
        A.ghi_wav(tho, am, SR)
        if bat_nen:
            chuan = os.path.join(tmp, "chuan.wav")
            A.chuan_am_luong(tho, chuan)
            NP.lot(chuan, nen_tep, ra, muc_nen, nen.get("rms"))
        else:
            A.chuan_am_luong(tho, ra)
    with open(os.path.join(ra_dir, goc_ten + ".srt"), "w", encoding="utf-8") as f:
        for i, (a, b, c) in enumerate(cue, 1):
            f.write(f"{i}\n{gio_srt(a)} --> {gio_srt(b)}\n{c}\n\n")
    with open(os.path.join(ra_dir, goc_ten + ".moc.json"), "w", encoding="utf-8") as f:
        json.dump({"thoiLuong": round(len(am) / SR, 2), "thieu": thieu,
                   "mayDoc": sorted({m["may"] for m in moc if m["may"]}),
                   "nenPhong": round(muc_nen, 1) if bat_nen else None, "coGianNghi": co_gian or None,
                   "quangNghi": ghi_nghi, "hoiTho": ghi_tho, "doan": moc}, f, ensure_ascii=False, indent=1)
    them = [f"nền phòng {muc_nen:.1f} dBFS" if bat_nen else "", f"nghỉ co giãn ±{co_gian:.0%}" if co_gian else "",
            f"{len(ghi_tho)} hơi thở" if ghi_tho else ""]
    them = ", ".join(x for x in them if x)
    print(f"   Đã ghép {os.path.relpath(ra, du_an)}: {len(am) / SR:.1f} giây, {len(moc)} đoạn"
          + (f", thiếu {', '.join(thieu)}" if thieu else "") + (f" ({them})" if them else ""))
    if str(tt.get("giong") or "").startswith("@") and not ten:
        print("   Nhắc: giọng nhân bản nghe như thật, khi đăng công khai nhớ khai báo nội dung tổng hợp "
              "(YouTube: Nội dung bị thay đổi hoặc tổng hợp = Có; Facebook, Instagram: nhãn Thông tin về AI; "
              "TikTok: Nội dung do AI tạo).")
    if giao_phim:
        giao(ra, giao_phim, ghi_de)
    return ra


def giao(tep, du_an_phim, ghi_de=False):
    xp = CH.xuong_phim()
    if not xp:
        sys.exit("Không thấy xưởng phim (thư mục mẹ có 'Du an/'). Khai cau-hinh.json > xuongPhim.")
    dich_dir = du_an_phim if os.path.isabs(du_an_phim) else os.path.join(xp, "Du an", du_an_phim)
    if not os.path.isdir(dich_dir):
        sys.exit(f"Không thấy dự án phim: {dich_dir}")
    dich = os.path.join(dich_dir, "nguon", "voice.wav")
    if os.path.exists(dich) and not ghi_de:
        sys.exit(f"Đã có {dich}; thêm --ghi-de nếu muốn thay")
    os.makedirs(os.path.dirname(dich), exist_ok=True)
    shutil.copyfile(tep, dich)
    for duoi in (".srt", ".moc.json"):
        if os.path.isfile(tep[:-4] + duoi):
            shutil.copyfile(tep[:-4] + duoi, dich[:-4] + duoi)
    with open(os.path.join(dich_dir, "nguon", "voice.nguon.json"), "w", encoding="utf-8") as f:
        json.dump({"tuXuongLongTieng": CH.tuong_doi(tep)}, f, ensure_ascii=False, indent=1)
    print("   Đã giao sang xưởng phim:", dich)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("du_an")
    ap.add_argument("--ban-nhap", action="store_true")
    ap.add_argument("--giao-phim")
    ap.add_argument("--ghi-de", action="store_true")
    ap.add_argument("--nen-phong", nargs="?", const="co", help="đè khóa nenPhong (co, khong, hoặc mức dBFS)")
    ap.add_argument("--co-gian", help="đè khóa coGianNghi (vd 0.1; 0 là tắt)")
    ap.add_argument("--hoi-tho", nargs="?", const="co", help="đè khóa hoiTho (co, khong)")
    ap.add_argument("--ten", help="tên bản thử: ghi vào thi-nghe/<tên>.wav thay vì thanh-pham/")
    a = ap.parse_args()
    import hang_doi
    khoa = {k: v for k, v in (("nenPhong", a.nen_phong), ("coGianNghi", a.co_gian), ("hoiTho", a.hoi_tho))
            if v is not None}
    ghep(hang_doi.tim_du_an(a.du_an), a.ban_nhap, ten=a.ten, giao_phim=a.giao_phim, ghi_de=a.ghi_de, ghi_khoa=khoa)


if __name__ == "__main__":
    main()
