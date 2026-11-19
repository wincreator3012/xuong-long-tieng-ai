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
