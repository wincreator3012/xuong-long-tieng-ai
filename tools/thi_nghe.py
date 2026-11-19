#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THI NGHE MÙ: cùng một kịch bản, nhiều máy đọc và giọng; bạn nghe theo chữ cái A, B, C... mà không biết máy nào,
chấm 4 tiêu chí (tự nhiên, biểu cảm đúng ý, phát âm đúng, giống giọng của bạn khi là giọng riêng), rồi mới lộ tên.

    python3 tools/thi_nghe.py tao "../Du an/<dự án>" --ung-vien "vieneu:Thiện Minh" "gemini:Charon" "drama3:@an" ...
    python3 tools/thi_nghe.py them "../Du an/<dự án>" --ung-vien "elevenlabs:@an"   # thêm ứng viên vào lượt thi cũ
    python3 tools/thi_nghe.py ket-qua "../Du an/<dự án>"
    # so nhiều cách viết lời đọc trên cùng máy, cùng giọng: "<máy>:<giọng>:<biến thể>" đọc tệp kich-ban-<biến thể>.md
    python3 tools/thi_nghe.py tao "../Du an/<dự án>" --ung-vien "drama3:@an:goc" "drama3:@an:nhip"

Mỗi ứng viên là một lượt tên "thi-<máy>-<giọng>", một lượt đọc mỗi đoạn; hàng đợi tự ghép thành thi-nghe/<lượt>.wav.
Bàn nghe (Mo ban nghe.command, thẻ "Thi nghe mù") phát theo chữ cái; điểm lưu ở thi-nghe/ket-qua.json.
"""
import argparse
import datetime as dt
import json
import os
import random
import string
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import hang_doi as H  # noqa: E402

TIEU_CHI = [
    {"id": "tuNhien", "ten": "Tự nhiên", "goi": "nghe như người thật đang nói, không máy móc"},
    {"id": "bieuCam", "ten": "Biểu cảm đúng ý", "goi": "cảm xúc, nhịp, nhấn đúng tinh thần đoạn văn"},
    {"id": "phatAm", "ten": "Phát âm đúng", "goi": "đúng dấu, đúng từ, đọc tên riêng và tiếng Anh ổn"},
    {"id": "giongAnh", "ten": "Giống giọng của bạn", "goi": "chỉ chấm khi nghe ra là giọng của bạn; bỏ trống nếu không"},
]


def p_thi(du_an):
    return os.path.join(du_an, "thi-nghe.json")


def them(du_an, ung_vien, moi=False):
    du_an = H.tim_du_an(du_an)
    thi = H.doc_json(p_thi(du_an), None)
    if moi or not thi:
        thi = {"taoLuc": H.bay_gio(), "tieuChi": TIEU_CHI, "ungVien": []}
    da = {u["nhan"] for u in thi["ungVien"]}
    con = [c for c in string.ascii_uppercase[:len(da) + len(ung_vien)] if c not in da]
    random.shuffle(con)
    for uv in ung_vien:
        may, giong, bien_the = (uv.split(":") + [None, None])[:3]
        giong = giong or None
        luot = f"thi-{may}-{H.slug(giong or 'mac-dinh')}" + (f"-{H.slug(bien_the)}" if bien_the else "")
        kb = f"kich-ban-{bien_the}.md" if bien_the else "loi-doc.md"
        H.them(du_an, may=may, giong=giong, so_luot=1, ten_luot=luot, tu_ghep=True, loai="thi-nghe", kich_ban=kb)
        thi["ungVien"].append({"nhan": con.pop(), "luot": luot, "may": may, "giong": giong, "bienThe": bien_the})
    thi["ungVien"].sort(key=lambda u: u["nhan"])
    H.ghi_json(p_thi(du_an), thi)
    print(f"Lượt thi có {len(thi['ungVien'])} ứng viên: " + ", ".join(u["nhan"] for u in thi["ungVien"]))


def ket_qua(du_an):
    du_an = H.tim_du_an(du_an)
    thi = H.doc_json(p_thi(du_an))
    kq = H.doc_json(os.path.join(du_an, "thi-nghe", "ket-qua.json"), {}) or {}
    diem = kq.get("diem", {})
    hang = []
    for u in thi["ungVien"]:
        d = diem.get(u["nhan"], {})
        so = [d[t["id"]] for t in TIEU_CHI if isinstance(d.get(t["id"]), (int, float)) and d[t["id"]] > 0]
        hang.append((sum(so) / len(so) if so else 0, u, d))
    hang.sort(key=lambda x: -x[0])
    for tb, u, d in hang:
        chi = "  ".join(f"{t['ten']} {d.get(t['id'], '-')}" for t in TIEU_CHI)
        print(f"{u['nhan']}  {tb:.2f}  {u['may']:10} {u['giong'] or '':14} {u.get('bienThe') or '':10} {chi}  {d.get('ghiChu', '')}")
    return hang


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="lenh", required=True)
    for ten in ("tao", "them"):
        a = sp.add_parser(ten)
        a.add_argument("du_an")
        a.add_argument("--ung-vien", nargs="+", required=True)
    a = sp.add_parser("ket-qua")
    a.add_argument("du_an")
    a = ap.parse_args()
    if a.lenh in ("tao", "them"):
        them(a.du_an, a.ung_vien, moi=a.lenh == "tao")
    else:
        ket_qua(a.du_an)


if __name__ == "__main__":
    main()
