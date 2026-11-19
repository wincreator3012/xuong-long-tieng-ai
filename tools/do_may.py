#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐO MÁY và ĐỀ XUẤT MÁY ĐỌC hợp cấu hình. Chạy trên máy thật (trình cài đặt gọi), không chạy trong máy ảo:
máy ảo của Cowork chỉ có vài GB bộ nhớ, đo ở đó sẽ ra sai.

    python tools/do_may.py              # in cấu hình và đề xuất
    python tools/do_may.py --json       # in JSON (trình cài ghi vào Du an/_tam/may-tinh.json cho AI đọc)

Đề xuất dựa trên may-doc.json (heDieuHanh, ramToiThieuGB, boNhoGB, dungLuongGB) và kết quả thi nghe thật:
  - Mac chip Apple, RAM từ ramToiThieuGB của Drama 3 trở lên: Drama 3 với giọng riêng (biểu cảm nhất, cần mẫu giọng).
  - Máy khác (Mac ít RAM, Mac chip Intel, Windows, Linux): VieNeu chạy tại máy (giọng có sẵn tiếng Việt, biểu cảm
    yếu), thêm Gemini hoặc ElevenLabs nếu có khóa API (biểu cảm tốt, tốn phí, cần mạng).
"""
import json
import os
import platform
import shutil
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import cau_hinh as CH  # noqa: E402


def _chay(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def ram_gb():
    he = platform.system()
    if he == "Darwin":
        v = _chay(["sysctl", "-n", "hw.memsize"])
        return round(int(v) / 2 ** 30) if v.isdigit() else None
    if he == "Windows":
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return round(m.ullTotalPhys / 2 ** 30)
    try:
        with open("/proc/meminfo") as f:
            for dong in f:
                if dong.startswith("MemTotal:"):
                    return round(int(dong.split()[1]) / 2 ** 20)
    except OSError:
        pass
    return None


def chip():
    he = platform.system()
    if he == "Darwin":
        return _chay(["sysctl", "-n", "machdep.cpu.brand_string"]) or platform.machine()
    if he == "Windows":
        return platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "")
    try:
        with open("/proc/cpuinfo") as f:
            for dong in f:
                if dong.startswith("model name"):
                    return dong.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.machine()


def gpu_nvidia():
    if not shutil.which("nvidia-smi"):
        return None
    v = _chay(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"])
    if not v:
        return None
    ten, _, mb = v.splitlines()[0].rpartition(",")
    try:
        return {"ten": ten.strip(), "vramGB": round(int(mb) / 1024)}
    except ValueError:
        return {"ten": v.splitlines()[0]}


def do():
    he = platform.system()
    mt = CH.moi_truong()
    goc_dia = mt if os.path.isdir(mt) else os.path.expanduser("~")
    return {
        "he": he, "phienBan": platform.release(), "kienTruc": platform.machine(), "chipApple": CH.APPLE,
        "chip": chip(), "ramGB": ram_gb(), "gpu": gpu_nvidia(),
        "diaTrongGB": round(shutil.disk_usage(goc_dia).free / 1e9), "may": platform.node(),
    }


def danh_gia(m, ten, cfg):
    """('khuyen' | 'duoc' | 'khong', lý do) cho một máy đọc trên máy này."""
    if m["he"] not in cfg.get("heDieuHanh", ["Darwin", "Windows", "Linux"]):
        return "khong", "không chạy trên hệ điều hành này"
    if cfg.get("moiTruong") == "mlx" and not m["chipApple"]:
        return "khong", "cần Mac chip Apple (M1 trở lên)"
    ram, can = m.get("ramGB") or 0, cfg.get("ramToiThieuGB") or 0
    if can and ram < can:
        if ram >= (cfg.get("boNhoGB") or 0) + 4:
            return "duoc", f"RAM {ram} GB, nên có {can} GB: chạy được nếu đóng bớt ứng dụng, có thể chậm"
        return "khong", f"RAM {ram} GB không đủ (máy đọc chiếm khoảng {cfg.get('boNhoGB')} GB)"
    if cfg.get("dungLuongGB") and m["diaTrongGB"] < cfg["dungLuongGB"] + 10:
        return "duoc", f"ổ đĩa còn {m['diaTrongGB']} GB, mô hình cần {cfg['dungLuongGB']:g} GB: dọn ổ trước"
    if cfg.get("loai") == "dam-may":
        return "duoc", "cần khóa API và mạng, tính phí theo lượng chữ"
    if ten == "higgs3":
        return "duoc", "chạy được nhưng thi nghe mù chỉ 1,5/5; giấy phép chỉ cho video, podcast có ghi công"
    if ten == "vieneu":
        return "duoc", "chạy được mọi máy; giọng có sẵn tiếng Việt, biểu cảm yếu (thi nghe 1,25/5)"
    return "khuyen", "chạy tốt trên máy này"


def de_xuat(m=None):
    """Danh sách máy đọc nên bật và bảng đánh giá từng máy."""
    m = m or do()
    bang = {k: danh_gia(m, k, v) for k, v in CH.may_doc().items()}
    if bang.get("drama3", ("",))[0] == "khuyen":
        chon = ["drama3"]
    else:
        chon = ["vieneu"] if bang.get("vieneu", ("khong",))[0] != "khong" else []
    return chon, bang


def in_bao_cao(m, chon, bang):
    print(f"Máy: {m['chip']} ({m['he']} {m['kienTruc']}), RAM {m['ramGB']} GB, ổ đĩa còn {m['diaTrongGB']} GB"
          + (f", GPU {m['gpu'].get('ten')} {m['gpu'].get('vramGB', '?')} GB" if m.get("gpu") else ""))
    nhan = {"khuyen": "nên dùng", "duoc": "dùng được", "khong": "không dùng được"}
    md = CH.may_doc()
    for k, (muc, ly_do) in bang.items():
        print(f"  {md[k]['ten']:32} {nhan[muc]:16} {ly_do}")
    print("Đề xuất bật:", ", ".join(chon) or "(không máy đọc tại máy nào chạy được; dùng Gemini hoặc ElevenLabs)")


if __name__ == "__main__":
    m = do()
    chon, bang = de_xuat(m)
    if "--json" in sys.argv:
        print(json.dumps({"may": m, "deXuat": chon, "danhGia": {k: list(v) for k, v in bang.items()}},
                         ensure_ascii=False, indent=1))
    else:
        in_bao_cao(m, chon, bang)
