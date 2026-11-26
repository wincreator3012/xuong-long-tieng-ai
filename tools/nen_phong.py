#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NỀN PHÒNG: tiếng nền phòng [room tone] lót dưới bản chỉ giọng, thay cho quãng lặng số tuyệt đối.

    python3 tools/nen_phong.py trich <bản thu gốc> <ra.wav> [--dai 12]   # trích nền phòng từ các quãng lặng của bản thu thật
    python3 tools/nen_phong.py do <tệp.wav>                              # đo mức (dBFS RMS), quãng 0 tuyệt đối, độ ồn nền
    python3 tools/nen_phong.py lot <giọng.wav> <nền.wav> <ra.wav> --muc -66

Vì sao: máy đọc sinh tiếng trong môi trường số nên chỗ ngừng rơi về 0 tuyệt đối, và khâu ghép còn chèn thêm quãng 0
giữa các đoạn. Nghe bằng tai nghe, chỗ đó như âm thanh bị cắt mất. Ngành phim lấp bằng tiếng nền của chính căn
phòng thu. Nền lấy từ phòng thu thật của chủ giọng (bản thu mẫu), lặp liền mạch, đặt ở mức ồn nền thật của phòng
sau khi chuẩn âm lượng, nên tai không nghe ra mà quãng nghỉ không còn "chân không".
"""
import argparse
import array
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import am_thanh as A  # noqa: E402

SR = 48000
MUC_MAC_DINH = -66.0   # dBFS RMS của nền sau chuẩn âm lượng, khi hồ sơ giọng không ghi mức đo thật


def _doc_float(tep):
    m = A.doc_pcm(tep, SR)
    return array.array("f", (x / 32768.0 for x in m))


def _ghi_float(tep, mau):
    """Ghi float mono ra WAV 48 kHz 24-bit qua ffmpeg (giữ được mức rất nhỏ, không làm tròn về 16-bit)."""
    with tempfile.TemporaryDirectory() as tmp:
        tho = os.path.join(tmp, "tho.f32")
        b = array.array("f", mau)
        if sys.byteorder == "big":
            b.byteswap()
        with open(tho, "wb") as f:
            f.write(b.tobytes())
        subprocess.run([A.ffmpeg(), "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", tho,
                        "-c:a", "pcm_s24le", tep], check=True)


def rms_db(mau):
    if not mau:
        return -120.0
    t = sum(x * x for x in mau) / len(mau)
    return 10 * math.log10(t) if t > 0 else -120.0


def trich(goc, ra, dai=12.0, toi_thieu=0.6, tran_db=-68.0, mep=0.05, xfade=0.04):
    """Ghép các quãng lặng thật (không có số 0, dưới tran_db, dài từ toi_thieu giây) thành một vòng lặp liền mạch."""
    m = _doc_float(goc)
    fr = SR // 100
    db = []
    for i in range(0, len(m) - fr + 1, fr):
        k = m[i:i + fr]
        db.append(-120.0 if not any(k) else rms_db(k))
    quang, s = [], None
    for i, x in enumerate(db + [0.0]):
        if -95.0 < x < tran_db:
            if s is None:
                s = i
        else:
            if s is not None and (i - s) / 100 >= toi_thieu:
                quang.append((s, i))
            s = None
    if not quang:
        sys.exit("Không thấy quãng lặng nào đủ dài trong bản thu: thu riêng 60 giây phòng trống rồi trích lại.")
    n_x = int(xfade * SR)
    ra_m = array.array("f")
    for s, e in quang:
        k = m[s * fr + int(mep * SR): e * fr - int(mep * SR)]
        if len(k) < 3 * n_x:
            continue
        if not ra_m:
            ra_m.extend(k)
        else:
            for j in range(n_x):   # nối kiểu cùng công suất
                g = j / n_x
                ra_m[-n_x + j] = ra_m[-n_x + j] * math.cos(g * math.pi / 2) + k[j] * math.sin(g * math.pi / 2)
            ra_m.extend(k[n_x:])
        if len(ra_m) >= dai * SR + n_x:
            break
    # khép vòng: phần cuối hòa vào phần đầu, để lặp không có mối nối
    for j in range(n_x):
        g = j / n_x
        ra_m[j] = ra_m[-n_x + j] * math.cos(g * math.pi / 2) + ra_m[j] * math.sin(g * math.pi / 2)
    del ra_m[-n_x:]
    _ghi_float(ra, ra_m)
    tt = {"tep": ra, "thoiLuong": round(len(ra_m) / SR, 2), "soQuang": len(quang), "rms": round(rms_db(ra_m), 1)}
    # mức ồn nền thật của phòng sau khi bản thu được chuẩn âm lượng như thành phẩm
    lufs = A.do_lufs(goc)
    if lufs is not None:
        tt["lufsBanThu"] = round(lufs, 1)
        tt["mucSauChuan"] = round(tt["rms"] + (A.MUC_LUFS - lufs), 1)
    print(json.dumps(tt, ensure_ascii=False, indent=1))
    return tt


def do(tep):
    m = A.doc_pcm(tep, SR)
    khong = chay = tong = 0
    for x in m:
        if x == 0:
            khong += 1
        else:
            if khong >= SR * 0.05:
                chay += 1
                tong += khong
            khong = 0
    if khong >= SR * 0.05:
        chay += 1
        tong += khong
    db = sorted(x for x in A.muc_khung(m, SR, 10) if x > -119)
    tt = {"thoiLuong": round(len(m) / SR, 1), "quang0": chay, "giay0": round(tong / SR, 1),
          "tiLe0": round(100 * m.count(0) / max(1, len(m)), 1),
          "nenP5": round(db[len(db) // 20], 1) if db else None, "lufs": A.do_lufs(tep)}
    print(json.dumps(tt, ensure_ascii=False))
    return tt


def lot(giong, nen, ra, muc=MUC_MAC_DINH, nen_rms=None):
    """Trộn nền phòng (lặp suốt bài) dưới bản giọng; mức nền là RMS đích tính bằng dBFS. Bản ra 48 kHz 24-bit."""
    if nen_rms is None:
        nen_rms = rms_db(_doc_float(nen))
    gain = muc - nen_rms
    loc = (f"[1:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=mono,volume={gain:.2f}dB,"
           f"afade=t=in:d=0.08[n];[0:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=mono[g];"
           f"[g][n]amerge=inputs=2,pan=mono|c0=c0+c1[r]")
    with tempfile.TemporaryDirectory() as tmp:
        tam = os.path.join(tmp, "lot.wav")
        subprocess.run([A.ffmpeg(), "-v", "error", "-y", "-i", giong, "-stream_loop", "-1", "-i", nen,
                        "-filter_complex", loc, "-map", "[r]", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s24le",
                        tam], check=True)
        shutil.copyfile(tam, ra)
    return ra


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="lenh", required=True)
    t = sp.add_parser("trich")
    t.add_argument("goc")
    t.add_argument("ra")
    t.add_argument("--dai", type=float, default=12.0)
    d = sp.add_parser("do")
    d.add_argument("tep")
    lo = sp.add_parser("lot")
    lo.add_argument("giong")
    lo.add_argument("nen")
    lo.add_argument("ra")
    lo.add_argument("--muc", type=float, default=MUC_MAC_DINH)
    a = ap.parse_args()
    if a.lenh == "trich":
        trich(a.goc, a.ra, a.dai)
    elif a.lenh == "do":
        do(a.tep)
    else:
        lot(a.giong, a.nen, a.ra, a.muc)


if __name__ == "__main__":
    main()
