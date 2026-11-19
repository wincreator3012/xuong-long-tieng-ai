# -*- coding: utf-8 -*-
"""Bộ nối ElevenLabs Eleven v4 qua REST; chỉ dùng thư viện chuẩn. Khóa API ở biến XLT_KHOA_ELEVENLABS.

Giọng: voice_id có sẵn trong thư viện ElevenLabs, hoặc voice_id giọng riêng đã nhân bản (tools/giong_rieng.py).
Thẻ diễn xuất nằm ngay trong lời ([warmly], [whispers]). language_code giúp máy đọc đúng giọng bản ngữ.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung  # noqa: E402

API = "https://api.elevenlabs.io/v1"
DS = None


def sinh(m, _dt, ra):
    khoa = os.environ.get("XLT_KHOA_ELEVENLABS")
    if not khoa:
        raise RuntimeError("chưa có khóa ElevenLabs: chạy tệp 'Them khoa API' của xưởng")
    giong = m.get("giong") or (m.get("mau") or {}).get("elevenlabs")
    if not giong:
        raise RuntimeError("giọng riêng chưa nhân bản trên ElevenLabs (tools/giong_rieng.py dang-ky --may elevenlabs)")
    dinh_dang = DS.get("dinhDang") or "mp3_44100_192"
    than = {"text": m["text"], "model_id": DS["moHinh"], "language_code": m.get("ngonNgu", "vi"),
            "seed": int(m.get("hatGiong", 1)), "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
    for i in range(4):
        rq = urllib.request.Request(f"{API}/text-to-speech/{giong}?output_format={dinh_dang}",
                                    data=json.dumps(than).encode(), method="POST",
                                    headers={"xi-api-key": khoa, "Content-Type": "application/json",
                                             "Accept": "audio/mpeg"})
        try:
            with urllib.request.urlopen(rq, timeout=300) as r:
                du_lieu = r.read()
            break
        except urllib.error.HTTPError as e:
            nd = e.read().decode("utf-8", "replace")[:800]
            if e.code in (429, 500, 502, 503) and i < 3:
                time.sleep(5 * (i + 1))
                continue
            if "output_format" in nd and dinh_dang != "mp3_44100_128":  # gói chưa cho định dạng cao: lùi về
                dinh_dang = "mp3_44100_128"
                continue
            raise RuntimeError(f"ElevenLabs báo lỗi {e.code}: {nd}")
    tho = ra + ".el.mp3"
    with open(tho, "wb") as f:
        f.write(du_lieu)
    chung.doi_sang_wav(tho, ra)
    os.remove(tho)


if __name__ == "__main__":
    DS = chung.doc_danh_sach()
    sys.exit(chung.chay(DS, sinh))
