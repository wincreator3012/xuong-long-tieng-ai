# -*- coding: utf-8 -*-
"""Âm thanh bằng thư viện chuẩn và ffmpeg (chạy được ở cả máy ảo lẫn máy thật, không cần numpy).

    doc_pcm(tep, tan_so)        mẫu s16 mono (array 'h')
    muc_khung(mau, tan_so, ms)  dBFS từng khung
    ghi_wav(tep, mau, tan_so)
    chuan_am_luong(vao, ra)     loudnorm hai lượt về -16 LUFS, đỉnh thật -1.5 dBTP, WAV 48 kHz 24-bit
"""
import array
import json
import math
import os
import re
import shutil
import subprocess
import sys
import wave

MUC_LUFS = -16.0
DINH_THAT = -1.5


def ffmpeg():
    p = os.environ.get("XLT_FFMPEG") or shutil.which("ffmpeg")
    if p and os.path.isfile(p):
        return p
    try:
        import cau_hinh
        p = cau_hinh.ffmpeg_moi_truong()
    except Exception:
        p = None
    for p in (p, "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        if p and os.path.isfile(p):
            return p
    sys.exit("Không tìm thấy ffmpeg: chạy trình cài đặt của xưởng trên máy này trước.")


def doc_pcm(tep, tan_so=16000):
    r = subprocess.run([ffmpeg(), "-v", "error", "-i", tep, "-ac", "1", "-ar", str(tan_so), "-f", "s16le", "-"],
                       capture_output=True, check=True)
    a = array.array("h")
    a.frombytes(r.stdout)
    if sys.byteorder == "big":
        a.byteswap()
    return a


def muc_khung(mau, tan_so, ms=20):
    n = max(1, int(tan_so * ms / 1000))
    ra = []
    for i in range(0, len(mau) - n + 1, n):
        k = mau[i:i + n]
        tb = sum(x * x for x in k) / n
        ra.append(10 * math.log10(tb / (32768.0 ** 2)) if tb > 0 else -120.0)
    return ra


def dinh_db(mau):
    m = max((abs(x) for x in mau), default=0)
    return 20 * math.log10(m / 32768.0) if m else -120.0


def ghi_wav(tep, mau, tan_so):
    os.makedirs(os.path.dirname(os.path.abspath(tep)), exist_ok=True)
    with wave.open(tep, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(tan_so)
        b = array.array("h", mau)
        if sys.byteorder == "big":
            b.byteswap()
        w.writeframes(b.tobytes())


def bien_tieng(db, nguong=None):
    """(khung đầu, khung cuối) có tiếng nói; ngưỡng mặc định: 40 dB dưới khung to nhất, không thấp hơn -55 dBFS."""
    if not db:
        return None
    if nguong is None:
        nguong = max(-55.0, max(db) - 40.0)
    co = [i for i, x in enumerate(db) if x > nguong]
    return (co[0], co[-1]) if co else None


def chuan_am_luong(vao, ra, muc=MUC_LUFS, dinh=DINH_THAT):
    loc = f"loudnorm=I={muc}:TP={dinh}:LRA=11"
    r = subprocess.run([ffmpeg(), "-hide_banner", "-nostats", "-i", vao, "-af", loc + ":print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if m:
        d = json.loads(m.group(0))
        loc += (f":measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
                f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true")
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", vao, "-af", loc, "-ar", "48000", "-ac", "1",
                    "-c:a", "pcm_s24le", ra], check=True)


def do_lufs(tep):
    r = subprocess.run([ffmpeg(), "-hide_banner", "-nostats", "-i", tep, "-af", "loudnorm=print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    return float(json.loads(m.group(0))["input_i"]) if m else None
