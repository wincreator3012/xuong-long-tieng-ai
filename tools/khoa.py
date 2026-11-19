# -*- coding: utf-8 -*-
"""KHÓA API của máy đọc đám mây (Gemini, ElevenLabs): chỉ nằm trong kho khóa của hệ điều hành, không bao giờ trong tệp.

    Mac      Keychain (lệnh security, dịch vụ "xuong-long-tieng", tài khoản = tên khóa)
    Windows  Windows Credential Manager qua thư viện keyring (cài sẵn trong môi trường venv-chung)
    Linux    keyring (Secret Service) nếu có; không thì chỉ đọc biến môi trường

    import khoa
    khoa.lay("gemini")          # giá trị khóa hoặc None; biến môi trường XLT_KHOA_GEMINI được ưu tiên
    khoa.luu("gemini", "...")   # True nếu lưu được
    python3 tools/khoa.py co gemini     # in "có" hoặc "chưa", không bao giờ in khóa
"""
import os
import platform
import subprocess
import sys

DICH_VU = "xuong-long-tieng"
HE = platform.system()


def _keyring():
    try:
        import keyring  # noqa: F401
        return keyring
    except Exception:
        return None


def lay(ten):
    v = os.environ.get("XLT_KHOA_" + ten.upper())
    if v:
        return v
    if HE == "Darwin":
        r = subprocess.run(["security", "find-generic-password", "-s", DICH_VU, "-a", ten, "-w"],
                           capture_output=True, text=True)
        return r.stdout.strip() or None
    kr = _keyring()
    if kr:
        try:
            return kr.get_password(DICH_VU, ten) or None
        except Exception:
            return None
    return None


def luu(ten, gia_tri):
    if HE == "Darwin":
        r = subprocess.run(["security", "add-generic-password", "-U", "-s", DICH_VU, "-a", ten, "-w", gia_tri],
                           capture_output=True, text=True)
        return r.returncode == 0
    kr = _keyring()
    if not kr:
        return False
    try:
        kr.set_password(DICH_VU, ten, gia_tri)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "co":
        print("có" if lay(sys.argv[2]) else "chưa")
    else:
        sys.exit(__doc__)
