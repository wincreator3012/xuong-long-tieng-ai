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
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import am_thanh as A  # noqa: E402
import cau_hinh as CH  # noqa: E402
import loi_doc as L  # noqa: E402

SR = 48000
DEM_DAU, DEM_CUOI, MO_DAU, KET = 0.06, 0.15, 0.3, 0.6


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


def ghep(du_an, ban_nhap=False, chi_luot=None, ten=None, giao_phim=None, ghi_de=False):
    import array
    if chi_luot:   # ghép riêng một lượt (thi nghe): theo lời của chính lượt đó, có thể là một biến thể kịch bản
        with open(os.path.join(du_an, "luot", chi_luot, "luot.json"), encoding="utf-8") as f:
            lt = json.load(f)
        kb = {"thongTin": lt.get("thongTin", {}), "doan": lt["doan"]}
    else:
        kb = L.doc_kich_ban(os.path.join(du_an, "loi-doc.md"), tu_dien=CH.tu_dien())
    tt = kb["thongTin"]
    tep = chon_tep(du_an, kb, chi_luot)
    may_cua = {lt["luot"]: (lt["may"], lt.get("giong")) for lt in cac_luot(du_an)}
    thieu = [d["id"] for d in kb["doan"] if d["id"] not in tep]
    if thieu and not ban_nhap:
        sys.exit(f"Thiếu lượt đọc cho {', '.join(thieu)}: sinh thêm hoặc ghép bản nháp (--ban-nhap)")
    am = array.array("h", bytes(int(MO_DAU * SR) * 2))
    moc, cue = [], []
    nghi = float(tt.get("nghiGiuaDoan", 0.6))
    dau_tien = True
    for d in kb["doan"]:
        if d["id"] not in tep:
            continue
        if not dau_tien:
            am.extend(array.array("h", bytes(int((nghi + d["nghiTruoc"]) * SR) * 2)))
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
    with tempfile.TemporaryDirectory() as tmp:
        tho = os.path.join(tmp, "tho.wav")
        A.ghi_wav(tho, am, SR)
        A.chuan_am_luong(tho, ra)
    with open(os.path.join(ra_dir, goc_ten + ".srt"), "w", encoding="utf-8") as f:
        for i, (a, b, c) in enumerate(cue, 1):
            f.write(f"{i}\n{gio_srt(a)} --> {gio_srt(b)}\n{c}\n\n")
    with open(os.path.join(ra_dir, goc_ten + ".moc.json"), "w", encoding="utf-8") as f:
        json.dump({"thoiLuong": round(len(am) / SR, 2), "thieu": thieu,
                   "mayDoc": sorted({m["may"] for m in moc if m["may"]}), "doan": moc}, f, ensure_ascii=False, indent=1)
    print(f"   Đã ghép {os.path.relpath(ra, du_an)}: {len(am) / SR:.1f} giây, {len(moc)} đoạn"
          + (f", thiếu {', '.join(thieu)}" if thieu else ""))
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
    a = ap.parse_args()
    import hang_doi
    ghep(hang_doi.tim_du_an(a.du_an), a.ban_nhap, giao_phim=a.giao_phim, ghi_de=a.ghi_de)


if __name__ == "__main__":
    main()
