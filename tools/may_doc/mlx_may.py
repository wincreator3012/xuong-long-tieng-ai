# -*- coding: utf-8 -*-
"""Bộ nối các mô hình chạy bằng MLX trên Apple Silicon (môi trường venv-mlx): Fish Audio Drama 3, Higgs Audio v3.

Drama 3 nhận thẻ diễn xuất viết tự do ngay trong lời ([whispers]); giọng riêng cần mẫu kèm lời của mẫu.
Higgs v3 nhận thẻ cố định <|emotion:...|>, <|prosody:...|>; mẫu giọng cũng cần lời của mẫu.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung  # noqa: E402

DS = None


def nap():
    from mlx_audio.tts.utils import load_model
    return load_model(model_path=DS["moHinh"])


def sinh(m, model, ra):
    import mlx.core as mx
    import numpy as np
    from mlx_audio.audio_io import write
    mx.random.seed(int(m.get("hatGiong", 1)))
    kw = {"text": m["text"]}
    if m.get("mau"):
        kw.update(ref_audio=m["mau"]["tep"], ref_text=m["mau"]["loi"])
    if DS["may"] == "higgs3":
        kw.update(temperature=1.0, max_new_tokens=2048, seed=int(m.get("hatGiong", 1)))
    phan = [np.array(r.audio, dtype=np.float32) for r in model.generate(**kw)]
    phan = [p for p in phan if p.size]
    if not phan:
        raise RuntimeError("máy đọc trả về tiếng rỗng")
    write(ra, np.concatenate(phan), model.sample_rate, format="wav")
    dinh = getattr(mx, "get_peak_memory", None) or getattr(getattr(mx, "metal", None), "get_peak_memory", None)
    if dinh:  # đo để biết máy bao nhiêu RAM thì chạy được (bảng cấu hình trong may-doc.json)
        print(f"  bộ nhớ đỉnh {dinh() / 1e9:.1f} GB", flush=True)
    mx.clear_cache()


if __name__ == "__main__":
    DS = chung.doc_danh_sach()
    sys.exit(chung.chay(DS, sinh, nap))
