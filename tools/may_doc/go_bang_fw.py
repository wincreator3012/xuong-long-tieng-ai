# -*- coding: utf-8 -*-
"""Gỡ băng ngược để kiểm trên máy không phải Mac chip Apple (môi trường venv-chung): faster-whisper large-v3-turbo.
Có GPU NVIDIA (CUDA) thì chạy trên GPU, không thì CPU với int8.

    python go_bang_fw.py <danh-sach.json>      (cùng định dạng với go_bang_may.py)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung  # noqa: E402

DS = None


def nap():
    from faster_whisper import WhisperModel
    try:
        import ctranslate2
        gpu = ctranslate2.get_cuda_device_count() > 0
    except Exception:
        gpu = False
    if gpu:
        try:
            return WhisperModel(DS["moHinh"], device="cuda", compute_type="float16")
        except Exception as e:  # thiếu thư viện CUDA: lùi về CPU
            print("GPU không dùng được, chạy CPU:", str(e)[:200], flush=True)
    return WhisperModel(DS["moHinh"], device="cpu", compute_type="int8")


def doc_16k(tep):
    """Giải mã bằng ffmpeg của xưởng ra mảng float32 16 kHz (tránh lệ thuộc phiên bản PyAV của faster-whisper)."""
    import subprocess
    import numpy as np
    r = subprocess.run([chung.ffmpeg(), "-v", "error", "-i", tep, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def go(m, model, ra):
    seg, _ = model.transcribe(doc_16k(m["vao"]), language=m.get("ngonNgu", "vi"), condition_on_previous_text=False,
                              beam_size=5, vad_filter=False)
    doan = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in seg]
    with open(ra, "w", encoding="utf-8") as f:
        json.dump({"text": " ".join(d["text"] for d in doan).strip(), "doan": doan}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    DS = chung.doc_danh_sach()
    sys.exit(chung.chay(DS, go, nap))
