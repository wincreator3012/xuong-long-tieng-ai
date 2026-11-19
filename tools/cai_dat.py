#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CÀI ĐẶT XƯỞNG trên máy thật (Mac hoặc Windows): đo máy, chọn máy đọc, dựng môi trường Python, tải mô hình,
gỡ những gì không còn dùng, rồi tự kiểm. Bấm lại bao nhiêu lần cũng được: bước đã xong thì bỏ qua.

Chạy qua tệp bấm đúp của xưởng ("Cai dat tren Mac.command", "Cai dat tren Windows.bat"); tệp đó cài uv rồi gọi:
    uv run --no-project --python 3.12 tools/cai_dat.py [--xem]
--xem: chỉ đo máy và in kế hoạch, không cài, không gỡ gì.

Máy đọc nào được bật: cau-hinh.json > mayDung. Chưa có thì trình cài đo máy, chọn theo tools/do_may.py rồi ghi vào.
Môi trường (ngoài repo, xem tools/cau_hinh.py): venv-mlx (Mac chip Apple: MLX, gỡ băng), venv-vieneu (VieNeu),
venv-chung (máy khác: hàng đợi, Bàn nghe, máy đọc đám mây, gỡ băng bằng faster-whisper). Mô hình ở <môi trường>/hf.
Chỉ dùng thư viện chuẩn của Python ở đây (chạy trước khi có môi trường nào).
"""
import json
import os
import shutil
import subprocess
import sys
import time

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import cau_hinh as CH  # noqa: E402
import do_may  # noqa: E402

GOI = {
    "mlx": ["mlx-audio[tts,stt]==0.6.6", "imageio-ffmpeg", "soundfile", "huggingface_hub"],
    "vieneu": ["vieneu==3.8.4", "soundfile"],
    "chung": ["faster-whisper==1.2.1", "imageio-ffmpeg", "soundfile", "huggingface_hub", "keyring"],
}
XEM = "--xem" in sys.argv
BUOC = [0]


def buoc(tieu_de):
    BUOC[0] += 1
    print(f"\n== {BUOC[0]}/6 {tieu_de}", flush=True)


def uv():
    for p in (shutil.which("uv"), os.path.expanduser("~/.local/bin/uv"), os.path.expanduser("~/.local/bin/uv.exe"),
              os.path.expanduser("~/.cargo/bin/uv")):
        if p and os.path.isfile(p):
            return p
    sys.exit("Không thấy công cụ uv: chạy lại tệp cài đặt bấm đúp của xưởng (tệp đó tự cài uv).")


def chay(cmd, **kw):
    print("   $", " ".join(os.path.basename(c) if i == 0 else c for i, c in enumerate(cmd))[:160], flush=True)
    return subprocess.run(cmd, **kw).returncode


def co_gb(d):
    tong = 0
    for goc, _, tep in os.walk(d):
        for t in tep:
            p = os.path.join(goc, t)
            if not os.path.islink(p):
                try:
                    tong += os.path.getsize(p)
                except OSError:
                    pass
    return tong / 1e9


def ghi_cau_hinh(**kv):
    p = os.path.join(CH.GOC, "cau-hinh.json")
    d = {}
    if os.path.isfile(p):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    d.update(kv)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")


def ket_thuc(ma, loi_nhan=None):
    print()
    if ma == 0:
        print("Cài xong. Quay lại Claude và nhắn: đã cài xưởng lồng tiếng.")
    else:
        print(loi_nhan or "Cài chưa xong.")
        print("Quay lại Claude và nhắn: cài xưởng lồng tiếng bị lỗi, kèm vài dòng báo lỗi cuối cùng trong cửa sổ này.")
    sys.exit(ma)


def main():
    if CH.HE not in ("Darwin", "Windows", "Linux"):
        ket_thuc(1, f"Hệ điều hành {CH.HE} chưa được hỗ trợ.")
    mt = CH.moi_truong()
    hf = os.path.join(mt, "hf")
    if not XEM:
        os.makedirs(hf, exist_ok=True)

    buoc("Đo máy")
    m = do_may.do()
    chon, bang = do_may.de_xuat(m)
    do_may.in_bao_cao(m, chon, bang)
    if not XEM:
        with open(os.path.join(CH.tam(), "may-tinh.json"), "w", encoding="utf-8") as f:
            json.dump({"luc": time.strftime("%Y-%m-%d %H:%M"), "may": m, "deXuat": chon,
                       "danhGia": {k: list(v) for k, v in bang.items()}}, f, ensure_ascii=False, indent=1)

    buoc("Chọn máy đọc")
    md = CH.may_doc()
    dung = CH.may_dung()
    if dung is None:
        dung = chon
        print("Xưởng chưa chọn máy đọc: dùng đề xuất ở trên.")
        if not XEM:
            ghi_cau_hinh(mayDung=dung)
            print("   đã ghi vào cau-hinh.json > mayDung (sửa ở đó rồi chạy lại trình cài để đổi).")
    cai = []
    for k in dung:
        if k not in md:
            print(f"   ! '{k}' không có trong may-doc.json: bỏ qua.")
            continue
        muc, ly_do = bang[k]
        if muc == "khong":
            print(f"   ! {md[k]['ten']}: {ly_do}. Không cài; bỏ khỏi mayDung hoặc đổi máy.")
            continue
        if muc == "duoc" and md[k].get("loai") == "tai-may":
            print(f"   {md[k]['ten']}: {ly_do}")
        cai.append(k)
    print("Máy đọc sẽ dùng:", ", ".join(md[k]["ten"] for k in cai) or "(chưa có)")

    buoc("Môi trường Python")
    can_mt = {"chung"} | {md[k]["moiTruong"] for k in cai}
    can_venv = {CH.ten_venv(x) for x in can_mt}
    can_torch = any(md[k].get("canTorch") for k in cai)
    for ten in ("venv-mlx", "venv-vieneu", "venv-chung"):
        d = os.path.join(mt, ten)
        if ten not in can_venv and os.path.isdir(d):
            print(f"   gỡ {ten} (không còn máy đọc nào dùng, {co_gb(d):.1f} GB)")
            if not XEM:
                shutil.rmtree(d, ignore_errors=True)
    goi_theo_venv = {}
    for x in sorted(can_mt, key=lambda t: t != "chung"):   # môi trường chung trước: các bước sau cần nó
        goi_theo_venv.setdefault(CH.ten_venv(x), (x, GOI["mlx" if CH.ten_venv(x) == "venv-mlx" else x]))
    for ten, (x, goi) in goi_theo_venv.items():
        if XEM:
            print(f"   {ten}: {'có sẵn' if os.path.isdir(os.path.join(mt, ten)) else 'sẽ tạo'}")
            continue
        py = CH.py_moi_truong(x, bat_buoc=False)
        if not os.path.isfile(py) and chay([uv(), "venv", "--python", "3.12", os.path.join(mt, ten)]):
            ket_thuc(1, f"Không tạo được môi trường {ten}: kiểm tra mạng rồi chạy lại.")
        goi = list(goi)
        if ten == "venv-mlx" and can_torch:
            goi.append("torch")
        if chay([uv(), "pip", "install", "--python", py] + goi):
            ket_thuc(1, f"Cài thư viện cho {ten} không thành công: kiểm tra mạng rồi chạy lại.")
        if ten == "venv-mlx" and not can_torch:
            co = subprocess.run([py, "-c", "import importlib.util as u; print(u.find_spec('torch') is not None)"],
                                capture_output=True, text=True).stdout.strip() == "True"
            if co:
                print("   gỡ torch (chỉ Higgs v3 cần)")
                chay([uv(), "pip", "uninstall", "--python", py, "torch"])

    buoc("ffmpeg")
    if not XEM:
        py = CH.py_moi_truong("chung")
        ff = subprocess.run([py, "-c", "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"],
                            capture_output=True, text=True).stdout.strip()
        if not ff or not os.path.isfile(ff):
            ket_thuc(1, "Không tìm được ffmpeg trong môi trường.")
        with open(os.path.join(mt, "ffmpeg.txt"), "w", encoding="utf-8") as f:
            f.write(ff)
        if CH.HE != "Windows":
            os.makedirs(os.path.join(mt, "bin"), exist_ok=True)
            lk = os.path.join(mt, "bin", "ffmpeg")
            if os.path.lexists(lk):
                os.remove(lk)
            os.symlink(ff, lk)
        print("   ", ff)

    buoc("Mô hình")
    env = dict(os.environ, HF_HOME=hf, HF_HUB_DISABLE_TELEMETRY="1", PYTHONUTF8="1", PYTHONUNBUFFERED="1")
    py = CH.py_moi_truong("chung", bat_buoc=not XEM)
    if XEM and not os.path.isfile(py):
        print("   (chưa có môi trường chung: chạy trình cài thật để xem kế hoạch mô hình)")
    elif subprocess.run([py, os.path.join(TOOLS, "tai_mo_hinh.py")] + (["--xem"] if XEM else []), env=env).returncode:
        ket_thuc(1, "Tải mô hình chưa xong (thường do mạng hoặc ổ đĩa): chạy lại trình cài, phần đã tải được giữ lại.")
    if XEM:
        print("\n(Chỉ xem kế hoạch: chưa cài, chưa gỡ gì.)")
        return

    buoc("Tự kiểm: mỗi máy đọc tại máy đọc một câu tiếng Việt, một câu tiếng Anh, rồi gỡ băng ngược")
    rc = subprocess.run([py, os.path.join(TOOLS, "hang_doi.py"), "thu-may"], env=env).returncode
    ket_thuc(rc, "Tự kiểm có lỗi.")


if __name__ == "__main__":
    main()
