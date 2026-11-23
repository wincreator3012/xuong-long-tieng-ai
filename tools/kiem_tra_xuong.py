#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Máy tự kiểm của xưởng: chạy sau mỗi lần sửa công cụ, trước khi commit. 0 lỗi mới commit.

    python3 tools/kiem_tra_xuong.py
Kiểm: mọi tệp Python biên dịch được; JSON hợp lệ; đọc số tiếng Việt; đọc kịch bản (thẻ, phát âm, ngừng, chú thích);
dịch thẻ cho từng máy đọc; mọi máy đọc trong may-doc.json có bộ nối và cách viết thẻ; các hàm lõi của luồng gỡ băng.
"""
import glob
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import loi_doc as L  # noqa: E402

loi = []


def bang(ten, that, mong):
    if that != mong:
        loi.append(f"{ten}: được {that!r}, mong {mong!r}")


for p in glob.glob(os.path.join(GOC, "**", "*.py"), recursive=True):
    try:
        compile(open(p, encoding="utf-8").read(), p, "exec")
    except SyntaxError as e:
        loi.append(f"không biên dịch được {os.path.relpath(p, GOC)}: {e}")
for p in glob.glob(os.path.join(GOC, "**", "*.json"), recursive=True):
    try:
        json.load(open(p, encoding="utf-8"))
    except ValueError as e:
        loi.append(f"JSON hỏng {os.path.relpath(p, GOC)}: {e}")

for so, chu in [("0", "không"), ("15", "mười lăm"), ("21", "hai mươi mốt"), ("24", "hai mươi tư"),
                ("105", "một trăm linh năm"), ("1005", "một nghìn không trăm linh năm"),
                ("2026", "hai nghìn không trăm hai mươi sáu"), ("1.200.000", "một triệu hai trăm nghìn"),
                ("3,5", "ba phẩy năm"), ("0909", "không chín không chín")]:
    bang("số " + so, L.so_thanh_chu(so), chu)
bang("câu có ngày giờ", L.chuan_hoa_so_vi("Ngày 19/11/2026 lúc 9:30, 85% (3-5 người)"),
     "Ngày mười chín tháng mười một năm hai nghìn không trăm hai mươi sáu lúc chín giờ ba mươi phút, "
     "tám mươi lăm phần trăm (ba đến năm người)")

KB = """---
ngonNgu: vi
phongCach: ấm áp | warm, slow
---
<!-- ghi chú
nhiều dòng -->
# Mục một

Chào bạn. {ngừng} Mình học {{AI|ây ai}} trong 3 phút. {cười nhẹ}

{ngừng 1.5}

