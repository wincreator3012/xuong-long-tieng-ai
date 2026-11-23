#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐO NHỊP: độ biến thiên cao độ của lượt đọc, thước phụ để bắt giọng đều đều kiểu máy.

    python3 tools/do_nhip.py "../Du an/<dự án>" luot-03 [d003-l2 ...]   # lượt tốt (hoặc các lượt nêu tên) của một nhóm lượt
    python3 tools/do_nhip.py --tep a.wav b.wav                          # đo thẳng các tệp

In "std" (độ lệch chuẩn cao độ, bán cung), "rộng" (quãng từ phân vị 10 đến 90) và f0 trung vị. Kinh nghiệm
(bài "Làm người hay người làm", 11/2026, giọng @an vi-03): lượt tự nhiên cỡ 4,0; dưới 3,7 là đều đều đáng nghi;
đoạn dày số liệu có thể nằm quanh 3,5 dù đã sửa chỉ dẫn. Đây là thước PHỤ: loại cờ lệch lời, tốc độ, xén đỉnh
trước (kiem.json), rồi mới dùng std để chọn giữa các lượt sạch. Không thay cho tai người nghe.
Cần numpy (có trong môi trường chung của xưởng); lấy cao độ bằng tự tương quan, không cần mô hình.
"""
import argparse
import json
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import am_thanh as A  # noqa: E402

SR = 16000


def _np():
    try:
        import numpy as np
        return np
    except ImportError:
        sys.exit("Thiếu numpy: pip install numpy (hoặc chạy ở môi trường chung của xưởng).")


def doc(tep):
    np = _np()
    r = subprocess.run([A.ffmpeg(), "-v", "error", "-i", tep, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768


def f0(x):
    np = _np()
    n, h = int(0.04 * SR), int(0.01 * SR)
    lo, hi = int(SR / 400), int(SR / 70)
    ra = []
    for i in range(0, len(x) - n, h):
        f = x[i:i + n] - x[i:i + n].mean()
        if np.sqrt((f ** 2).mean()) < 0.01:
            continue
        c = np.correlate(f, f, "full")[n - 1:]
        if c[0] <= 0:
            continue
        c = c / c[0]
        k = lo + int(np.argmax(c[lo:hi]))
        if c[k] > 0.45:
            ra.append(SR / k)
    return np.array(ra)


def do(tep):
    """Trả {std, rong, f0} hoặc None nếu quá ít quãng có thanh."""
    np = _np()
    p = f0(doc(tep))
    if len(p) < 20:
        return None
    s = 12 * np.log2(p / np.median(p))
    return {"std": float(s.std()), "rong": float(np.percentile(s, 90) - np.percentile(s, 10)),
            "f0": float(np.median(p))}


def _in(ten, r, ghi_chu=""):
    print(ten, "std %.2f rộng %.2f f0 %.0f" % (r["std"], r["rong"], r["f0"]) if r else "ít tiếng", "|", ghi_chu)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("du_an", nargs="?", help="thư mục dự án")
    ap.add_argument("nhom", nargs="?", help="nhóm lượt, ví dụ luot-03")
    ap.add_argument("ma", nargs="*", help="mã lượt như d003-l2; bỏ trống thì đo lượt tốt của mọi đoạn")
    ap.add_argument("--tep", nargs="+", help="đo thẳng các tệp tiếng")
    a = ap.parse_args()
    if a.tep:
        for t in a.tep:
            _in(os.path.basename(t), do(t))
        return
    if not (a.du_an and a.nhom):
        ap.error("cần thư mục dự án và nhóm lượt, hoặc --tep")
    k = json.load(open(os.path.join(a.du_an, "luot", a.nhom, "kiem.json"), encoding="utf-8"))
    ids = a.ma or list(k["tot"].values())
    for lid in ids:
        v = k["muc"][lid]
        _in(lid, do(os.path.join(a.du_an, v["tep"])), (v.get("nghe") or "")[:48])


if __name__ == "__main__":
    main()
