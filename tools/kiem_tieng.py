#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KIỂM TIẾNG: chấm từng lượt đọc của một lần sinh, để bạn chỉ phải nghe những gì đáng nghe.

    python3 tools/kiem_tieng.py "../Du an/<dự án>" [--luot luot-01]   # mặc định: mọi lượt chưa kiểm

Đo cho mỗi lượt đọc:
  - lệch lời: so bản gỡ băng ngược (Whisper) với lời đọc, tính tỷ lệ âm tiết sai; lấy mức thấp hơn khi so với
    bản viết và bản đọc (để từ đã thay phát âm, như "ây ai" cho AI, không bị tính là sai);
  - tốc độ (âm tiết mỗi giây), lặng đầu, lặng cuối, quãng lặng dài giữa câu, đỉnh, số mẫu bị xén;
  - điểm tổng (càng thấp càng tốt) để tự chọn lượt tốt nhất mỗi đoạn.
Kết quả: luot/<lượt>/kiem.json; in bảng ngắn. Gỡ băng ngược là máy nghe nên vẫn có thể nghe sai:
cờ "lệch lời" nghĩa là cần nghe lại, chưa chắc là máy đọc sai.
"""
import argparse
import datetime as dt
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import am_thanh as A  # noqa: E402
import cau_hinh as CH  # noqa: E402
import loi_doc as L  # noqa: E402

TOC_DO = {"vi": (3.0, 7.0), "en": (1.8, 3.8)}   # âm tiết (tiếng Việt) hoặc từ (tiếng Anh) mỗi giây


def kiem_mot(wav, gb, doan, nn):
    ra = {}
    mau = A.doc_pcm(wav, 16000)
    sr = 16000
    db = A.muc_khung(mau, sr, 20)
    ra["thoiLuong"] = round(len(mau) / sr, 2)
    ra["dinh"] = round(A.dinh_db(mau), 1)
    ra["xen"] = sum(1 for x in mau if abs(x) >= 32700)
    b = A.bien_tieng(db)
    co = []
    if not b:
        return {**ra, "co": ["không có tiếng"], "diem": 999}
    ra["langDau"] = round(b[0] * 0.02, 2)
    ra["langCuoi"] = round((len(db) - 1 - b[1]) * 0.02, 2)
    nguong = max(-55.0, max(db) - 40.0)
    chuoi, dai = 0, 0
    for x in db[b[0]:b[1] + 1]:
        chuoi = chuoi + 1 if x <= nguong else 0
        dai = max(dai, chuoi)
    ra["langGiuaDaiNhat"] = round(dai * 0.02, 2)
    noi = (b[1] - b[0] + 1) * 0.02
    so_tieng = len(L.lam_sach_de_so(doan["docTrungTinh"], nn).split())
    ra["tocDo"] = round(so_tieng / max(noi, 0.1), 2)
    diem = 0.0
    if gb and os.path.isfile(gb):
        with open(gb, encoding="utf-8") as f:
            nghe = L.lam_sach_de_so(json.load(f).get("text", ""), nn)
        g1, g2 = L.lam_sach_de_so(doan["docTrungTinh"], nn), L.lam_sach_de_so(doan["chu"], nn)
        nghe = L.bo_nghe_ao(g1 + " " + g2, nghe)
        if nn == "vi":   # so trên bản đã gộp âm; danh sách chỗ lệch vẫn chỉ ra chữ gốc
            g1, g2, nghe_so = L.gop_am_vi(g1), L.gop_am_vi(g2), L.gop_am_vi(nghe)
        else:
            nghe_so = nghe
        ty1, lech1 = L.ty_le_loi(g1, nghe_so)
        ty2, lech2 = L.ty_le_loi(g2, nghe_so)
        ty, lech = (ty1, lech1) if ty1 <= ty2 else (ty2, lech2)
        ra["lechLoi"] = round(ty, 3)
        ra["choLech"] = [" ".join(x for x in (k, a or "", "->", b_ or "") if x) for k, a, b_ in lech[:12]]
        ra["nghe"] = nghe
        diem += ty * 100
        if ty > 0.3:
            co.append("lệch lời nhiều")
        elif ty > 0.12:
            co.append("lệch lời")
    else:
        co.append("chưa gỡ băng ngược")
        diem += 20
    lo, hi = TOC_DO.get(nn, (2, 7))
    if ra["tocDo"] < lo:
        co.append("chậm bất thường")
        diem += 3
    elif ra["tocDo"] > hi:
        co.append("nhanh bất thường")
        diem += 3
    if ra["xen"] > 5:
        co.append("bị xén đỉnh")
        diem += 5
    if ra["langGiuaDaiNhat"] > 1.6:
        co.append("lặng giữa câu quá dài")
        diem += 3
    if ra["langDau"] > 1.0 or ra["langCuoi"] > 1.5:
        diem += 1
    ra["co"] = co
    ra["diem"] = round(diem, 2)
    return ra


def kiem_luot(du_an, luot, in_bang=False):
    th = os.path.join(du_an, "luot", luot)
    with open(os.path.join(th, "luot.json"), encoding="utf-8") as f:
        lt = json.load(f)
    nn = lt["ngonNgu"]
    doan = {d["id"]: d for d in lt["doan"]}
    kq, tot = {}, {}
    for m in lt["muc"]:
        wav = CH.tuyet_doi(m["ra"])
        if not os.path.isfile(wav):
            kq[m["id"]] = {"co": ["chưa có tệp"], "diem": 999}
            continue
        kq[m["id"]] = kiem_mot(wav, wav[:-4] + ".gb.json", doan[m["doan"]], nn)
        kq[m["id"]]["tep"] = os.path.relpath(wav, du_an)
    for m in lt["muc"]:
        cu = tot.get(m["doan"])
        if kq[m["id"]]["diem"] < 999 and (cu is None or kq[m["id"]]["diem"] < kq[cu]["diem"]):
            tot[m["doan"]] = m["id"]
    out = {"taoLuc": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "luot": luot, "may": lt["may"],
           "giong": lt.get("giong"), "muc": kq, "tot": tot}
    with open(os.path.join(th, "kiem.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    if in_bang:
        print(f"\n   Kiểm {os.path.basename(du_an)} / {luot} ({lt['may']}, {lt.get('giong')}):")
        for mid, k in kq.items():
            dau = "*" if mid in tot.values() else " "
            print(f"   {dau} {mid:10} lệch {k.get('lechLoi', '-')!s:6} tốc độ {k.get('tocDo', '-')!s:5} "
                  f"{k.get('thoiLuong', '-')!s:6}s  {', '.join(k.get('co', []))}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("du_an")
    ap.add_argument("--luot")
    a = ap.parse_args()
    import hang_doi
    du_an = hang_doi.tim_du_an(a.du_an)
    luots = [a.luot] if a.luot else sorted(x for x in os.listdir(os.path.join(du_an, "luot"))
                                           if os.path.isfile(os.path.join(du_an, "luot", x, "luot.json")))
    for lt in luots:
        kiem_luot(du_an, lt, in_bang=True)


if __name__ == "__main__":
    main()
