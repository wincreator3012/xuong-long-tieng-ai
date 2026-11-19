# -*- coding: utf-8 -*-
"""Gỡ băng ngược để kiểm (môi trường venv-mlx): Whisper large-v3-turbo chạy bằng MLX.

    python go_bang_may.py <danh-sach.json>
    danh-sach: {"may": "whisper", "moHinh": "...", "muc": [{"id", "vao": "<wav>", "ngonNgu": "vi", "ra": "<.gb.json>"}]}
Mỗi tệp ra: {"text": "...", "doan": [{"start", "end", "text"}]}.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung  # noqa: E402

DS = None


def nap():
    from mlx_audio.stt import load
    return load(DS["moHinh"])


def go(m, model, ra):
    kq = model.generate(m["vao"], language=m.get("ngonNgu", "vi"), condition_on_previous_text=False,
                        word_timestamps=False)
    doan = [{"start": round(float(s.get("start", 0)), 2), "end": round(float(s.get("end", 0)), 2),
             "text": s.get("text", "").strip()} for s in (kq.segments or [])]
    with open(ra, "w", encoding="utf-8") as f:
        json.dump({"text": kq.text.strip(), "doan": doan}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    DS = chung.doc_danh_sach()
    sys.exit(chung.chay(DS, go, nap))
