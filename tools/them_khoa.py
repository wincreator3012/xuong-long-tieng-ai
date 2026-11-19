#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LƯU VÀ THỬ KHÓA API cho máy đọc đám mây (gọi từ tệp "Them khoa API" của xưởng, chạy trên máy thật).

    python tools/them_khoa.py              # lần lượt hỏi khóa Gemini, ElevenLabs; để trống để giữ khóa cũ hoặc bỏ qua
    python tools/them_khoa.py --thu        # chỉ thử các khóa đã lưu
Khóa gõ vào không hiện trên màn hình, được lưu vào kho khóa của hệ điều hành (xem tools/khoa.py), không vào tệp nào.
"""
import getpass
import os
import sys
import urllib.error
import urllib.request

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import khoa  # noqa: E402

DICH_VU = [
    ("gemini", "Gemini (Google AI Studio)", "https://aistudio.google.com/apikey",
     "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts", "x-goog-api-key"),
    ("elevenlabs", "ElevenLabs", "https://elevenlabs.io/app/settings/api-keys",
     "https://api.elevenlabs.io/v1/models", "xi-api-key"),
]


def thu(ten, url, dau):
    k = khoa.lay(ten)
    if not k:
        print(f"   Chưa có khóa {ten}: máy đọc này tạm chưa dùng được.")
        return False
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={dau: k}), timeout=30) as r:
            print(f"   Khóa {ten} dùng được (mã {r.status}).")
            return True
    except urllib.error.HTTPError as e:
        print(f"   Khóa {ten} chưa dùng được: lỗi {e.code} {e.read().decode('utf-8', 'replace')[:200]}")
    except Exception as e:
        print(f"   Không thử được khóa {ten}: {e}")
    return False


def main():
    chi_thu = "--thu" in sys.argv
    for ten, nhan, noi_lay, url, dau in DICH_VU:
        print(f"\n== {nhan}")
        if not chi_thu:
            print(f"   Lấy khóa ở: {noi_lay}")
            if khoa.lay(ten):
                print(f"   (đã có khóa {ten}; dán khóa mới để thay, để trống để giữ)")
            gt = getpass.getpass("   Dán khóa rồi Enter (khóa không hiện ra màn hình): ").strip()
            if gt:
                if khoa.luu(ten, gt):
                    print("   Đã lưu vào kho khóa của máy.")
                else:
                    print("   Không lưu được: máy thiếu kho khóa (trên Windows, chạy lại trình cài đặt của xưởng).")
                    continue
        thu(ten, url, dau)


if __name__ == "__main__":
    main()
