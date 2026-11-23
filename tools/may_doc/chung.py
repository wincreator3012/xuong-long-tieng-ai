# -*- coding: utf-8 -*-
"""Khung chung cho bộ nối máy đọc. Mỗi bộ nối chạy trong môi trường Python riêng của nó trên máy thật (Mac hoặc Windows):

    <python của môi trường> tools/may_doc/<bo_noi>.py <danh-sach.json>

danh-sach.json (do tools/hang_doi.py chay tạo ra):
    {"may": "drama3", "moHinh": "...", "ghiDe": false,
     "muc": [{"id": "d001-l1", "text": "...", "style": null, "giong": "Charon" | null,
              "mau": {"tep": "<đường dẫn tuyệt đối>", "loi": "lời của mẫu", "ten": "an-vi"} | null,
              "ngonNgu": "vi", "hatGiong": 1, "ra": "<đường dẫn .wav tuyệt đối>"}]}

Mỗi mục xong in một dòng '@@{json}' (id, ok, giay, loi) để hàng đợi ghi lại; mục đã có tệp ra thì bỏ qua.
Chỉ dùng thư viện chuẩn ở đây, để bộ nối nào cũng nạp được.
"""
import json
import os
import sys
import time
import traceback


def doc_danh_sach():
    if len(sys.argv) < 2:
        sys.exit("thiếu đường dẫn danh-sach.json")
    with open(sys.argv[1], encoding="utf-8") as f:
        return json.load(f)


def bao(**kw):
    print("@@" + json.dumps(kw, ensure_ascii=False), flush=True)


def chay(ds, ham, nap=None):
    """nap(): nạp mô hình một lần (trả về đối tượng dùng chung); ham(muc, doi_tuong): sinh tiếng cho một mục."""
    can = [m for m in ds["muc"] if ds.get("ghiDe") or not os.path.isfile(m["ra"])]
    for m in ds["muc"]:
        if m not in can:
            bao(id=m["id"], ok=True, boQua=True)
    if not can:
        return 0
    t = time.time()
    try:
        dt = nap() if nap else None
    except Exception as e:  # nạp mô hình hỏng: mọi mục đều lỗi
        traceback.print_exc()
        for m in can:
            bao(id=m["id"], ok=False, loi=f"nạp mô hình không được: {e}"[:600])
        return 1
    print(f"Đã nạp {ds['may']} sau {time.time() - t:.1f} giây", flush=True)
    loi = 0
    for i, m in enumerate(can, 1):
        t = time.time()
        os.makedirs(os.path.dirname(m["ra"]), exist_ok=True)
        tam = m["ra"] + ".dang-ghi.wav"
        try:
            ham(m, dt, tam)
            os.replace(tam, m["ra"])
            bao(id=m["id"], ok=True, giay=round(time.time() - t, 2))
            print(f"  [{i}/{len(can)}] {m['id']} xong ({time.time() - t:.1f} giây)", flush=True)
        except Exception as e:
            traceback.print_exc()
            loi += 1
            if os.path.exists(tam):
                os.remove(tam)
            bao(id=m["id"], ok=False, loi=str(e)[:600])
    return 1 if loi else 0


def ffmpeg():
    """ffmpeg của môi trường xưởng (tải kèm imageio-ffmpeg; hàng đợi truyền qua XLT_FFMPEG), rồi của hệ thống."""
    import shutil
    for p in (os.environ.get("XLT_FFMPEG"), shutil.which("ffmpeg"), "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        if p and os.path.isfile(p):
            return p
    return "ffmpeg"


def doi_sang_wav(nguon, dich, tan_so=48000):
    import subprocess
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", nguon, "-ac", "1", "-ar", str(tan_so), dich], check=True)


def doc_16k(tep):
    """Giải mã tệp tiếng hoặc phim bằng ffmpeg của xưởng ra mảng float32 mono 16 kHz (đầu vào của Whisper)."""
    import subprocess
    import numpy as np
    r = subprocess.run([ffmpeg(), "-v", "error", "-i", tep, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def doan_chi_tiet(s):
    """Một câu Whisper (dạng dict) -> câu của transcript chi tiết: lời, mốc, chữ kèm độ chắc, chỉ số để rà nghe ảo."""
    def so(x, n=3):
        try:
            return round(float(x), n)
        except (TypeError, ValueError):
            return None
    chu = [{"w": w.get("word", ""), "s": so(w.get("start"), 2), "e": so(w.get("end"), 2), "p": so(w.get("probability"))}
           for w in (s.get("words") or [])]
    return {"start": so(s.get("start"), 2), "end": so(s.get("end"), 2), "text": (s.get("text") or "").strip(),
            "chu": chu, "logprob": so(s.get("avg_logprob")), "nen": so(s.get("compression_ratio")),
            "imLang": so(s.get("no_speech_prob"))}


def tao_tep_nghe(nguon, dich):
    """Tệp nghe nhẹ (m4a mono 64 kbps) để Bàn soát phát đúng quãng có chữ nghi; có rồi thì thôi."""
    import subprocess
    if os.path.isfile(dich):
        return
    tam = dich + ".dang-ghi.m4a"
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", nguon, "-vn", "-ac", "1", "-c:a", "aac", "-b:a", "64k", tam],
                   check=True)
    os.replace(tam, dich)
