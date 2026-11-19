#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HÀNG ĐỢI LỒNG TIẾNG: Claude xếp việc trong máy ảo, máy thật (Mac hoặc Windows) chạy mô hình ngoài máy ảo.

Vì sao: máy ảo Cowork chỉ có khoảng 3-4 GB bộ nhớ, không chạm được chip đồ họa và kho khóa của máy thật.
Mô hình và khóa API chỉ dùng được trên máy thật, nên mọi việc sinh tiếng đi qua hàng đợi này.

Trong máy ảo (Claude, từ gốc repo):
    python3 tools/hang_doi.py them "../Du an/<dự án>" [--may gemini] [--giong Charon|@an] [--so-luot 2]
                                   [--doan d002,d005] [--luot luot-03] [--khong-ghep]
    python3 tools/hang_doi.py go-bang <tệp.wav> ... [--ngon-ngu vi]   # gỡ băng tệp bất kỳ (vd mẫu giọng mới thu)
    python3 tools/hang_doi.py trang-thai
    python3 tools/hang_doi.py don                       # cất việc đã xong
Trên máy thật (bạn bấm đúp "Long tieng tren Mac.command", tệp đó gọi bằng python của môi trường "chung"):
    python tools/hang_doi.py chay                       # sinh tiếng -> gỡ băng ngược -> kiểm -> ghép bản nháp
    python tools/hang_doi.py thu-may                    # tự kiểm sau khi cài: mỗi máy đọc đang bật đọc một câu

