#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BÀN NGHE: máy chủ nhỏ chạy trên máy thật (chỉ nghe ở 127.0.0.1) để bạn nghe duyệt và thi nghe mù.

    python tools/ban_nghe/may_chu.py [--cong 8768]      ("Mo ban nghe.command" gọi và mở trình duyệt)

Chỉ đọc, ghi trong thư mục "Du an": chon.json (lượt bạn chọn, ghi chú làm lại), thi-nghe/ket-qua.json (điểm),
và thành phẩm khi bạn bấm "Ghép bản chính". Không gửi gì ra ngoài máy.
"""
import argparse
import json
import mimetypes
import os
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import cau_hinh as CH  # noqa: E402
import ghep_tieng  # noqa: E402
import hang_doi as H  # noqa: E402
import loi_doc as L  # noqa: E402

TRANG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
KHOA_GHEP = threading.Lock()


def thu_muc(ten):
    goc = os.path.realpath(CH.du_an())
    p = os.path.realpath(os.path.join(goc, ten))
    if not p.startswith(goc + os.sep) or not os.path.isfile(os.path.join(p, "loi-doc.md")):
        raise FileNotFoundError(ten)
    return p


def danh_sach():
    goc = CH.du_an()
    ra = []
    for ten in sorted(os.listdir(goc), reverse=True) if os.path.isdir(goc) else []:
        p = os.path.join(goc, ten)
        if ten.startswith("_") or not os.path.isfile(os.path.join(p, "loi-doc.md")):
            continue
        luot = os.path.join(p, "luot")
        ra.append({"ten": ten, "soLuot": len(os.listdir(luot)) if os.path.isdir(luot) else 0,
                   "thiNghe": os.path.isfile(os.path.join(p, "thi-nghe.json")),
                   "thanhPham": os.path.isdir(os.path.join(p, "thanh-pham"))})
    return ra


def chi_tiet(ten):
    p = thu_muc(ten)
    kb = L.doc_kich_ban(os.path.join(p, "loi-doc.md"), tu_dien=CH.tu_dien())
    luots = []
    for lt in ghep_tieng.cac_luot(p):
        if lt["luot"].startswith("thi-"):
            continue
        km = lt.pop("_kiem", {}).get("muc", {})
        luots.append({"luot": lt["luot"], "may": lt["may"], "giong": lt.get("giong"), "taoLuc": lt.get("taoLuc"),
                      "doanText": {d["id"]: d["docTrungTinh"] for d in lt["doan"]},
                      "muc": [{**m, "tep": os.path.relpath(CH.tuyet_doi(m["ra"]), p),
                               "co": os.path.isfile(CH.tuyet_doi(m["ra"])), "kiem": km.get(m["id"], {})}
                              for m in lt["muc"]]})
    chon = H.doc_json(os.path.join(p, "chon.json"), {}) or {}
    tp = []
    d = os.path.join(p, "thanh-pham")
    if os.path.isdir(d):
        tp = sorted(x for x in os.listdir(d) if x.endswith(".wav"))
    return {"ten": ten, "thongTin": kb["thongTin"], "canhBao": kb["canhBao"],
            "doan": [{"id": x["id"], "chu": x["chu"], "doc": x["docTrungTinh"], "muc": x["muc"]} for x in kb["doan"]],
            "luot": luots, "chon": chon.get("chon", {}), "lamLai": chon.get("lamLai", {}),
            "thanhPham": [f"thanh-pham/{x}" for x in tp], "tot": ghep_tieng.chon_tep(p, kb, dung_chon=False)}


def thi_nghe(ten, lo=False):
    p = thu_muc(ten)
    thi = H.doc_json(os.path.join(p, "thi-nghe.json"))
    kq = H.doc_json(os.path.join(p, "thi-nghe", "ket-qua.json"))
    uv = []
    for u in thi["ungVien"]:
        x = {"nhan": u["nhan"], "co": os.path.isfile(os.path.join(p, "thi-nghe", u["luot"] + ".wav"))}
        if kq or lo:
            x.update(may=u["may"], giong=u["giong"], bienThe=u.get("bienThe"))
        uv.append(x)
    return {"tieuChi": thi["tieuChi"], "ungVien": uv, "ketQua": kq}


class XuLy(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def gui(self, ma, du_lieu, kieu="application/json; charset=utf-8"):
        if not isinstance(du_lieu, bytes):
            du_lieu = json.dumps(du_lieu, ensure_ascii=False).encode()
        self.send_response(ma)
        self.send_header("Content-Type", kieu)
        self.send_header("Content-Length", str(len(du_lieu)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(du_lieu)

    def gui_tep(self, p):
        if not os.path.isfile(p):
            return self.gui(404, {"loi": "không có tệp"})
        kich = os.path.getsize(p)
        rng = self.headers.get("Range")
        a, b = 0, kich - 1
        if rng and rng.startswith("bytes="):
            x, _, y = rng[6:].partition("-")
            a = int(x or 0)
            b = int(y) if y else kich - 1
        with open(p, "rb") as f:
            f.seek(a)
            du = f.read(b - a + 1)
        self.send_response(206 if rng else 200)
        self.send_header("Content-Type", mimetypes.guess_type(p)[0] or "audio/wav")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(len(du)))
        if rng:
            self.send_header("Content-Range", f"bytes {a}-{b}/{kich}")
        self.end_headers()
        self.wfile.write(du)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        phan = [urllib.parse.unquote(x) for x in u.path.strip("/").split("/") if x]
        try:
            if not phan:
                return self.gui(200, open(TRANG, "rb").read(), "text/html; charset=utf-8")
            if phan[:2] == ["api", "du-an"] and len(phan) == 2:
                return self.gui(200, danh_sach())
            if phan[:2] == ["api", "du-an"] and len(phan) == 3:
                return self.gui(200, chi_tiet(phan[2]))
            if phan[:2] == ["api", "thi-nghe"] and len(phan) == 3:
                return self.gui(200, thi_nghe(phan[2]))
            if phan[0] == "am" and len(phan) >= 3:
                goc = thu_muc(phan[1])
                p = os.path.realpath(os.path.join(goc, *phan[2:]))
                if not p.startswith(goc + os.sep):
                    return self.gui(403, {"loi": "ngoài dự án"})
                return self.gui_tep(p)
            if phan[0] == "am-thi" and len(phan) == 3:
                goc = thu_muc(phan[1])
                thi = H.doc_json(os.path.join(goc, "thi-nghe.json"))
                u_ = next(x for x in thi["ungVien"] if x["nhan"] == phan[2])
                return self.gui_tep(os.path.join(goc, "thi-nghe", u_["luot"] + ".wav"))
        except (FileNotFoundError, StopIteration):
            return self.gui(404, {"loi": "không thấy"})
        except Exception as e:
            return self.gui(500, {"loi": str(e)})
        self.gui(404, {"loi": "không thấy"})

    def do_POST(self):
        phan = [urllib.parse.unquote(x) for x in urllib.parse.urlparse(self.path).path.strip("/").split("/") if x]
        try:
            n = int(self.headers.get("Content-Length") or 0)
            than = json.loads(self.rfile.read(n) or b"{}")
            if phan[:2] == ["api", "du-an"] and len(phan) == 4 and phan[3] == "chon":
                p = thu_muc(phan[2])
                H.ghi_json(os.path.join(p, "chon.json"), {"chon": than.get("chon", {}),
                                                          "lamLai": than.get("lamLai", {}), "capNhat": H.bay_gio()})
                return self.gui(200, {"ok": True})
            if phan[:2] == ["api", "du-an"] and len(phan) == 4 and phan[3] == "ghep":
                p = thu_muc(phan[2])
                with KHOA_GHEP:
                    ra = ghep_tieng.ghep(p, ban_nhap=bool(than.get("banNhap")))
                return self.gui(200, {"ok": True, "tep": os.path.relpath(ra, p)})
            if phan[:2] == ["api", "thi-nghe"] and len(phan) == 3:
                p = thu_muc(phan[2])
                H.ghi_json(os.path.join(p, "thi-nghe", "ket-qua.json"), {"diem": than.get("diem", {}),
                                                                         "luc": H.bay_gio()})
                return self.gui(200, thi_nghe(phan[2], lo=True))
        except SystemExit as e:
            return self.gui(400, {"loi": str(e)})
        except FileNotFoundError:
            return self.gui(404, {"loi": "không thấy"})
        except Exception as e:
            return self.gui(500, {"loi": str(e)})
        self.gui(404, {"loi": "không thấy"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cong", type=int, default=8768)
    ap.add_argument("--khong-mo", action="store_true")
    a = ap.parse_args()
    url = f"http://127.0.0.1:{a.cong}/"
    try:
        may = ThreadingHTTPServer(("127.0.0.1", a.cong), XuLy)
    except OSError:  # cổng đang bận: thường là Bàn nghe đã chạy sẵn trong một cửa sổ khác
        print(f"Bàn nghe đang chạy sẵn; mở lại trình duyệt ở {url}")
        if not a.khong_mo:
            webbrowser.open(url)
        return
    print(f"Bàn nghe đang mở ở {url}  (đóng cửa sổ này để tắt)", flush=True)
    if not a.khong_mo:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        may.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
