# -*- coding: utf-8 -*-
"""Gỡ băng (môi trường venv-mlx): Whisper large-v3-turbo chạy bằng MLX, trên Mac chip Apple.

    python go_bang_may.py <danh-sach.json>
    danh-sach: {"may": "whisper", "moHinh": "...", "muc": [{"id", "vao": "<tệp tiếng hoặc phim>", "ngonNgu": "vi",
                "ra": "<.gb.json>", "chiTiet": false, "goiY": "<tên riêng, thuật ngữ>", "nghe": "<.nghe.m4a>"}]}
Hai chế độ:
- Gỡ băng ngược để kiểm (mặc định): nhanh, chỉ cần lời.
- chiTiet: gỡ băng một bản ghi để làm transcript: mốc và độ chắc từng chữ, chỉ số từng câu (để máy rà chỗ nghi),
  gợi ý từ vựng cho cửa sổ đầu, và tệp nghe m4a nhẹ cho Bàn soát.
Mỗi tệp ra: {"text", "doan": [{"start", "end", "text", "chu": [{"w", "s", "e", "p"}], "logprob", "nen", "lang"}],
             "thoiLuong", "moHinh", "luc"}.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung  # noqa: E402

DS = None


def nap():
    from mlx_audio.stt import load
    return load(DS["moHinh"])


def go(m, model, ra):
    if not m.get("chiTiet"):
        kq = model.generate(m["vao"], language=m.get("ngonNgu", "vi"), condition_on_previous_text=False,
                            word_timestamps=False)
        doan = [{"start": round(float(s.get("start", 0)), 2), "end": round(float(s.get("end", 0)), 2),
                 "text": s.get("text", "").strip()} for s in (kq.segments or [])]
        with open(ra, "w", encoding="utf-8") as f:
            json.dump({"text": kq.text.strip(), "doan": doan}, f, ensure_ascii=False, indent=1)
        return
    am = chung.doc_16k(m["vao"])          # đọc được cả phim: ffmpeg lấy tiếng ra
    tl = len(am) / 16000
    print(f"    {os.path.basename(m['vao'])}: {tl / 60:.1f} phút tiếng, đang gỡ băng...", flush=True)
    t = time.time()
    kq = model.generate(am, language=m.get("ngonNgu", "vi"), condition_on_previous_text=False,
                        word_timestamps=True, initial_prompt=m.get("goiY") or None,
                        hallucination_silence_threshold=2.0)
    doan = [chung.doan_chi_tiet(s) for s in (kq.segments or [])]
    with open(ra, "w", encoding="utf-8") as f:
        json.dump({"text": " ".join(d["text"] for d in doan).strip(), "doan": doan, "thoiLuong": round(tl, 2),
                   "moHinh": DS["moHinh"], "giay": round(time.time() - t, 1), "luc": time.strftime("%Y-%m-%d %H:%M:%S")},
                  f, ensure_ascii=False, indent=1)
    if m.get("nghe"):
        chung.tao_tep_nghe(m["vao"], m["nghe"])


if __name__ == "__main__":
    DS = chung.doc_danh_sach()
    sys.exit(chung.chay(DS, go, nap))
