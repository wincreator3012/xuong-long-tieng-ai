#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CẤU HÌNH ĐƯỜNG DẪN của xưởng lồng tiếng: repo chỉ chứa NĂNG LỰC; hồ sơ dự án, thành phẩm, việc tạm nằm NGOÀI repo.

    <thư mục mẹ>/
      <repo xưởng>/                công cụ, skill, tài liệu
      Du an/<YYYY-MM tên>/         hồ sơ một bản lồng tiếng: loi-doc.md, luot/, chon.json, thanh-pham/
      Du an/_tam/                  hàng đợi (long-tieng/viec, log), việc tạm; xóa lúc nào cũng được
    môi trường Python, mô hình, ffmpeg (ngoài repo, theo hệ điều hành của máy chạy mô hình):
      Mac      ~/Library/Application Support/xuong-long-tieng/
      Windows  %LOCALAPPDATA%\\xuong-long-tieng\\
      Linux    ~/.local/share/xuong-long-tieng/

Đường dẫn đọc từ cau-hinh.json ở gốc repo (chép từ cau-hinh.mau.json, không lên git), tương đối tính từ gốc repo.

    import cau_hinh as CH
    CH.du_an(), CH.thanh_pham(), CH.tam("long-tieng", "viec")
    CH.may_doc()                  # danh mục máy đọc (may-doc.json)
    CH.may_dung()                 # máy đọc đang bật trên xưởng này (cau-hinh.json > mayDung)
    CH.py_moi_truong("chung")     # python của một môi trường (mlx, vieneu, chung) trên máy chạy mô hình
    CH.tu_dien()                  # từ điển phát âm đã gộp (đề xuất của xưởng, rồi bản đã duyệt trong kho)
    CH.giong("@an")             # hồ sơ giọng riêng trong kho (giong-noi/giong-noi.json)
    CH.giai("@kho/giong-noi/an/mau-vi-01.wav")   # tệp trong kho; "@xuong/..." tệp trong repo
    CH.tuong_doi(p), CH.tuyet_doi(r)              # đường dẫn trong việc tính từ gốc repo: chạy được cả máy ảo lẫn Mac
    CH.xuong_phim()               # thư mục mẹ của xưởng phim (có "Du an/"), để giao tiếng; None nếu không thấy
