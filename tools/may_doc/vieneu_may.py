# -*- coding: utf-8 -*-
"""Bộ nối VieNeu-TTS v3 Turbo (chạy tại máy, môi trường venv-vieneu). Đường ONNX trên CPU nhanh hơn PyTorch trên Apple Silicon."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung  # noqa: E402


def nap():
    from vieneu import Vieneu
    return {"tts": Vieneu(mode="v3turbo", backend="onnx"), "giong": {}}


def sinh(m, dt, ra):
    import soundfile as sf
    tts = dt["tts"]
    if m.get("mau"):
        ten = "rieng-" + m["mau"].get("ten", "mau")
        if dt["giong"].get(ten) != m["mau"]["tep"]:
            tts.add_voice(ten, m["mau"]["tep"], denoise=True)
            dt["giong"][ten] = m["mau"]["tep"]
        giong = ten
    else:
        giong = m.get("giong")
    wav = tts.infer(m["text"], voice=giong, temperature=0.8)
    if wav is None or len(wav) == 0:
        raise RuntimeError("máy đọc trả về tiếng rỗng")
    sf.write(ra, wav, tts.sample_rate, subtype="PCM_16")


if __name__ == "__main__":
    sys.exit(chung.chay(chung.doc_danh_sach(), sinh, nap))
