#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DỰNG XƯỞNG từ bản thiết kế: cá nhân hoá xưởng lồng tiếng vừa chép về máy người dùng (chạy một lần, chạy lại an toàn).

    python3 tools/dung_xuong.py --ten-xuong "<tên>" --tien-to <2-6 chữ> --ban-mau <mã commit>
    python3 tools/dung_xuong.py --kiem        # tạo lại thư mục cạnh xưởng nếu thiếu, in trạng thái dựng xưởng

Việc làm:
  - bỏ các khối chỉ dành cho bản thiết kế (<!-- BAN-MAU --> ... <!-- /BAN-MAU -->) trong tệp .md;
  - tạo cau-hinh.json (từ cau-hinh.mau.json) với tiền tố skill "tienToSkill";
  - tạo cạnh xưởng: "Du an/" (hồ sơ dự án), "Kho giong/" (hồ sơ giọng riêng, từ điển phát âm đã duyệt);
  - viết README.md của xưởng (ghi công bản thiết kế, giấy phép MIT), cấp quyền chạy cho tệp .command;
  - ghi bản thiết kế đã dùng (repo, commit, ngày) vào tools/.dung-xuong.json.
Máy đọc, hồ sơ giọng chọn sau, ở skill long-tieng-thiet-lap.
"""
import argparse
import json
import os
import re
import sys
import time

TOOLS = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import cau_hinh as CH  # noqa: E402
import kho_tu_lieu  # noqa: E402

REPO_BAN_MAU = "https://github.com/wincreator3012/xuong-long-tieng-ai"
SO = os.path.join(TOOLS, ".dung-xuong.json")


def doc_so():
    try:
        with open(SO, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def bo_khoi_ban_mau():
    so = 0
    for dp, dn, fn in os.walk(GOC):
        dn[:] = [d for d in dn if d not in (".git", "__pycache__")]
        for f in fn:
            if not f.endswith(".md"):
                continue
            p = os.path.join(dp, f)
            goc = open(p, encoding="utf-8").read()
            moi = re.sub(r"[ \t]*<!-- BAN-MAU -->.*?<!-- /BAN-MAU -->[ \t]*\n*", "", goc, flags=re.S)
            if moi != goc:
                with open(p, "w", encoding="utf-8") as g:
                    g.write(moi)
                so += 1
    return so


def thu_muc_canh():
    for d in (CH.du_an(), CH.tam()):
        os.makedirs(d, exist_ok=True)
    kho = kho_tu_lieu.tim() or kho_tu_lieu.tao()
    return kho


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ten-xuong")
    ap.add_argument("--tien-to")
    ap.add_argument("--ban-mau", default="main")
    ap.add_argument("--kiem", action="store_true")
    a = ap.parse_args()
    so = doc_so()
    if a.kiem:
        kho = thu_muc_canh()
        print(f"Xưởng: {GOC}")
        print(f"Bản thiết kế: {so.get('banMau') or 'chưa dựng (chạy --ten-xuong ... --tien-to ...)'}")
        print(f"Dự án: {CH.du_an()}\nKho giọng: {kho}")
        print(f"Máy đọc đang bật: {CH.may_dung() or 'chưa chọn (trình cài đặt sẽ đề xuất theo máy)'}")
        print(f"Giọng riêng mặc định: {CH.giong_rieng() or 'chưa có'}")
        return 0
    ten = (a.ten_xuong or os.path.basename(GOC)).strip()
    tt = (a.tien_to or "").strip().lower()
    if not re.match(r"^[a-z0-9]{2,6}$", tt):
        sys.exit("! --tien-to cần 2-6 chữ thường hoặc số, không dấu (vd chữ cái đầu họ tên: tma)")
    print(f"Dựng xưởng từ bản thiết kế: {GOC}")
    print(f"  bỏ khối chỉ dành cho bản thiết kế ở {bo_khoi_ban_mau()} tệp")
    p = os.path.join(GOC, "cau-hinh.json")
    cfg = {}
    for nguon in (p, os.path.join(GOC, "cau-hinh.mau.json")):
        if os.path.isfile(nguon):
            with open(nguon, encoding="utf-8") as f:
                cfg = json.load(f)
            break
    cfg["tienToSkill"] = tt
    with open(p, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"  cau-hinh.json: tiền tố skill '{tt}' (skill trong tài khoản sẽ tên {tt}-long-tieng, {tt}-long-tieng-thiet-lap)")
    kho = thu_muc_canh()
    print(f"  dự án: {CH.du_an()}\n  kho giọng: {kho}")
    readme = os.path.join(GOC, "README.md")
    if not os.path.isfile(readme):
        with open(readme, "w", encoding="utf-8") as f:
            f.write(f"# {ten}\n\nXưởng lồng tiếng cùng AI của riêng tôi. AI đọc `CLAUDE.md` ở đầu mỗi phiên; cách dùng ở "
                    f"`HUONG-DAN.md`.\n\nDựng từ bản thiết kế [xuong-long-tieng-ai]({REPO_BAN_MAU}) của Lương Dũng Nhân "
                    f"(commit {a.ban_mau}, ngày {time.strftime('%Y-%m-%d')}), giấy phép MIT (xem `LICENSE`). "
                    "Xưởng này không phải bản clone: không push, không pull về repo bản thiết kế. Muốn học thêm từ bản "
                    "mới, nói với AI \"xem bản thiết kế có gì mới\".\n")
        print("  README.md của xưởng (ghi công bản thiết kế)")
    for f in os.listdir(GOC):
        if f.endswith(".command"):
            os.chmod(os.path.join(GOC, f), 0o755)
    so.update(banMau={"repo": REPO_BAN_MAU, "commit": a.ban_mau, "ngay": time.strftime("%Y-%m-%d")}, tenXuong=ten,
              tienTo=tt)
    with open(SO, "w", encoding="utf-8") as f:
        json.dump(so, f, ensure_ascii=False, indent=1)
    print("\nĐã cá nhân hoá. Bước kế tiếp: skill long-tieng-thiet-lap (chọn máy đọc, cài trên máy thật, giọng riêng).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
