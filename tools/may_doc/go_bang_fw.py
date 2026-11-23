# -*- coding: utf-8 -*-
"""Gỡ băng trên máy không phải Mac chip Apple (môi trường venv-chung): faster-whisper large-v3-turbo.
Có GPU NVIDIA (CUDA) thì chạy trên GPU, không thì CPU với int8.

    python go_bang_fw.py <danh-sach.json>      (cùng định dạng và hai chế độ với go_bang_may.py)
"""
import json
import os
import sys
import time

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


def go(m, model, ra):
    # Giải mã bằng ffmpeg của xưởng (tránh lệ thuộc phiên bản PyAV của faster-whisper)
    am = chung.doc_16k(m["vao"])
    if not m.get("chiTiet"):
        seg, _ = model.transcribe(am, language=m.get("ngonNgu", "vi"), condition_on_previous_text=False,
                                  beam_size=5, vad_filter=False)
        doan = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in seg]
        with open(ra, "w", encoding="utf-8") as f:
            json.dump({"text": " ".join(d["text"] for d in doan).strip(), "doan": doan}, f, ensure_ascii=False, indent=1)
        return
    tl = len(am) / 16000
    print(f"    {os.path.basename(m['vao'])}: {tl / 60:.1f} phút tiếng, đang gỡ băng...", flush=True)
    t = time.time()
    seg, _ = model.transcribe(am, language=m.get("ngonNgu", "vi"), condition_on_previous_text=False, beam_size=5,
                              vad_filter=False, word_timestamps=True, hotwords=m.get("goiY") or None,
                              hallucination_silence_threshold=2.0)   # hotwords nhắc lại ở mọi cửa sổ 30 giây
    doan = []
    for s in seg:
        doan.append(chung.doan_chi_tiet({
            "start": s.start, "end": s.end, "text": s.text, "avg_logprob": s.avg_logprob,
            "no_speech_prob": s.no_speech_prob, "compression_ratio": s.compression_ratio,
            "words": [{"word": w.word, "start": w.start, "end": w.end, "probability": w.probability}
                      for w in (s.words or [])]}))
    with open(ra, "w", encoding="utf-8") as f:
        json.dump({"text": " ".join(d["text"] for d in doan).strip(), "doan": doan, "thoiLuong": round(tl, 2),
                   "moHinh": DS["moHinh"], "giay": round(time.time() - t, 1), "luc": time.strftime("%Y-%m-%d %H:%M:%S")},
                  f, ensure_ascii=False, indent=1)
    if m.get("nghe"):
        chung.tao_tep_nghe(m["vao"], m["nghe"])


if __name__ == "__main__":
    DS = chung.doc_danh_sach()
    sys.exit(chung.chay(DS, go, nap))
