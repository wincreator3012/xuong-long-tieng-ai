#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LỒNG NHẠC NỀN cho bản đọc đã ghép: tạo nhạc nền gốc bằng mã, rồi trộn với giọng.

    python3 tools/long_nhac.py tao "../Du an/<dự án>/nhac/nhac-nen.wav" [--so-hop-am 20]
    python3 tools/long_nhac.py tron "../Du an/<dự án>/thanh-pham/<tên>.wav" "../Du an/<dự án>/nhac/nhac-nen.wav"
        [--ra "<tên>-co-nhac"]   # tạo <ra>.wav, <ra>.mp3 (192k) và <tên>-chi-giong.mp3 (160k) cạnh bản chính

Nhạc nền `tao`: thảm hòa âm ấm (Am9, Fmaj7, Cadd9, G6 lặp), chuyển chậm, vài nốt chuông thưa, tự vẽ bằng ffmpeg
aevalsrc nên không dính bản quyền của ai; mỗi hợp âm 40 giây, nối chéo 10 giây; 20 hợp âm cho khoảng 10 phút.
Nhạc thư viện (nếu muốn thay) là của xưởng phim; xưởng này không tự chép nhạc.

Trộn `tron`: giọng lùi vào 5 giây sau nhạc; nhạc lên cao (+4 dB) ở đầu và sau câu cuối, thấp (-4 dB) lúc giọng đọc,
chuyển mượt theo đường cong cố định; nhạc nhỏ dần 9 giây cuối; cuối bài kéo thêm 14 giây cho nhạc kết. KHÔNG
dùng sidechain rồi loudnorm sau trộn: lần thử đầu nhạc vọt to, giọng chìm (xem docs/BAI-HOC.md). Tiếng giọng giữ nguyên
mức của bản chính (-16 LUFS), đỉnh trộn chạm giới hạn 0,84 (khoảng -1,5 dBFS) qua alimiter.
"""
import argparse
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import am_thanh as A  # noqa: E402

HOP_AM = [
    (110.00, 164.81, 220.00, 261.63, 329.63, 493.88),
    (87.31, 130.81, 220.00, 261.63, 329.63, 392.00),
    (65.41, 130.81, 196.00, 261.63, 329.63, 392.00),
    (98.00, 146.83, 196.00, 246.94, 293.66, 392.00),
]
D, X = 40, 10


def tao(ra, n):
    args, fc = [], ""
    for i in range(n):
        b, a, c, d, e, f = HOP_AM[i % 4]
        pad = f"0.060*sin(2*PI*{b}*t)+0.030*sin(2*PI*{b}*2*t)"
        for fr in (a, c, d, e):
            pad += f"+0.028*sin(2*PI*{fr}*t)+0.022*sin(2*PI*({fr}*1.0035)*t)+0.022*sin(2*PI*({fr}*0.9965)*t)"
        trem = f"(0.80+0.20*sin(2*PI*0.07*t+{i}))"
        bell = (f"0.050*sin(2*PI*{f}*2*t)*exp(-1.6*mod(t,9))+0.040*sin(2*PI*{e}*2*t)*exp(-1.6*mod(t+4.3,13))"
                f"+0.035*sin(2*PI*{d}*4*t)*exp(-2.0*mod(t+7.1,17))")
        args += ["-f", "lavfi", "-t", str(D), "-i", f"aevalsrc='({pad})*{trem}+{bell}':s=48000:c=mono"]
    fc = "[0:a][1:a]acrossfade=d=%d:c1=tri:c2=tri[a1]" % X
    for i in range(2, n):
        fc += f";[a{i-1}][{i}:a]acrossfade=d={X}:c1=tri:c2=tri[a{i}]"
    fc += (f";[a{n-1}]lowpass=f=2600,aecho=0.8:0.6:700|1300:0.30|0.20,stereotools=mlev=1:slev=1.3,"
           "loudnorm=I=-26:TP=-3,aformat=sample_rates=48000:channel_layouts=stereo[out]")
    os.makedirs(os.path.dirname(os.path.abspath(ra)), exist_ok=True)
    subprocess.run([A.ffmpeg(), "-y", "-v", "error", *args, "-filter_complex", fc, "-map", "[out]",
                    "-c:a", "pcm_s24le", ra], check=True)
    print("xong", ra)


def tron(giong, nhac, ra_ten):
    sec = _do_dai(giong)
    T = sec + 14                      # tổng thời lượng
    RS = 5 + sec + 1.2                # lúc nhạc bắt đầu lên lại sau câu cuối
    vol = f"pow(10,(-4+8*(clip((5-t)/2,0,1)+clip((t-{RS:.2f})/2.5,0,1)))/20)"
    fc = (f"[0:a]aformat=sample_fmts=fltp:channel_layouts=stereo,adelay=5000|5000,apad=whole_dur={T:.2f}[v];"
          f"[1:a]aformat=sample_fmts=fltp:channel_layouts=stereo,atrim=0:{T:.2f},afade=t=in:d=3,"
          f"afade=t=out:st={T-9:.2f}:d=9,volume='{vol}':eval=frame[m];"
          "[v][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.84:level=disabled[out]")
    thu = os.path.dirname(os.path.abspath(giong))
    wav, mp3 = os.path.join(thu, ra_ten + ".wav"), os.path.join(thu, ra_ten + ".mp3")
    ff = A.ffmpeg()
    subprocess.run([ff, "-y", "-v", "error", "-i", giong, "-i", nhac, "-filter_complex", fc, "-map", "[out]",
                    "-ar", "48000", "-c:a", "pcm_s24le", wav], check=True)
    subprocess.run([ff, "-y", "-v", "error", "-i", wav, "-b:a", "192k", mp3], check=True)
    chi = os.path.splitext(giong)[0] + "-chi-giong.mp3"
    subprocess.run([ff, "-y", "-v", "error", "-i", giong, "-b:a", "160k", chi], check=True)
    for t in (wav, mp3, chi):
        print(os.path.basename(t), "%.1f s" % _do_dai(t))
    print("Kiểm lại (LUFS): giọng", A.do_lufs(giong), "| bản trộn", A.do_lufs(wav))


def _do_dai(tep):
    r = subprocess.run([A.ffmpeg(), "-hide_banner", "-i", tep], capture_output=True, text=True)
    for dong in r.stderr.splitlines():
        if "Duration:" in dong:
            h, m, s = dong.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    sys.exit("Không đọc được thời lượng: " + tep)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="lenh", required=True)
    a1 = sp.add_parser("tao")
    a1.add_argument("ra")
    a1.add_argument("--so-hop-am", type=int, default=20)
    a2 = sp.add_parser("tron")
    a2.add_argument("giong")
    a2.add_argument("nhac")
    a2.add_argument("--ra", default=None)
    a = ap.parse_args()
    if a.lenh == "tao":
        tao(a.ra, max(2, a.so_hop_am))
    else:
        ra = a.ra or os.path.splitext(os.path.basename(a.giong))[0] + "-co-nhac"
        tron(a.giong, a.nhac, ra)


if __name__ == "__main__":
    main()
