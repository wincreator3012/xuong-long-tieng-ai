#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tạo hồ sơ dự án lồng tiếng: "Du an/<YYYY-MM tên>/loi-doc.md" theo khuôn.

    python3 tools/du_an_moi.py "Gioi thieu khoa hoc" [--ngon-ngu en] [--may gemini] [--giong @an] [--so-luot 2]
Tên thư mục không dấu (như xưởng phim) để đường dẫn chạy ổn ở mọi máy; tiêu đề tiếng Việt ghi trong loi-doc.md.
"""
import argparse
import datetime as dt
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import cau_hinh as CH  # noqa: E402

KHUON = """---
tieuDe: {tieu_de}
ngonNgu: {nn}
may: {may}
giong: {giong}
soLuot: {so_luot}
phongCach: {phong_cach}
nghiGiuaDoan: 0.6
---

<!-- Mỗi đoạn văn (cách nhau bằng một dòng trống) là một đoạn đọc. Thẻ trong lời: {{ngừng}}, {{ngừng dài}}, {{cười}},
{{cười nhẹ}}, {{thở dài}}, {{hít thở}}, {{hắng giọng}}. Dòng riêng {{ngừng 1.5}}: thêm 1,5 giây lặng.
Dòng "> chỉ dẫn | directions": cách đọc cho đoạn ngay dưới. {{{{chữ|cách đọc}}}}: đặt cách đọc riêng.
Tiêu đề "# ...": không đọc, chèn quãng lặng dài hơn. Không dùng ngoặc vuông trong lời đọc. -->

"""

# Khuôn đã chốt sau thi nghe 19/11/2026: tiếng Việt nhịp mạnh (kèm chỉ dẫn giữa câu), tiếng Anh ấm và chậm (không chỉ dẫn giữa câu).
PHONG_CACH = {"vi": "sôi nổi mà điềm tĩnh, nhịp biến hóa | lively yet grounded, dynamic pacing, like an engaging teacher",
              "en": "ấm, chậm, gần gũi | warm, unhurried, intimate"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ten")
    ap.add_argument("--tieu-de")
    ap.add_argument("--ngon-ngu", default="vi")
    ap.add_argument("--may", help="mặc định: máy đọc đầu tiên trong cau-hinh.json > mayDung")
    ap.add_argument("--giong")
    ap.add_argument("--so-luot", type=int, default=2)
    ap.add_argument("--phong-cach", help="mặc định theo khuôn đã chốt của từng thứ tiếng (19/11/2026)")
    a = ap.parse_args()
    a.phong_cach = a.phong_cach or PHONG_CACH.get(a.ngon_ngu, PHONG_CACH["vi"])
    a.may = a.may or (CH.may_dung() or ["drama3"])[0]
    cfg = CH.may_doc()[a.may]
    giong = a.giong
    if not giong:
        md = cfg.get("giongMacDinh")
        giong = (md.get(a.ngon_ngu) if isinstance(md, dict) else md) or CH.giong_rieng()
    if cfg.get("canGiongMau") and not (giong or "").startswith("@"):
        giong = CH.giong_rieng()
    if not giong:
        sys.exit(f"{cfg['ten']} cần giọng: thêm --giong (giọng có sẵn hoặc @<hồ sơ giọng riêng>)")
    d = os.path.join(CH.du_an(), f"{dt.date.today():%Y-%m} {a.ten}")
    if os.path.exists(d):
        sys.exit(f"Đã có {d}")
    os.makedirs(d)
    with open(os.path.join(d, "loi-doc.md"), "w", encoding="utf-8") as f:
        f.write(KHUON.format(tieu_de=a.tieu_de or a.ten, nn=a.ngon_ngu, may=a.may, giong=giong,
                             so_luot=a.so_luot, phong_cach=a.phong_cach))
    print(d)


if __name__ == "__main__":
    main()