> trìu mến | tender
Hệ giao cảm [sympathetic] giúp ta {ngừng 1.2} phản ứng.
"""
kb = L.doc_kich_ban(van_ban=KB)
bang("số đoạn", len(kb["doan"]), 2)
if len(kb["doan"]) == 2:
    d1, d2 = kb["doan"]
    bang("bản viết", d1["chu"], "Chào bạn. Mình học AI trong 3 phút.")
    bang("ngừng trước đoạn 2", d2["nghiTruoc"], 1.5)
    bang("chỉ dẫn đoạn 2", list(d2["chiDan"]), ["trìu mến", "tender"])
    bang("bỏ chú thích", d2["chu"], "Hệ giao cảm giúp ta phản ứng.")
    bang("gemini", L.cho_may(d1, "gemini", {}),
         {"text": "Chào bạn. <short pause> Mình học ây ai trong 3 phút. <laugh>", "style": "warm, slow"})
    bang("drama3", L.cho_may(d2, "drama3", {"chuanHoaSo": True})["text"],
         "[tender] Hệ giao cảm giúp ta [long pause] phản ứng.")
    bang("higgs3 số", L.cho_may(d1, "higgs3", {"chuanHoaSo": True})["text"],
         "<|prosody:speed_slow|><|emotion:affection|>Chào bạn. <|prosody:pause|> Mình học ây ai trong ba phút. "
         "<|sfx:laughter|>Hì.")
    bang("vieneu", L.cho_may(d1, "vieneu", {})["text"], "Chào bạn. Mình học ây ai trong 3 phút. [cười]")
bang("so lời", L.ty_le_loi(L.lam_sach_de_so("Mình học 3 phút."), L.lam_sach_de_so("mình học ba phút"))[0], 0.0)

kb2 = L.doc_kich_ban(van_ban="{> tò mò | curious} Có bao giờ bạn để ý? {> nhanh hơn | faster} Rồi.")
bang("chỉ dẫn giữa câu, bản viết", kb2["doan"][0]["chu"], "Có bao giờ bạn để ý? Rồi.")
bang("chỉ dẫn giữa câu, drama3", L.cho_may(kb2["doan"][0], "drama3", {})["text"], "[curious] Có bao giờ bạn để ý? [faster] Rồi.")
bang("chỉ dẫn giữa câu, gemini", L.cho_may(kb2["doan"][0], "gemini", {})["text"], "Có bao giờ bạn để ý? Rồi.")
bang("chỉ dẫn giữa câu, không cảnh báo", kb2["canhBao"], [])

g = L.lam_sach_de_so("Xin chào, đây là xưởng lồng tiếng.")
n = L.bo_nghe_ao(g, L.lam_sach_de_so("xin chào đây là sưởng lồng tiếng cảm ơn các bạn đã theo dõi"))
bang("bỏ nghe ảo, gộp x/s", L.ty_le_loi(L.gop_am_vi(g), L.gop_am_vi(n))[0], 0.0)

for p in glob.glob(os.path.join(GOC, "*.command")):
    if not os.access(p, os.X_OK):
        loi.append(f"{os.path.basename(p)} mất quyền chạy (chmod +x): Finder sẽ báo không đủ quyền")

for p in glob.glob(os.path.join(GOC, "*.bat")):
    if b"\r\n" not in open(p, "rb").read():
        loi.append(f"{os.path.basename(p)} phải xuống dòng kiểu Windows (CRLF)")

md = json.load(open(os.path.join(GOC, "may-doc.json"), encoding="utf-8"))
for k, v in md.items():
    if k.startswith("_"):
        continue
    if not os.path.isfile(os.path.join(TOOLS, "may_doc", v["boNoi"] + ".py")):
        loi.append(f"máy {k}: thiếu tools/may_doc/{v['boNoi']}.py")
    if v.get("moiTruong") not in ("mlx", "vieneu", "chung"):
        loi.append(f"máy {k}: moiTruong phải là mlx, vieneu hoặc chung")
    if not set(v.get("heDieuHanh", [])) <= {"Darwin", "Windows", "Linux"} or not v.get("heDieuHanh"):
        loi.append(f"máy {k}: heDieuHanh thiếu hoặc sai")
    for ten, cach in L.THE.items():
        if k not in cach:
            loi.append(f"thẻ {{{ten}}} chưa có cách viết cho {k}")

import cau_hinh as CH  # noqa: E402
import do_may  # noqa: E402
for k in CH.may_dung() or []:
    if k not in md:
        loi.append(f"mayDung có '{k}' nhưng may-doc.json không có")
gia = {"he": "Darwin", "kienTruc": "arm64", "chipApple": True, "chip": "thử", "ramGB": 64, "gpu": None, "diaTrongGB": 200}
bang("đề xuất Mac 64 GB", do_may.de_xuat(gia)[0], ["drama3"])
bang("đề xuất Mac 16 GB", do_may.de_xuat(dict(gia, ramGB=16))[0], ["vieneu"])
bang("đề xuất Windows", do_may.de_xuat(dict(gia, he="Windows", kienTruc="AMD64", chipApple=False))[0], ["vieneu"])
bang("Drama 3 trên Windows", do_may.danh_gia(dict(gia, he="Windows", chipApple=False), "drama3", md["drama3"])[0], "khong")
bang("môi trường chung trên Windows", CH.ten_venv("chung") if not CH.APPLE else "venv-chung", "venv-chung")

# Luồng gỡ băng: âm tiết tiếng Việt, từ nước ngoài, áp chỗ sửa, câu trả lời, phụ đề không chồng nhau
import go_bang as GB  # noqa: E402
for w, mong in [("xưởng", True), ("nghiêng", True), ("khuya", True), ("quyển", True), ("gì", True),
                ("online", False), ("deadline", False), ("team", False), ("Zoom", False)]:
    bang(f"âm tiết Việt '{w}'", GB.la_am_tiet_viet(w), mong)
bang("viết tắt là từ nước ngoài", GB.la_tieng_ngoai("KPI,"), True)
bang("chữ Việt không phải từ nước ngoài", GB.la_tieng_ngoai("ai"), False)
gb_thu = {"doan": [{"start": 0, "end": 3, "text": "", "chu": [
    {"w": " Tôi", "s": 0, "e": .3}, {"w": " học", "s": .3, "e": .6}, {"w": " sô", "s": .6, "e": .9},
    {"w": " mi,", "s": .9, "e": 1.2}, {"w": " rồi", "s": 1.2, "e": 1.5}, {"w": " về.", "s": 1.5, "e": 2}]}]}
GB.thay_noi(gb_thu, {"d": 0, "a": 2, "b": 3}, "Somi")
bang("thay chữ giữ dấu câu", "".join(c["w"] for c in gb_thu["doan"][0]["chu"]), " Tôi học Somi, rồi về.")
GB.thay_noi(gb_thu, {"d": 0, "a": 4, "b": 5}, "")
bang("xóa chữ dời dấu chấm", "".join(c["w"] for c in gb_thu["doan"][0]["chu"]), " Tôi học Somi.")
c_thu = {"id": "c001", "deXuat": ["A", "-"]}
bang("trả lời +", GB.dich_tra_loi(c_thu, "+"), {"kieu": "sua", "chu": "A"})
bang("trả lời +2 là xóa", GB.dich_tra_loi(c_thu, "+2"), {"kieu": "xoa"})
bang("trả lời ok", GB.dich_tra_loi(c_thu, "ok"), {"kieu": "giu"})
bang("trả lời chữ", GB.dich_tra_loi(c_thu, '"Lê Văn A"'), {"kieu": "sua", "chu": "Lê Văn A"})
srt = GB.cau_srt({"doan": [{"start": 0, "end": 5, "text": "Một.", "chu": []}, {"start": 4, "end": 6, "text": "Hai.", "chu": []}]})
bang("phụ đề không chồng nhau", srt[0][1] <= srt[1][0], True)
bang("mốc srt", GB.moc_srt(3725.5), "01:02:05,500")

if loi:
    print("LỖI:")
    for x in loi:
        print("  -", x)
    sys.exit(1)
print("Xưởng sạch: 0 lỗi.")
