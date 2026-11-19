# -*- coding: utf-8 -*-
"""Bộ nối Gemini 3.8 Flash TTS qua REST (/v1beta/interactions); chỉ dùng thư viện chuẩn.

Khóa API lấy từ biến XLT_KHOA_GEMINI (hàng đợi đọc từ kho khóa của máy, xem tools/khoa.py). Giọng: tên giọng có sẵn (Charon, Kore...)
hoặc mã giọng riêng 'voice_...' đã đăng ký bằng tools/giong-rieng.py. Tiếng trả về: WAV 24 kHz.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chung  # noqa: E402

API = "https://generativelanguage.googleapis.com/v1beta"
DS = None


def goi(duong, than=None, phuong_thuc="POST", lan=4):
    khoa = os.environ.get("XLT_KHOA_GEMINI")
    if not khoa:
        raise RuntimeError("chưa có khóa Gemini: chạy tệp 'Them khoa API' của xưởng")
    du_lieu = json.dumps(than).encode() if than is not None else None
    for i in range(lan):
        rq = urllib.request.Request(API + duong, data=du_lieu, method=phuong_thuc,
                                    headers={"x-goog-api-key": khoa, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(rq, timeout=300) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            noi_dung = e.read().decode("utf-8", "replace")[:800]
            if e.code in (429, 500, 502, 503, 504) and i < lan - 1:
                time.sleep(5 * (i + 1))
                continue
            raise RuntimeError(f"Gemini báo lỗi {e.code}: {noi_dung}")


def sinh(m, _dt, ra):
    giong = m.get("giong") or (m.get("mau") or {}).get("gemini")
    if not giong:
        raise RuntimeError("giọng riêng chưa đăng ký với Gemini (tools/giong-rieng.py dang-ky --may gemini)")
    noi_dung = {"type": "text", "text": m["text"]}
    if m.get("style"):
        noi_dung["annotations"] = [{"type": "speech_metadata", "style": m["style"]}]
    than = {"model": DS["moHinh"], "input": [{"type": "user_input", "content": [noi_dung]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": giong}]}}
    kq = goi("/interactions", than)
    am = [c for s in kq.get("steps", []) if s.get("type") == "model_output"
          for c in s.get("content", []) if c.get("type") == "audio" and c.get("data")]
    if not am:
        raise RuntimeError("Gemini không trả tiếng: " + json.dumps(kq, ensure_ascii=False)[:600])
    tho = ra + ".gemini.wav"
    with open(tho, "wb") as f:
        f.write(base64.b64decode(am[-1]["data"]))
    chung.doi_sang_wav(tho, ra)
    os.remove(tho)


if __name__ == "__main__":
    DS = chung.doc_danh_sach()
    sys.exit(chung.chay(DS, sinh))