Mỗi việc là <Du an>/_tam/long-tieng/viec/<id>.json; kết quả ở <id>.ket-qua.json, nhật ký ở log/<id>.log.
Mọi đường dẫn trong việc tính từ gốc repo, nên cùng một việc chạy được ở máy ảo lẫn máy thật.
Lời đọc và danh sách lượt của một lần sinh nằm trong hồ sơ dự án: luot/<lượt>/luot.json.
"""
import argparse
import datetime as dt
import glob
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import cau_hinh as CH  # noqa: E402
import khoa  # noqa: E402
import loi_doc as L  # noqa: E402

QDIR = CH.tam("long-tieng", "viec")
LOGDIR = CH.tam("long-tieng", "log")


def bay_gio():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def doc_json(p, mac_dinh=None):
    if not os.path.isfile(p):
        return mac_dinh
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def ghi_json(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def slug(s):
    import unicodedata
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d").replace("Đ", "D")
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()[:50] or "x"


def tim_du_an(p):
    """Nhận đường dẫn hồ sơ, hoặc chỉ tên thư mục trong Du an/."""
    for c in (p, os.path.join(CH.du_an(), p)):
        if os.path.isfile(os.path.join(c, "loi-doc.md")):
            return os.path.abspath(c)
    sys.exit(f"Không thấy hồ sơ dự án có loi-doc.md: {p}")


# ----------------------------------------------------------------------------- xếp việc (máy ảo)
def chon_giong(cfg, may, giong, nn):
    if giong:
        return giong
    md = cfg.get("giongMacDinh")
    if isinstance(md, dict):
        return md.get(nn)
    return md


def them(du_an, may=None, giong=None, so_luot=None, chi_doan=None, ten_luot=None, tu_ghep=True,
         loai="sinh", nhan=None, kich_ban="loi-doc.md"):
    du_an = tim_du_an(du_an)
    kb = L.doc_kich_ban(os.path.join(du_an, kich_ban), tu_dien=CH.tu_dien())
    tt = kb["thongTin"]
    may = may or tt.get("may")
    danh_muc = CH.may_doc()
    if may not in danh_muc:
        sys.exit(f"Máy đọc '{may}' không có trong may-doc.json ({', '.join(danh_muc)})")
    cfg = danh_muc[may]
    dung = CH.may_dung()
    if dung is not None and may not in dung:
        sys.exit(f"Máy đọc '{may}' đang tắt trên xưởng này (cau-hinh.json > mayDung: {', '.join(dung)}). "
                 "Muốn bật: thêm vào mayDung rồi chạy lại trình cài đặt trên máy thật để tải mô hình.")
    nn = tt.get("ngonNgu", "vi")
    if nn not in cfg.get("ngonNgu", []):
        sys.exit(f"{cfg['ten']} không đọc ngôn ngữ {nn}")
    giong = chon_giong(cfg, may, giong or (tt.get("giong") if may == tt.get("may") else None), nn)
    if not giong and cfg.get("canGiongMau") and loai != "thu-may":
        sys.exit(f"{cfg['ten']} không có giọng sẵn: cần --giong @<hồ sơ giọng riêng>")
    if giong and giong.startswith("@"):
        CH.giong(giong)  # dừng sớm nếu kho chưa có hồ sơ
    so_luot = int(so_luot or tt.get("soLuot", 2))
    doan = kb["doan"]
    if chi_doan:
        muon = set(chi_doan)
        doan = [d for d in doan if d["id"] in muon]
        if not doan:
            sys.exit("Không có đoạn nào khớp --doan")
    os.makedirs(os.path.join(du_an, "luot"), exist_ok=True)
    if not ten_luot:
        co = [int(m.group(1)) for x in os.listdir(os.path.join(du_an, "luot"))
              for m in [re.match(r"luot-(\d+)$", x)] if m]
        ten_luot = f"luot-{max(co, default=0) + 1:02d}"
    thu_muc = os.path.join(du_an, "luot", ten_luot)
    if os.path.exists(os.path.join(thu_muc, "luot.json")):
        sys.exit(f"Lượt {ten_luot} đã có; đặt tên khác bằng --luot")
    muc = []
    for i, d in enumerate(doan):
        loi = L.cho_may(d, may, cfg, nn)
        d.update({"text": loi["text"], "style": loi.get("style")})
        for lan in range(1, so_luot + 1):
            muc.append({"id": f"{d['id']}-l{lan}", "doan": d["id"], "lan": lan,
                        "hatGiong": lan * 1000 + i + 1,
                        "ra": CH.tuong_doi(os.path.join(thu_muc, f"{d['id']}-l{lan}.wav"))})
    luot = {"luot": ten_luot, "may": may, "moHinh": cfg.get("moHinh"), "giong": giong, "ngonNgu": nn,
            "soLuot": so_luot, "taoLuc": bay_gio(), "nhan": nhan, "kichBan": kich_ban, "thongTin": tt, "canhBao": kb["canhBao"],
            "doan": doan, "muc": muc}
    ghi_json(os.path.join(thu_muc, "luot.json"), luot)
    jid = f"{dt.datetime.now():%Y%m%d-%H%M%S}-{slug(os.path.basename(du_an))[:30]}-{ten_luot}"
    ghi_json(os.path.join(QDIR, jid + ".json"), {
        "id": jid, "loai": loai, "duAn": CH.tuong_doi(du_an), "luot": ten_luot, "may": may,
        "tuGhep": tu_ghep, "xepLuc": bay_gio()})
    for c in kb["canhBao"]:
        print("  cảnh báo:", c)
    print(f"Đã xếp {jid}: {len(doan)} đoạn x {so_luot} lượt, {cfg['ten']}, giọng {giong or 'ngẫu nhiên'}")
    return jid


def them_dang_ky(ho_so, may, mau=None):
    jid = f"{dt.datetime.now():%Y%m%d-%H%M%S}-dang-ky-{slug(ho_so)}-{may}"
    ghi_json(os.path.join(QDIR, jid + ".json"), {"id": jid, "loai": "dang-ky", "hoSo": ho_so, "may": may,
                                                 "mau": mau, "xepLuc": bay_gio()})
    print("Đã xếp", jid)
    return jid


def them_go_bang(tep, nn="vi"):
    """Xếp việc gỡ băng cho tệp bất kỳ (mẫu giọng mới thu...): kết quả <tệp>.gb.json cạnh tệp, chạy trên máy thật."""
    ds = []
    for t in tep:
        if not os.path.isfile(t):
            sys.exit(f"Không thấy tệp {t}")
        ds.append(CH.tuong_doi(t))
    jid = f"{dt.datetime.now():%Y%m%d-%H%M%S}-go-bang-{len(ds)}-tep"
    ghi_json(os.path.join(QDIR, jid + ".json"), {"id": jid, "loai": "go-bang", "tep": ds, "ngonNgu": nn,
                                                 "xepLuc": bay_gio()})
    print(f"Đã xếp {jid}: gỡ băng {len(ds)} tệp; kết quả ở <tệp>.gb.json")
    return jid


def viec():
    ra = []
    for p in sorted(glob.glob(os.path.join(QDIR, "*.json"))):
        if p.endswith(".ket-qua.json") or p.endswith(".tmp"):
            continue
        jid = os.path.basename(p)[:-5]
        ra.append((jid, p, doc_json(os.path.join(QDIR, jid + ".ket-qua.json"))))
    return ra


def trang_thai():
    vs = viec()
    if not vs:
        print("Hàng đợi trống.")
    for jid, p, kq in vs:
        tt = kq["trangThai"] if kq else "chờ"
        them_ = ""
        if kq and kq.get("loi"):
            them_ = f" ({kq['loi'][:160]})"
        elif kq and kq.get("soMuc"):
            them_ = f" ({kq.get('soXong', 0)}/{kq['soMuc']} mục, {kq.get('giay', 0):.0f} giây, máy {kq.get('may')})"
        print(f"{tt:6} {jid}{them_}")


def don():
    dich = CH.tam("long-tieng", "xong")
    n = 0
    for jid, p, kq in viec():
        if kq and kq.get("trangThai") == "xong":
            for t in (p, os.path.join(QDIR, jid + ".ket-qua.json")):
                shutil.move(t, os.path.join(dich, os.path.basename(t)))
            n += 1
    print(f"Đã cất {n} việc vào {dich}")


# ----------------------------------------------------------------------------- chạy (máy thật)
def lay_khoa(ten):
    return khoa.lay(ten)


def env_chay():
    e = dict(os.environ)
    mt = CH.moi_truong()
    e["HF_HOME"] = os.path.join(mt, "hf")
    e["HF_HUB_DISABLE_TELEMETRY"] = "1"
    e["PYTHONUNBUFFERED"] = "1"
    e["PYTHONUTF8"] = "1"   # Windows: in tiếng Việt ra cửa sổ lệnh không lỗi mã hóa
    ff = CH.ffmpeg_moi_truong()
    if ff:
        e["XLT_FFMPEG"] = ff
        e["PATH"] = os.path.dirname(ff) + os.pathsep + e.get("PATH", "")
    for k in {v.get("khoa") for v in CH.may_doc().values() if v.get("khoa")}:
        v = lay_khoa(k)
        if v:
            e["XLT_KHOA_" + k.upper()] = v
    return e


def chay_bo_noi(bo_noi, moi_truong, ds, log):
    """Chạy một bộ nối trong môi trường của nó; trả {id: kết quả}."""
    p_ds = os.path.join(CH.tam("long-tieng"), f"ds-{ds['may']}.json")
    ghi_json(p_ds, ds)
    cmd = [CH.py_moi_truong(moi_truong), os.path.join(TOOLS, "may_doc", bo_noi + ".py"), p_ds]
    ket = {}
    log.write(f"\n== {bay_gio()} {ds['may']}: {len(ds['muc'])} mục\n")
    log.flush()
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                          errors="replace", env=env_chay(), cwd=CH.GOC)
    for dong in pr.stdout:
        log.write(dong)
        log.flush()
        if dong.startswith("@@"):
            try:
                k = json.loads(dong[2:])
                ket[k["id"]] = k
            except ValueError:
                pass
        elif dong.strip():
            print("   ", dong.rstrip()[:200], flush=True)
    pr.wait()
    for m in ds["muc"]:
        ket.setdefault(m["id"], {"id": m["id"], "ok": False, "loi": f"bộ nối dừng (mã {pr.returncode}), xem log"})
    return ket


def mau_cho(giong, nn, may):
    """Hồ sơ giọng riêng -> thông tin mẫu cho bộ nối (tệp, lời, mã giọng đám mây)."""
    hs = CH.giong(giong)
    chinh = (hs.get("mauChinh") or {})
    chi_dinh = giong.split("#")[1] if "#" in giong else None   # @an#vi-02: dùng đúng mẫu vi-02
    ma = chi_dinh or chinh.get(nn) or chinh.get("vi") or chinh.get("en")
    mau = next((m for m in hs.get("mau", []) if m.get("id") == ma), None)
    if chi_dinh and not any(m.get("id") == ma for m in hs.get("mau", [])):
        raise RuntimeError(f"hồ sơ {giong.split('#')[0]} không có mẫu {ma}")
    ra = {"ten": giong[1:].replace("#", "-")}
    if mau:
        ra.update(tep=CH.giai("@kho/" + mau["tep"]), loi=mau["loi"], ma=mau["id"])
    dk = hs.get("dangKy") or {}
    for k in ("gemini", "elevenlabs"):
        if dk.get(k):
            ra[k] = dk[k].get("id") if isinstance(dk[k], dict) else dk[k]
    if CH.may_doc().get(may, {}).get("loai") == "tai-may" and "tep" not in ra:
        raise RuntimeError(f"hồ sơ {giong} chưa chọn mẫu chính cho {nn} (giong-noi.json > mauChinh)")
    return ra


def chay(chi=None):
    vs = [(j, p, kq) for j, p, kq in viec() if not kq or kq.get("trangThai") != "xong"]
    if chi:
        vs = [x for x in vs if x[0] in chi]
    if not vs:
        print("Không có việc nào đang chờ.")
        return 0
    danh_muc = CH.may_doc()
    t0 = time.time()
    tong_loi = 0
    may_tinh = platform.node()
    # 1. gom mục theo máy đọc để mỗi mô hình chỉ nạp một lần
    theo_may, cua_viec = {}, {}
    for jid, p, _ in vs:
        v = doc_json(p)
        if v["loai"] in ("dang-ky", "go-bang"):
            continue
        du_an = CH.tuyet_doi(v["duAn"])
        luot = doc_json(os.path.join(du_an, "luot", v["luot"], "luot.json"))
        cfg = danh_muc[luot["may"]]
        theo_doan = {d["id"]: d for d in luot["doan"]}
        try:
            mau = mau_cho(luot["giong"], luot["ngonNgu"], luot["may"]) if (luot.get("giong") or "").startswith("@") else None
        except (RuntimeError, SystemExit) as e:
            ghi_json(os.path.join(QDIR, jid + ".ket-qua.json"), {"trangThai": "loi", "loi": str(e), "may": may_tinh,
                                                                 "luc": bay_gio()})
            tong_loi += 1
            continue
        ds = theo_may.setdefault(luot["may"], {"may": luot["may"], "moHinh": cfg.get("moHinh"),
                                               "dinhDang": cfg.get("dinhDang"), "muc": [], "_cfg": cfg})
        cua_viec[jid] = (v, du_an, luot, [])
        for m in luot["muc"]:
            d = theo_doan[m["doan"]]
            mid = f"{jid}|{m['id']}"
            ds["muc"].append({"id": mid, "text": d["text"], "style": d.get("style"), "ngonNgu": luot["ngonNgu"],
                              "giong": None if mau else luot.get("giong"), "mau": mau, "hatGiong": m["hatGiong"],
                              "ra": CH.tuyet_doi(m["ra"])})
            cua_viec[jid][3].append(mid)
    ket = {}
    for may, ds in theo_may.items():
        cfg = ds.pop("_cfg")
        print(f"\n>> {cfg['ten']}: {len(ds['muc'])} mục", flush=True)
        with open(os.path.join(LOGDIR, f"{dt.datetime.now():%Y%m%d}-{may}.log"), "a", encoding="utf-8") as log:
            try:
                ket.update(chay_bo_noi(cfg["boNoi"], cfg["moiTruong"], ds, log))
            except RuntimeError as e:
                for m in ds["muc"]:
                    ket[m["id"]] = {"id": m["id"], "ok": False, "loi": str(e)}
    # 2. gỡ băng ngược mọi tệp vừa có, cùng các tệp của việc "go-bang"
    gb, viec_gb = [], []
    for jid, p, _ in vs:
        v = doc_json(p)
        if v["loai"] == "go-bang":
            viec_gb.append((jid, v))
            for i, t in enumerate(v["tep"]):
                wav = CH.tuyet_doi(t)
                gb.append({"id": f"{jid}|{i}", "vao": wav, "ngonNgu": v.get("ngonNgu", "vi"),
                           "ra": os.path.splitext(wav)[0] + ".gb.json"})
    for jid, (v, du_an, luot, ids) in cua_viec.items():
        for m in luot["muc"]:
            wav = CH.tuyet_doi(m["ra"])
            if os.path.isfile(wav) and not os.path.isfile(wav[:-4] + ".gb.json"):
                gb.append({"id": f"{jid}|{m['id']}|gb", "vao": wav, "ngonNgu": luot["ngonNgu"],
                           "ra": wav[:-4] + ".gb.json"})
    if gb:
        print(f"\n>> Gỡ băng ngược để kiểm: {len(gb)} tệp", flush=True)
        asr = CH.asr()
        with open(os.path.join(LOGDIR, f"{dt.datetime.now():%Y%m%d}-go-bang.log"), "a", encoding="utf-8") as log:
            try:
                ket_gb = chay_bo_noi(asr["boNoi"], asr["moiTruong"], {"may": "whisper", "moHinh": asr["moHinh"], "muc": gb}, log)
            except RuntimeError as e:
                print("   gỡ băng ngược không chạy được:", e)
                ket_gb = {}
        for jid, v in viec_gb:
            ok = [ket_gb.get(f"{jid}|{i}", {}).get("ok") for i in range(len(v["tep"]))]
            kq = {"trangThai": "xong" if all(ok) else "loi", "soMuc": len(ok), "soXong": sum(1 for x in ok if x),
                  "may": may_tinh, "luc": bay_gio(), "giay": round(time.time() - t0, 1)}
            if not all(ok):
                kq["loi"] = "có tệp gỡ băng không được, xem log go-bang"
                tong_loi += 1
            ghi_json(os.path.join(QDIR, jid + ".ket-qua.json"), kq)
    # 3. kiểm, ghép bản nháp, ghi kết quả từng việc
    import kiem_tieng
    import ghep_tieng
    for jid, (v, du_an, luot, ids) in cua_viec.items():
        xong = [i for i in ids if ket.get(i, {}).get("ok")]
        loi = [ket[i].get("loi") for i in ids if i in ket and not ket[i].get("ok")]
        kq = {"trangThai": "xong" if len(xong) == len(ids) else "loi", "soMuc": len(ids), "soXong": len(xong),
              "may": may_tinh, "luc": bay_gio(), "giay": round(time.time() - t0, 1)}
        if loi:
            kq["loi"] = loi[0]
            tong_loi += 1
        if xong:
            try:
                kiem_tieng.kiem_luot(du_an, v["luot"], in_bang=True)
                if v.get("tuGhep"):
                    ghep_tieng.ghep(du_an, ban_nhap=True, chi_luot=v["luot"] if v.get("loai") == "thi-nghe" else None,
                                    ten=None if v.get("loai") != "thi-nghe" else v["luot"])
            except Exception as e:  # kiểm hay ghép hỏng không làm mất tiếng đã sinh
                kq["canhBao"] = f"kiểm hoặc ghép không xong: {e}"
                print("   ", kq["canhBao"])
        ghi_json(os.path.join(QDIR, jid + ".ket-qua.json"), kq)
    # 4. việc đăng ký giọng riêng với dịch vụ đám mây
    for jid, p, _ in vs:
        v = doc_json(p)
        if v["loai"] != "dang-ky":
            continue
        import giong_rieng
        try:
            ma = giong_rieng.dang_ky_tren_mac(v["hoSo"], v["may"], v.get("mau"), lay_khoa(v["may"]))
            ghi_json(os.path.join(QDIR, jid + ".ket-qua.json"), {"trangThai": "xong", "ma": ma, "luc": bay_gio(),
                                                                 "may": may_tinh})
            print(f"\n>> Đã đăng ký giọng {v['hoSo']} với {v['may']}: {ma}")
        except Exception as e:
            tong_loi += 1
            ghi_json(os.path.join(QDIR, jid + ".ket-qua.json"), {"trangThai": "loi", "loi": str(e)[:800],
                                                                 "luc": bay_gio(), "may": may_tinh})
            print(f"\n>> Đăng ký giọng {v['hoSo']} với {v['may']} không được: {e}")
    print(f"\nXong sau {time.time() - t0:.0f} giây.")
    trang_thai()
    return 1 if tong_loi else 0


def thu_may():
    """Tự kiểm sau khi cài: mỗi máy đọc tại máy đang bật đọc một câu tiếng Việt, một câu tiếng Anh, rồi gỡ băng ngược."""
    goc = os.path.join(CH.du_an(), "_kiem-may")
    os.makedirs(goc, exist_ok=True)
    rieng = CH.giong_rieng()
    try:
        mau_chinh = (CH.giong(rieng) or {}).get("mauChinh") or {} if rieng else {}
    except SystemExit:
        mau_chinh = {}
    dung = CH.may_dung() or []
    jids = []
    for nn, cau in (("vi", "Xin chào, đây là xưởng lồng tiếng. Hôm nay là ngày 19/11/2026, trời rất đẹp."),
                    ("en", "Hello, this is the voice workshop. Take a slow breath, and notice how you feel.")):
        d = os.path.join(goc, nn)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "loi-doc.md"), "w", encoding="utf-8") as f:
            f.write(f"---\ntieuDe: Kiểm máy {nn}\nngonNgu: {nn}\nsoLuot: 1\n---\n\n{cau}\n")
        if os.path.isdir(os.path.join(d, "luot")):
            shutil.rmtree(os.path.join(d, "luot"))
        for may, cfg in CH.may_doc().items():
            if cfg["loai"] != "tai-may" or may not in dung:
                continue
            # máy cần mẫu giọng dùng giọng riêng khi kho đã có mẫu; chưa có thì giọng ngẫu nhiên (vẫn kiểm được cài đặt)
            giong = rieng if mau_chinh and cfg.get("canGiongMau") else None
            jids.append(them(d, may=may, giong=giong, so_luot=1, ten_luot=may, tu_ghep=False, loai="thu-may"))
    rc = chay(set(jids))
    thieu = [os.path.relpath(p, goc) for p in glob.glob(os.path.join(goc, "*", "luot", "*", "*.wav"))
             if not p.endswith(".gb.wav") and not os.path.isfile(p[:-4] + ".gb.json")]
    if thieu:
        print("\nGỡ băng ngược chưa chạy được (xem log trong Du an/_tam/long-tieng/log/):", ", ".join(thieu))
        return 1
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="lenh", required=True)
    a = sp.add_parser("them")
    a.add_argument("du_an")
    a.add_argument("--may")
    a.add_argument("--giong")
    a.add_argument("--so-luot", type=int)
    a.add_argument("--doan", help="vd d002,d005")
    a.add_argument("--luot")
    a.add_argument("--khong-ghep", action="store_true")
    g = sp.add_parser("go-bang")
    g.add_argument("tep", nargs="+")
    g.add_argument("--ngon-ngu", default="vi")
    sp.add_parser("trang-thai")
    sp.add_parser("don")
    c = sp.add_parser("chay")
    c.add_argument("--viec", nargs="*")
    sp.add_parser("thu-may")
    a = ap.parse_args()
    if a.lenh == "them":
        them(a.du_an, a.may, a.giong, a.so_luot, a.doan.split(",") if a.doan else None, a.luot,
             tu_ghep=not a.khong_ghep)
    elif a.lenh == "go-bang":
        them_go_bang(a.tep, a.ngon_ngu)
    elif a.lenh == "trang-thai":
        trang_thai()
    elif a.lenh == "don":
        don()
    elif a.lenh == "chay":
        sys.exit(chay(set(a.viec) if a.viec else None))
    elif a.lenh == "thu-may":
        sys.exit(thu_may())


if __name__ == "__main__":
    main()