"""
import json
import os
import platform
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(TOOLS)
sys.dont_write_bytecode = True
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import kho_tu_lieu  # noqa: E402

LOI_KHO = "Kho giọng nằm cạnh xưởng (thư mục 'Kho giong'); chạy python3 tools/dung_xuong.py --kiem để tạo lại."
HE = platform.system()                                      # Darwin, Windows, Linux
APPLE = HE == "Darwin" and platform.machine() == "arm64"     # Mac chip Apple: chạy được mô hình MLX


def _moi_truong_mac_dinh():
    if HE == "Darwin":
        return "~/Library/Application Support/xuong-long-tieng"
    if HE == "Windows":
        return os.path.join(os.environ.get("LOCALAPPDATA") or "~/AppData/Local", "xuong-long-tieng")
    return "~/.local/share/xuong-long-tieng"


MAC_DINH = {
    "thuMucDuAn": "../Du an",
    "thuMucThanhPham": "../Thanh pham",
    "thuMucTam": "../Du an/_tam",
    "thuMucMoiTruong": _moi_truong_mac_dinh(),
    "xuongPhim": ["../../../Xuong phim AI", "../../Xuong phim AI", "~/Xuong phim AI", "~/mnt/Xuong phim AI"],
    "mayDung": None,          # chưa thiết lập: tools/cai_dat.py đo máy rồi đề xuất và ghi vào cau-hinh.json
    "giongRieng": None,       # hồ sơ giọng riêng mặc định, vd "@an"; skill thiết lập ghi vào cau-hinh.json
}


def doc():
    cfg = dict(MAC_DINH)
    p = os.path.join(GOC, "cau-hinh.json")
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as f:
                cfg.update({k: v for k, v in json.load(f).items() if not k.startswith("_")})
        except ValueError:
            pass
    return cfg


def _tuyet_doi(v):
    v = os.path.expanduser(v)
    return os.path.normpath(v if os.path.isabs(v) else os.path.join(GOC, v))


def du_an():
    return _tuyet_doi(doc()["thuMucDuAn"])


def thanh_pham():
    return _tuyet_doi(doc()["thuMucThanhPham"])


def tam(*phan):
    d = os.path.join(_tuyet_doi(doc()["thuMucTam"]), *phan)
    os.makedirs(d, exist_ok=True)
    return d


def moi_truong():
    return _tuyet_doi(doc()["thuMucMoiTruong"])


def xuong_phim():
    v = doc()["xuongPhim"]
    for p in ([v] if isinstance(v, str) else v):
        p = _tuyet_doi(p)
        if os.path.isdir(os.path.join(p, "Du an")):
            return p
    return None


def tuong_doi(p):
    return os.path.relpath(os.path.abspath(p), GOC)


def tuyet_doi(r):
    return r if os.path.isabs(r) else os.path.normpath(os.path.join(GOC, r))


def giai(p):
    """'@kho/<rel>' -> tệp trong kho, '@xuong/<rel>' -> tệp trong repo, khác thì đường dẫn thường (tính từ gốc repo)."""
    if p.startswith("@kho/"):
        goc = kho_tu_lieu.tim()
        if not goc:
            raise SystemExit("Không tìm thấy kho giọng (cần cho " + p + "). " + LOI_KHO)
        return os.path.join(goc, p[5:])
    if p.startswith("@xuong/"):
        return os.path.join(GOC, p[7:])
    return tuyet_doi(p)


def _json(p, mac_dinh=None):
    if not os.path.isfile(p):
        return mac_dinh
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def may_doc():
    return {k: v for k, v in _json(os.path.join(GOC, "may-doc.json"), {}).items() if not k.startswith("_")}


def may_dung():
    """Máy đọc đang bật (cau-hinh.json > mayDung). None: xưởng chưa chọn máy (chạy tools/cai_dat.py)."""
    v = doc().get("mayDung")
    return list(v) if v else None


def giong_rieng():
    """Hồ sơ giọng riêng mặc định của xưởng, vd '@an'; None nếu chưa có."""
    return doc().get("giongRieng")


# Tên môi trường trong may-doc.json > moiTruong -> thư mục venv. "chung" chạy hàng đợi, Bàn nghe, máy đọc đám mây và
# gỡ băng ngược; trên Mac chip Apple nó chính là môi trường MLX (gỡ băng bằng MLX nhanh hơn), máy khác là venv-chung.
def ten_venv(ten):
    ten = {"venv-mlx": "mlx", "venv-vieneu": "vieneu", "venv-chung": "chung"}.get(ten, ten)
    if ten == "chung":
        return "venv-mlx" if APPLE else "venv-chung"
    return "venv-" + ten


def py_moi_truong(ten, bat_buoc=True):
    d = os.path.join(moi_truong(), ten_venv(ten))
    p = os.path.join(d, "Scripts", "python.exe") if HE == "Windows" else os.path.join(d, "bin", "python")
    if bat_buoc and not os.path.isfile(p):
        raise RuntimeError(f"chưa có môi trường {ten_venv(ten)}: chạy trình cài đặt của xưởng trước")
    return p


# Gỡ băng ngược để kiểm: Whisper large-v3-turbo. Mac chip Apple chạy bản MLX, máy khác chạy faster-whisper (CPU,
# hoặc GPU NVIDIA nếu có).
ASR = {"mlx": "mlx-community/whisper-large-v3-turbo-asr-fp16", "fw": "mobiuslabsgmbh/faster-whisper-large-v3-turbo"}


def asr():
    if APPLE:
        return {"boNoi": "go_bang_may", "moiTruong": "mlx", "moHinh": ASR["mlx"]}
    return {"boNoi": "go_bang_fw", "moiTruong": "chung", "moHinh": ASR["fw"]}


def ffmpeg_moi_truong():
    """ffmpeg trình cài đã ghi lại (tải kèm imageio-ffmpeg), hoặc None."""
    mt = moi_truong()
    for p in (os.path.join(mt, "bin", "ffmpeg"), os.path.join(mt, "bin", "ffmpeg.exe")):
        if os.path.isfile(p):
            return p
    try:
        with open(os.path.join(mt, "ffmpeg.txt"), encoding="utf-8") as f:
            p = f.read().strip()
        return p if os.path.isfile(p) else None
    except OSError:
        return None


def duong_tu_dien():
    ra = [os.path.join(GOC, "du-lieu", "phat-am-de-xuat.json")]
    k = kho_tu_lieu.tim()
    if k:
        ra.append(os.path.join(k, "ngon-ngu", "phat-am.json"))
    return ra


def tu_dien():
    import loi_doc
    return loi_doc.doc_tu_dien(*duong_tu_dien())


def ho_so_giong():
    k = kho_tu_lieu.tim()
    if not k:
        return {}
    d = _json(os.path.join(k, "giong-noi", "giong-noi.json"), {}) or {}
    return {kk: v for kk, v in d.items() if not kk.startswith("_")}


def giong(ten):
    """'@an' (hoặc '@an#vi-02' để chỉ định mẫu) -> hồ sơ giọng riêng trong kho; tên khác -> None."""
    if not ten or not str(ten).startswith("@"):
        return None
    hs = ho_so_giong().get(ten[1:].split("#")[0])
    if hs is None:
        raise SystemExit(f"Kho chưa có hồ sơ giọng {ten.split('#')[0]} (giong-noi/giong-noi.json).")
    return hs


if __name__ == "__main__":
    print(json.dumps({"goc": GOC, "duAn": du_an(), "tam": tam(), "moiTruong": moi_truong(), "he": HE,
                      "mayDung": may_dung(), "giongRieng": giong_rieng(),
                      "kho": kho_tu_lieu.tim(), "xuongPhim": xuong_phim()}, ensure_ascii=False, indent=1))
