#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LUỒNG GỠ BĂNG: từ tệp tiếng hoặc phim ra transcript đã soát, có khâu hỏi lại bạn những chữ nghe chưa chắc.

    Gỡ băng      Whisper large-v3-turbo chạy trên máy thật (hàng đợi chung với lồng tiếng): mốc và độ chắc từng chữ.
    Máy rà       chữ máy nghe không chắc, chữ gần giống tên riêng hay thuật ngữ đã biết, tên riêng lạ, từ nước ngoài,
                 câu nghe ảo, quãng dài không có lời.
    Claude soát  đọc cả bản theo ngữ cảnh: bỏ chỗ máy báo nhầm, thêm chỗ nghe sai nghĩa, đề xuất chữ đúng.
    Hỏi bạn      danh sách chỗ cần xác nhận (trong chat, hoặc nghe từng chỗ ở Bàn soát), ghi câu trả lời.
    Xuất         áp mọi chỗ sửa, xuất .md (đọc), .txt (lời trơn), .srt (phụ đề), .json (đủ mốc); học từ vựng mới.

Trong máy ảo (Claude, từ gốc repo):
    python3 tools/go_bang.py moi "<Ten khong dau>" [<tệp> ...] [--tieu-de "..."] [--ngon-ngu vi]
                                [--tu "tên riêng, thuật ngữ"] [--boi-canh "buổi gì, ai nói"]
    python3 tools/go_bang.py xep <dự án>                 # xếp việc gỡ băng mọi tệp trong nguon/
    python3 tools/go_bang.py soat <dự án> [--lai]        # máy rà, ghi soat/cho-can-hoi.json
    python3 tools/go_bang.py doc <dự án> [--tep 0] [--tu 0] [--den 10]   # bản nháp theo phút, chỗ nghi đánh dấu
    python3 tools/go_bang.py them-cho <dự án> --moc 754.2 --chu "sưởng" --de-xuat "xưởng" [--tu-sua] [--moi-noi]
                                [--ly-do "..."] [--tep 0]
    python3 tools/go_bang.py bo-cho <dự án> c003 c007    # chỗ máy báo nhầm, không hỏi bạn
    python3 tools/go_bang.py de-xuat <dự án> c003 "chữ A" ["chữ B"] [--tu-sua]
    python3 tools/go_bang.py hoi <dự án> [--toi-da 30]   # danh sách hỏi bạn, ghi soat/HOI.md
    python3 tools/go_bang.py tra-loi <dự án> 3=+ 5=ok 7=- 8=? c012="chữ đúng"
    python3 tools/go_bang.py xuat <dự án> [--con-lai de-xuat|giu]
    python3 tools/go_bang.py trang-thai <dự án>

Câu trả lời: "ok" giữ như máy nghe; "+" lấy đề xuất đầu; "+2" đề xuất thứ hai; "-" xóa (câu nghe ảo);
"?" không rõ (ghi [không rõ] trong bản cuối); chữ khác là chữ đúng bạn gõ.
Hồ sơ: Du an/<YYYY-MM tên>/go-bang.json, nguon/, tho/ (bản máy gỡ, tệp nghe), soat/, thanh-pham/.
"""
import argparse
import datetime as dt
import difflib
import glob
import json
import os
import re
import shutil
import sys
import unicodedata

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import cau_hinh as CH  # noqa: E402
import kho_tu_lieu  # noqa: E402

DUOI_TEP = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma", ".aiff", ".aif", ".caf",
            ".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mts", ".3gp"}
TU_VUNG_XUONG = os.environ.get("XLT_TU_VUNG") or os.path.join(CH.GOC, "du-lieu", "tu-vung-de-xuat.json")  # biến: để thử
NGUONG_KHONG_CHAC = 0.5      # độ chắc dưới mức này: hỏi
NGUONG_RAT_KHONG_CHAC = 0.3  # dưới mức này: ưu tiên cao
NGUONG_KHOANG_TRONG = 8.0    # giây không có lời giữa hai câu: hỏi im lặng thật hay máy bỏ sót
CAU_NGHE_AO = ["cảm ơn các bạn đã theo dõi", "cảm ơn các bạn đã lắng nghe", "hãy đăng ký kênh", "đăng ký kênh",
               "subscribe cho kênh", "like và share", "hẹn gặp lại các bạn trong những video tiếp theo",
               "hẹn gặp lại các bạn trong video tiếp theo", "ghiền mì gõ", "để không bỏ lỡ những video hấp dẫn",
               "phụ đề được thực hiện bởi", "thanks for watching"]
TEN_QUEN = {"Việt Nam", "Hà Nội", "Sài Gòn", "Thành phố Hồ Chí Minh", "Đà Nẵng", "Huế", "Phật", "Đức Phật", "Chúa",
            "Trời", "Mỹ", "Bạn", "Pháp", "Nhật", "Trung Quốc", "Hàn Quốc", "Thái Lan", "Tết"}
TEN_LOAI = {"khong-chac": "máy nghe không chắc", "tu-vung": "gần giống từ vựng đã biết", "ten-rieng": "tên riêng",
            "tieng-ngoai": "từ nước ngoài", "nghe-ao": "nghi máy nghe ảo", "khoang-trong": "quãng không có lời",
            "ngu-canh": "nghe sai theo ngữ cảnh"}


# ----------------------------------------------------------------------------- tiện ích
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


def ghi_chu(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def khong_dau(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D")


def chuan(s):
    """So khớp lỏng: bỏ dấu, chữ thường, bỏ mọi thứ không phải chữ số."""
    return re.sub(r"[^a-z0-9]", "", khong_dau(s).lower())


def tron(s):
    """Bỏ dấu câu bao quanh một chữ, giữ nguyên dấu thanh và hoa thường."""
    return re.sub(r"^[\W_]+|[\W_]+$", "", s.strip())


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", khong_dau(s)).strip("-").lower()[:60] or "x"


def moc(t, gio=None):
    t = max(0.0, float(t or 0))
    h, r = divmod(int(t), 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if (gio or h) else f"{m:02d}:{s:02d}"


def moc_srt(t):
    t = max(0.0, float(t or 0))
    ms = int(round(t * 1000))
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    s, ms = divmod(r, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ----------------------------------------------------------------------------- âm tiết tiếng Việt
_DAU_THANH = {"̀", "́", "̃", "̉", "̣"}
_AM_DAU = r"(ngh|ng|gh|gi|ch|kh|nh|ph|th|tr|qu|[bcdđghklmnprstvx])?"
_VAN = ("a ă â e ê i o ô ơ u ư y ai ao au ay âu ây eo êu ia iê iu oa oă oe oi ôi ơi ua uâ uê ui uô uơ uy ưa ưi ươ ưu yê "
        "iêu yêu oai oay oao oeo uây uôi ươi ươu uya uyê uyu").split()
_AM_TIET = re.compile("^" + _AM_DAU + "(" + "|".join(sorted(_VAN, key=len, reverse=True)) + ")(ch|ng|nh|[cmnpt])?$")


def bo_thanh(s):
    s = unicodedata.normalize("NFD", s)
    return unicodedata.normalize("NFC", "".join(c for c in s if c not in _DAU_THANH))


def la_am_tiet_viet(chu):
    """Chữ có dáng một âm tiết tiếng Việt (không xét có nghĩa hay không)."""
    w = bo_thanh(tron(chu).lower())
    return bool(w) and bool(_AM_TIET.match(w))


def la_tieng_ngoai(chu):
    w = tron(chu)
    if not w or not re.search(r"[A-Za-z]", w) or re.search(r"\d", w):
        return False
    if len(w) >= 2 and w.isupper():
        return True                     # viết tắt
    return not la_am_tiet_viet(w)


# ----------------------------------------------------------------------------- hồ sơ dự án
def tim_du_an(p):
    for c in (p, os.path.join(CH.du_an(), p)):
        if os.path.isfile(os.path.join(c, "go-bang.json")):
            return os.path.abspath(c)
    sys.exit(f"Không thấy dự án gỡ băng (có go-bang.json): {p}")


def thong_tin(du_an):
    return doc_json(os.path.join(du_an, "go-bang.json"), {})


def tep_nguon(du_an):
    d = os.path.join(du_an, "nguon")
    if not os.path.isdir(d):
        return []
    return sorted(x for x in os.listdir(d) if os.path.splitext(x)[1].lower() in DUOI_TEP and not x.startswith("."))


def duong_tho(du_an, ten):
    return os.path.join(du_an, "tho", ten + ".gb.json"), os.path.join(du_an, "tho", ten + ".nghe.m4a")


def moi(ten, tep, tieu_de=None, ngon_ngu="vi", tu=None, boi_canh=None):
    d = os.path.join(CH.du_an(), f"{dt.date.today():%Y-%m} {ten}")
    if os.path.exists(d):
        sys.exit(f"Đã có {d}")
    os.makedirs(os.path.join(d, "nguon"), exist_ok=True)
    for t in tep:
        if not os.path.isfile(t):
            sys.exit(f"Không thấy tệp {t}")
        if os.path.splitext(t)[1].lower() not in DUOI_TEP:
            sys.exit(f"Không nhận dạng tệp tiếng hay phim: {t}")
        dich = os.path.join(d, "nguon", os.path.basename(t))
        if not os.path.exists(dich):
            shutil.copy2(t, dich)
    ghi_json(os.path.join(d, "go-bang.json"), {
        "loai": "go-bang", "tieuDe": tieu_de or ten, "ngonNgu": ngon_ngu,
        "tuVung": [x.strip() for x in re.split(r"[,;\n]", tu or "") if x.strip()],
        "boiCanh": boi_canh or "", "taoLuc": bay_gio()})
    print(d)
    if not tep:
        print("Chép tệp tiếng hoặc phim vào", os.path.join(d, "nguon"), "rồi chạy: go_bang.py xep", f'"{d}"')
    return d


# ----------------------------------------------------------------------------- từ vựng
def _doc_muc(p):
    return (doc_json(p, {}) or {}).get("muc", {}) or {}


def _cung_am_dau(chu, doc):
    """Cách đọc có cùng âm đầu với chữ gốc không: phân biệt cách đọc phiên âm (xô mi) với lời dịch nghĩa."""
    a, b = khong_dau(chu).lower(), khong_dau(doc).lower()
    if not a or not b:
        return False
    nguyen = "aeiouy"
    nhom = {"f": ("ph",), "w": ("o", "u", "qu"), "z": ("d", "gi"), "j": ("gi", "d", "j"), "s": ("x", "s"),
            "c": ("c", "k", "q", "x"), "k": ("c", "k", "q"), "q": ("c", "k", "q"), "x": ("x", "s", "e"),
            "t": ("t", "th"), "d": ("d", "đ"), "g": ("g", "gh", "gi")}
    if a[0] in nguyen:
        return b[0] in nguyen or b.startswith(("o", "u", "y"))
    return b.startswith(nhom.get(a[0], (a[0],)))


def tu_vung(du_an=None):
    """Danh sách {chu, bien: [cách nghe nhầm, cách đọc phiên âm], nguon} theo thứ tự ưu tiên."""
    ra, thay = [], {}

    def them(chu, bien=(), nguon=""):
        chu = (chu or "").strip()
        if not chu or len(chu) < 2:
            return
        if chu in thay:
            x = thay[chu]
            x["bien"] = list(dict.fromkeys(x["bien"] + [b for b in bien if b and b != chu]))
            return
        thay[chu] = {"chu": chu, "bien": [b for b in dict.fromkeys(bien) if b and b != chu], "nguon": nguon}
        ra.append(thay[chu])

    if du_an:
        for x in thong_tin(du_an).get("tuVung", []):
            them(x, nguon="dự án")
    kho = kho_tu_lieu.tim()
    for p, nguon in ((os.path.join(kho, "ngon-ngu", "tu-vung.json") if kho else None, "kho"),
                     (TU_VUNG_XUONG, "xưởng")):
        for chu, v in (_doc_muc(p) if p else {}).items():
            them(chu, v.get("bienThe", []), nguon)
    for p in CH.duong_tu_dien():           # từ điển phát âm: cách đọc phiên âm là cách máy dễ nghe nhầm
        for chu, v in _doc_muc(p).items():
            doc = (v or {}).get("vi") if isinstance(v, dict) else None
            if "." in chu:
                continue
            bien = [doc] if doc and _cung_am_dau(chu, doc) else []
            them(chu, bien, "phát âm")
    return ra


def goi_y(du_an, toi_da=380):
    """Lời gợi cho Whisper: bối cảnh và các tên riêng, thuật ngữ (Whisper chỉ nhận khoảng 220 token)."""
    tt = thong_tin(du_an)
    phan = [tt.get("boiCanh", "").strip().rstrip(".")]
    # chỉ tên riêng, thuật ngữ thật sự (dự án, kho, đã học); từ điển phát âm chỉ dùng để rà, vì gợi quá nhiều
    # từ phổ thông làm Whisper chèn từ đó vào chỗ không ai nói
    chu = [x["chu"] for x in tu_vung(du_an) if x["nguon"] != "phát âm"]
    s = ". ".join(p for p in phan if p)
    if chu:
        them_ = []
        for c in chu:
            if len(s) + len(", ".join(them_ + [c])) + 2 > toi_da:
                break
            them_.append(c)
        s = (s + ". " if s else "") + ", ".join(them_) + "."
    return s or None


# ----------------------------------------------------------------------------- xếp việc
def xep(du_an):
    du_an = tim_du_an(du_an)
    ds = tep_nguon(du_an)
    if not ds:
        sys.exit(f"Thư mục nguon/ chưa có tệp tiếng hay phim: {os.path.join(du_an, 'nguon')}")
    can = [t for t in ds if not os.path.isfile(duong_tho(du_an, t)[0])]
    if not can:
        print("Mọi tệp đã gỡ băng xong. Chạy: go_bang.py soat", f'"{du_an}"')
        return None
    import hang_doi
    tt = thong_tin(du_an)
    tt["tep"] = ds
    ghi_json(os.path.join(du_an, "go-bang.json"), tt)
    gy = goi_y(du_an)
    jid = hang_doi.them_go_bang([os.path.join(du_an, "nguon", t) for t in can], tt.get("ngonNgu", "vi"),
                                thu_muc_ra=os.path.join(du_an, "tho"), chi_tiet=True, goi_y=gy,
                                nhan=os.path.basename(du_an))
    if gy:
        print("  gợi ý từ vựng cho máy nghe:", gy)
    return jid


# ----------------------------------------------------------------------------- bản nháp
def nap_ban(du_an):
    """[(tên tệp, bản gỡ băng)] theo thứ tự trong nguon/; câu nào thiếu chữ (bộ gỡ cũ) thì tách chữ theo khoảng trắng."""
    ra = []
    for ten in tep_nguon(du_an):
        gb = doc_json(duong_tho(du_an, ten)[0])
        if not gb:
            continue
        for d in gb.get("doan", []):
            if not d.get("chu"):
                d["chu"] = [{"w": " " + w, "s": None, "e": None, "p": None} for w in d.get("text", "").split()]
        ra.append((ten, gb))
    return ra


def chu_phang(gb):
    """Danh sách phẳng (chỉ số câu, chỉ số chữ, chữ) để lấy ngữ cảnh xuyên câu."""
    return [(i, j, c) for i, d in enumerate(gb["doan"]) for j, c in enumerate(d["chu"])]


def van_noi(i, a, b, gb):
    return " ".join(tron(c["w"]) for c in gb["doan"][i]["chu"][a:b + 1] if tron(c["w"])) or \
        " ".join(c["w"].strip() for c in gb["doan"][i]["chu"][a:b + 1])


def ngu_canh(gb, phang, i, a, b, n=8):
    vi_tri = {(x[0], x[1]): k for k, x in enumerate(phang)}
    k0, k1 = vi_tri.get((i, a)), vi_tri.get((i, b))
    if k0 is None:
        return "", ""
    truoc = "".join(x[2]["w"] for x in phang[max(0, k0 - n):k0]).strip()
    sau = "".join(x[2]["w"] for x in phang[k1 + 1:k1 + 1 + n]).strip()
    return truoc, sau


def moc_noi(gb, i, a, b):
    d = gb["doan"][i]
    cs = d["chu"][a:b + 1]
    s = next((c["s"] for c in cs if c.get("s") is not None), d.get("start"))
    e = next((c["e"] for c in reversed(cs) if c.get("e") is not None), d.get("end"))
    return s, e


# ----------------------------------------------------------------------------- máy rà
def _cho(tep, loai, gb, i, a, b, ly_do, muc=2, de_xuat=None, tu_sua=False, chen=False):
    return {"tep": tep, "loai": loai, "noi": [{"d": i, "a": a, "b": b, **({"chen": True} if chen else {})}],
            "lyDo": [ly_do], "muc": muc, "deXuat": list(de_xuat or []), "tuSua": tu_sua, "tu": "máy"}


def ra_soat_tep(k, gb, tv, nn="vi"):
    cho = []
    viet = nn == "vi"
    doan = gb["doan"]
    # 1. chữ máy nghe không chắc: gom các chữ liền nhau dưới 0,7 quanh một chữ dưới ngưỡng
    for i, d in enumerate(doan):
        cs = d["chu"]
        j = 0
        while j < len(cs):
            p = cs[j].get("p")
            if p is not None and p < NGUONG_KHONG_CHAC and tron(cs[j]["w"]):
                a = b = j
                while a > 0 and (cs[a - 1].get("p") or 1) < 0.7 and tron(cs[a - 1]["w"]):
                    a -= 1
                while b + 1 < len(cs) and (cs[b + 1].get("p") or 1) < 0.7 and tron(cs[b + 1]["w"]):
                    b += 1
                pmin = min(c.get("p") or 1 for c in cs[a:b + 1])
                cho.append(_cho(k, "khong-chac", gb, i, a, b, f"máy nghe không chắc ({pmin:.0%})",
                                1 if pmin < NGUONG_RAT_KHONG_CHAC else 2))
                j = b + 1
            else:
                j += 1
    # 2. gần giống từ vựng đã biết, và viết sai chính tả của từ vựng (khác hoa thường, dấu, cách)
    dang = []
    for x in tv:
        for f, la_bien in [(x["chu"], False)] + [(b, True) for b in x["bien"]]:
            n = chuan(f)
            if len(n) >= 2:
                dang.append((n, x["chu"], la_bien, len(f.split())))
    for i, d in enumerate(doan):
        cs = d["chu"]
        dung = set()
        for a in range(len(cs)):
            if a in dung:
                continue
            tot = None
            for dai in (4, 3, 2, 1):
                b = a + dai - 1
                if b >= len(cs):
                    continue
                if any(not tron(c["w"]) for c in cs[a:b + 1]):
                    continue
                goc = " ".join(tron(c["w"]) for c in cs[a:b + 1])
                n = chuan(goc)
                if len(n) < 2:
                    continue
                pmin = min((c.get("p") if c.get("p") is not None else 1) for c in cs[a:b + 1])
                for nf, dung_chu, la_bien, so_am in dang:
                    if goc == dung_chu:
                        tot = ("dung", a, b)
                        break
                    if n == nf:
                        if la_bien and so_am == 1 and pmin >= 0.75 and la_am_tiet_viet(goc):
                            continue    # chữ tiếng Việt một âm tiết nghe chắc: không phải nghe nhầm
                        toan_viet = all(la_am_tiet_viet(x) for x in goc.split())
                        if not la_bien and not toan_viet:
                            tot = ("sai-chinh-ta", a, b, dung_chu)     # vd "Thrive" -> dạng viết của từ vựng
                        elif not la_bien:
                            if pmin >= 0.75:
                                continue    # chữ tiếng Việt trùng mặt chữ với từ vựng (vd "ai"), nghe chắc: bỏ qua
                            tot = ("gan", a, b, dung_chu, 1.0)
                        else:
                            tot = ("bien", a, b, dung_chu)
                        if tot[0] != "gan":
                            break
                        continue
                    if len(nf) >= 5 and abs(len(nf) - len(n)) <= 2 and nf[0] == n[0]:
                        r = difflib.SequenceMatcher(None, n, nf).ratio()
                        if r >= 0.8 and (not la_bien or so_am > 1 or pmin < 0.75):
                            tot = tot or ("gan", a, b, dung_chu, r)
                if tot and tot[0] in ("dung", "sai-chinh-ta", "bien"):
                    break
            if not tot or tot[0] == "dung":
                if tot:
                    dung.update(range(tot[1], tot[2] + 1))
                continue
            loai, a_, b_, dung_chu = tot[:4]
            if loai == "sai-chinh-ta":
                cho.append(_cho(k, "tu-vung", gb, i, a_, b_, f"đúng chính tả theo từ vựng: {dung_chu}", 3,
                                [dung_chu], tu_sua=True))
            elif loai == "bien":
                cho.append(_cho(k, "tu-vung", gb, i, a_, b_, f"thường bị nghe nhầm từ: {dung_chu}", 1, [dung_chu]))
            else:
                cho.append(_cho(k, "tu-vung", gb, i, a_, b_, f"gần giống từ vựng: {dung_chu}", 2, [dung_chu]))
            dung.update(range(a_, b_ + 1))
    # 3. tên riêng lạ (chữ hoa giữa câu, chưa có trong từ vựng) và từ nước ngoài
    biet = {x["chu"] for x in tv} | TEN_QUEN
    biet_chuan = {chuan(x) for x in biet}
    for i, d in enumerate(doan):
        cs = d["chu"]
        j = 0
        while j < len(cs):
            w = tron(cs[j]["w"])
            dau_cau = j == 0 or re.search(r"[.!?…:]\s*$", cs[j - 1]["w"].strip()) is not None
            if w and w[0].isupper() and not dau_cau and (not viet or not la_tieng_ngoai(w)) and \
                    (viet or w not in ("I", "I'm", "I've", "I'll", "I'd")):
                b = j
                while b + 1 < len(cs) and tron(cs[b + 1]["w"])[:1].isupper() and not re.search(r"[.!?,:;]$", cs[b]["w"]):
                    b += 1
                ten = " ".join(tron(c["w"]) for c in cs[j:b + 1])
                if ten not in biet and chuan(ten) not in biet_chuan:
                    cho.append(_cho(k, "ten-rieng", gb, i, j, b, "tên riêng, cần đúng chính tả", 2))
                j = b + 1
                continue
            if viet and la_tieng_ngoai(w):
                b = j
                while b + 1 < len(cs) and la_tieng_ngoai(cs[b + 1]["w"]) and not re.search(r"[.!?,:;]$", cs[b]["w"]):
                    b += 1
                cum = " ".join(tron(c["w"]) for c in cs[j:b + 1])
                if cum not in biet and chuan(cum) not in biet_chuan:
                    cho.append(_cho(k, "tieng-ngoai", gb, i, j, b, "từ nước ngoài hoặc viết tắt, cần đúng chính tả", 2))
                j = b + 1
                continue
            j += 1
    # 4. câu nghe ảo, lặp lời, quãng dài không có lời
    for i, d in enumerate(doan):
        t = chuan(d.get("text", ""))
        ly = None
        if any(chuan(c) in t for c in CAU_NGHE_AO) and len(t) < 90:
            ly = "câu hay bị máy nghe ảo ở quãng lặng"
        elif (d.get("nen") or 0) > 2.4:
            ly = "câu lặp lời bất thường"
        elif (d.get("imLang") or 0) > 0.6 and (d.get("logprob") or 0) < -1:
            ly = "máy đoán đây là quãng lặng"
        elif i >= 2 and t and t == chuan(doan[i - 1].get("text", "")) == chuan(doan[i - 2].get("text", "")):
            ly = "cùng một câu lặp ba lần liền"
        if ly and d["chu"]:
            cho.append(_cho(k, "nghe-ao", gb, i, 0, len(d["chu"]) - 1, ly, 1, ["-"]))
        if i + 1 < len(doan):
            ho = (doan[i + 1].get("start") or 0) - (d.get("end") or 0)
            if ho >= NGUONG_KHOANG_TRONG and d["chu"]:
                cho.append(_cho(k, "khoang-trong", gb, i, len(d["chu"]) - 1, len(d["chu"]) - 1,
                                f"{ho:.0f} giây không có lời: im lặng thật hay máy bỏ sót?", 3, chen=True))
    return cho


def gop_cho(cho, ban):
    """Gộp chỗ trùng hoặc chồng lên nhau trong cùng câu; gộp các lần xuất hiện của cùng một tên riêng, từ vựng."""
    cho.sort(key=lambda c: (c["tep"], c["noi"][0]["d"], c["noi"][0]["a"], -c["noi"][0]["b"]))
    ra = []
    for c in cho:
        n = c["noi"][0]
        x = ra[-1] if ra else None
        if x and not n.get("chen") and not x["noi"][0].get("chen") and x["tep"] == c["tep"] and \
                x["noi"][0]["d"] == n["d"] and n["a"] <= x["noi"][0]["b"]:
            x["noi"][0]["b"] = max(x["noi"][0]["b"], n["b"])
            x["lyDo"] += [l for l in c["lyDo"] if l not in x["lyDo"]]
            x["deXuat"] += [d for d in c["deXuat"] if d not in x["deXuat"]]
            if c["loai"] != "khong-chac":
                x["loai"] = c["loai"] if x["loai"] == "khong-chac" else x["loai"]
            x["muc"] = min(x["muc"], c["muc"])
            x["tuSua"] = x["tuSua"] and c["tuSua"]
            continue
        ra.append(c)
    theo_chu, cuoi = {}, []
    for c in ra:
        n = c["noi"][0]
        c["_chu"] = van_noi(n["d"], n["a"], n["b"], ban[c["tep"]][1]) if not n.get("chen") else ""
        if c["loai"] in ("ten-rieng", "tieng-ngoai", "tu-vung"):
            kh = (c["tep"], c["loai"], c["_chu"])
            if kh in theo_chu:
                theo_chu[kh]["noi"] += c["noi"]
                theo_chu[kh]["muc"] = min(theo_chu[kh]["muc"], c["muc"])
                continue
            theo_chu[kh] = c
        cuoi.append(c)
    return cuoi


def danh_so(cho, ban):
    for k, c in enumerate(cho, 1):
        c["id"] = f"c{k:03d}"
    for c in cho:
        dien(c, ban)


def dien(c, ban):
    """Điền chữ máy nghe, mốc, ngữ cảnh của lần xuất hiện đầu."""
    ten, gb = ban[c["tep"]]
    n = c["noi"][0]
    c["tenTep"] = ten
    c["chu"] = van_noi(n["d"], n["a"], n["b"], gb) if not n.get("chen") else ""
    c["bat"], c["het"] = moc_noi(gb, n["d"], n["a"], n["b"])
    if n.get("chen"):
        c["bat"] = gb["doan"][n["d"]].get("end")
        c["het"] = gb["doan"][n["d"] + 1].get("start") if n["d"] + 1 < len(gb["doan"]) else c["bat"]
    phang = chu_phang(gb)
    c["truoc"], c["sau"] = ngu_canh(gb, phang, n["d"], n["a"], n["b"])
    c["soLan"] = len(c["noi"])
    c.pop("_chu", None)


def soat(du_an, lai=False):
    du_an = tim_du_an(du_an)
    p = os.path.join(du_an, "soat", "cho-can-hoi.json")
    if os.path.isfile(p) and not lai:
        sys.exit("Đã có soat/cho-can-hoi.json (có thể kèm chỗ Claude thêm, câu trả lời của bạn). "
                 "Rà lại từ đầu thì thêm --lai.")
    ban = nap_ban(du_an)
    if not ban:
        sys.exit("Chưa có bản gỡ băng nào trong tho/: xếp việc (go_bang.py xep) và chạy trên máy thật trước.")
    tv = tu_vung(du_an)
    cho = []
    nn = thong_tin(du_an).get("ngonNgu", "vi")
    for k, (ten, gb) in enumerate(ban):
        cho += ra_soat_tep(k, gb, tv, nn)
    cho = gop_cho(cho, ban)
    danh_so(cho, ban)
    ghi_json(p, {"capNhat": bay_gio(), "tuVung": len(tv), "cho": cho})
    if lai and os.path.isfile(os.path.join(du_an, "soat", "tra-loi.json")):
        os.replace(os.path.join(du_an, "soat", "tra-loi.json"), os.path.join(du_an, "soat", "tra-loi.cu.json"))
    dem = {}
    for c in cho:
        dem[c["loai"]] = dem.get(c["loai"], 0) + 1
    tong_chu = sum(len(d["chu"]) for _, gb in ban for d in gb["doan"])
    print(f"Máy rà {len(ban)} tệp, {tong_chu} chữ: {len(cho)} chỗ "
          + ", ".join(f"{TEN_LOAI[k]} {v}" for k, v in sorted(dem.items())))
    print("Tiếp: đọc bản nháp (go_bang.py doc) để bỏ chỗ báo nhầm, thêm chỗ nghe sai nghĩa, rồi go_bang.py hoi.")
    return cho


# ----------------------------------------------------------------------------- Claude soát theo ngữ cảnh
def nap_soat(du_an):
    p = os.path.join(du_an, "soat", "cho-can-hoi.json")
    s = doc_json(p)
    if not s:
        sys.exit("Chưa rà: chạy go_bang.py soat trước.")
    return p, s


def doc_ban(du_an, tep=0, tu=0.0, den=None):
    du_an = tim_du_an(du_an)
    ban = nap_ban(du_an)
    if not ban:
        sys.exit("Chưa có bản gỡ băng.")
    ten, gb = ban[tep]
    s = doc_json(os.path.join(du_an, "soat", "cho-can-hoi.json"), {"cho": []})
    dau = {}
    for c in s["cho"]:
        if c["tep"] != tep or c.get("bo"):
            continue
        for n in c["noi"]:
            dau.setdefault((n["d"], n["a"]), []).append((c["id"], n["b"], n.get("chen")))
    print(f"# {ten}  ({moc(gb.get('thoiLuong') or 0)}; ⟨chữ⟩ máy nghe không chắc, ⟦c001: chữ⟧ chỗ đã ghi để hỏi)")
    for i, d in enumerate(gb["doan"]):
        if (d.get("end") or 0) < tu * 60 or (den is not None and (d.get("start") or 0) > den * 60):
            continue
        out, j = [], 0
        cs = d["chu"]
        while j < len(cs):
            if (i, j) in dau:
                ma, b, chen = dau[(i, j)][0]
                if chen:
                    out.append(cs[j]["w"] + f" ⟦{ma}: quãng trống⟧")
                    j += 1
                    continue
                out.append(" ⟦" + ma + ":" + "".join(c["w"] for c in cs[j:b + 1]) + "⟧")
                j = b + 1
                continue
            w = cs[j]["w"]
            p = cs[j].get("p")
            out.append(f" ⟨{w.strip()}⟩" if p is not None and p < 0.6 else w)
            j += 1
        print(f"[{moc(d.get('start'))}] " + "".join(out).strip())


def tim_noi(gb, chu, quanh=None, cua_so=8.0):
    """Mọi lần xuất hiện của cụm chữ (so lỏng theo chữ thường, bỏ dấu câu) trong bản; quanh: chỉ lấy gần mốc đó."""
    muc = [tron(x).lower() for x in chu.split() if tron(x)]
    if not muc:
        return []
    ra = []
    for i, d in enumerate(gb["doan"]):
        cs = [tron(c["w"]).lower() for c in d["chu"]]
        for a in range(len(cs) - len(muc) + 1):
            if cs[a:a + len(muc)] == muc:
                s, e = moc_noi(gb, i, a, a + len(muc) - 1)
                if quanh is None or (s is not None and abs(s - quanh) <= cua_so) or \
                        (s is None and abs((d.get("start") or 0) - quanh) <= cua_so + 15):
                    ra.append({"d": i, "a": a, "b": a + len(muc) - 1})
    if quanh is not None and ra:
        ra.sort(key=lambda n: abs((moc_noi(gb, n["d"], n["a"], n["b"])[0] or gb["doan"][n["d"]].get("start") or 0) - quanh))
        ra = ra[:1]
    return ra


def them_cho(du_an, chu, moc_giay=None, de_xuat=(), ly_do=None, tu_sua=False, moi_noi=False, tep=0):
    du_an = tim_du_an(du_an)
    p, s = nap_soat(du_an)
    ban = nap_ban(du_an)
    gb = ban[tep][1]
    noi = tim_noi(gb, chu, None if moi_noi else moc_giay)
    if not noi:
        sys.exit(f'Không thấy "{chu}"' + (f" quanh {moc(moc_giay)}" if moc_giay is not None and not moi_noi else ""))
    so_cu = max([int(c["id"][1:]) for c in s["cho"]] + [0])
    c = {"id": f"c{so_cu + 1:03d}", "tep": tep, "loai": "ngu-canh", "noi": noi,
         "lyDo": [ly_do or "nghe sai theo ngữ cảnh"], "muc": 3 if tu_sua else 1, "deXuat": list(de_xuat),
         "tuSua": bool(tu_sua), "tu": "Claude"}
    dien(c, ban)
    s["cho"].append(c)
    s["capNhat"] = bay_gio()
    ghi_json(p, s)
    print(f'{c["id"]}: "{c["chu"]}" ({c["soLan"]} chỗ, đầu tiên ở {moc(c["bat"])})'
          + (f' -> {", ".join(de_xuat)}' if de_xuat else "") + (" [tự sửa]" if tu_sua else ""))
    return c


def bo_cho(du_an, ids, bo=True):
    du_an = tim_du_an(du_an)
    p, s = nap_soat(du_an)
    co = {c["id"]: c for c in s["cho"]}
    for i in ids:
        if i not in co:
            sys.exit(f"Không có {i}")
        co[i]["bo"] = bo
    ghi_json(p, s)
    print(("Bỏ " if bo else "Khôi phục ") + ", ".join(ids))


def dat_de_xuat(du_an, ma, de_xuat, tu_sua=None):
    du_an = tim_du_an(du_an)
    p, s = nap_soat(du_an)
    c = next((x for x in s["cho"] if x["id"] == ma), None)
    if not c:
        sys.exit(f"Không có {ma}")
    c["deXuat"] = list(de_xuat)
    if tu_sua is not None:
        c["tuSua"] = tu_sua
        c["muc"] = 3 if tu_sua else min(c["muc"], 2)
    ghi_json(p, s)
    print(f'{ma}: "{c["chu"]}" -> {", ".join(de_xuat) or "(không đề xuất)"}' + (" [tự sửa]" if c["tuSua"] else ""))


# ----------------------------------------------------------------------------- hỏi bạn
def tra_loi_da_co(du_an):
    return (doc_json(os.path.join(du_an, "soat", "tra-loi.json"), {}) or {}).get("traLoi", {})


def hoi(du_an, toi_da=30, in_ra=True):
    du_an = tim_du_an(du_an)
    p, s = nap_soat(du_an)
    tl = tra_loi_da_co(du_an)
    so_max = max([c.get("so") or 0 for c in s["cho"]] + [0])
    con = [c for c in s["cho"] if not c.get("bo") and not c.get("tuSua") and c["id"] not in tl]
    con.sort(key=lambda c: (c["muc"], c["tep"], c.get("bat") or 0))      # quan trọng trước
    hien = sorted(con[:toi_da], key=lambda c: (c["tep"], c.get("bat") or 0))   # hiện theo thứ tự thời gian
    for c in hien:                      # đánh số theo thứ tự hiện, giữ số cũ để câu trả lời trước vẫn đúng chỗ
        if not c.get("so"):
            so_max += 1
            c["so"] = so_max
    hien.sort(key=lambda c: c["so"])
    ghi_json(p, s)
    nhieu_tep = len({c["tep"] for c in s["cho"]}) > 1
    dong = []
    for c in hien:
        chu = c["chu"] or "(quãng trống)"
        cau = f"…{c['truoc']} **{chu}** {c['sau']}…".replace("  ", " ")
        dx = " / ".join("xóa câu này" if d == "-" else d for d in c["deXuat"])
        them_ = f" ({c['soLan']} chỗ)" if c.get("soLan", 1) > 1 else ""
        tep = f"{c['tenTep']} " if nhieu_tep else ""
        if not c["chu"]:
            dong.append(f"{c['so']}. [{tep}{moc(c['bat'])}] {cau}\n   {'; '.join(c['lyDo'])}")
            continue
        dong.append(f"{c['so']}. [{tep}{moc(c['bat'])}] {cau}{them_}\n   máy nghe: \"{chu}\""
                    + (f"; đề xuất: **{dx}**" if dx else "") + f" ({'; '.join(c['lyDo'])})")
    tu_sua = [c for c in s["cho"] if c.get("tuSua") and not c.get("bo") and c["id"] not in tl]
    ts = [f"- \"{c['chu']}\" -> \"{c['deXuat'][0]}\" ({c.get('soLan', 1)} chỗ)" for c in tu_sua if c["deXuat"]]
    md = ["# Chỗ cần bạn xác nhận", ""]
    md += dong or ["(Không còn chỗ nào cần hỏi.)"]
    if len(con) > len(hien):
        md += ["", f"Còn {len(con) - len(hien)} chỗ ít quan trọng hơn: bạn nghe ở Bàn soát, "
                   "hoặc để tôi lấy đề xuất của máy cho các chỗ đó."]
    if ts:
        md += ["", "# Tôi tự chuẩn chính tả (bạn xem lướt)", ""] + ts
    md += ["", "Cách trả lời: `3 ok` (giữ như máy nghe), `3 +` (lấy đề xuất), `3 -` (xóa), `3 ?` (không rõ), "
               "hoặc `3 chữ đúng`."]
    van = "\n".join(md) + "\n"
    ghi_chu(os.path.join(du_an, "soat", "HOI.md"), van)
    if in_ra:
        print(van)
    return hien


def ghi_tra_loi(du_an, cap, nguon="chat", con_lai=None):
    """cap: ["3=+", "c012=chữ", "5=ok"]; con_lai: 'de-xuat' | 'giu' cho mọi chỗ chưa trả lời."""
    du_an = tim_du_an(du_an)
    p, s = nap_soat(du_an)
    theo_so = {str(c.get("so")): c for c in s["cho"] if c.get("so")}
    theo_id = {c["id"]: c for c in s["cho"]}
    pt = os.path.join(du_an, "soat", "tra-loi.json")
    tl = (doc_json(pt, {}) or {}).get("traLoi", {})
    for x in cap:
        k, sep, v = x.partition("=")
        if not sep:
            m = re.match(r"^\s*(c?\d+)\s+(.+)$", x)
            if not m:
                sys.exit(f"Không hiểu câu trả lời: {x}")
            k, v = m.groups()
        k, v = k.strip(), v.strip()
        c = theo_id.get(k) if k.startswith("c") else theo_so.get(k)
        if not c:
            sys.exit(f"Không có chỗ số {k}")
        tl[c["id"]] = dich_tra_loi(c, v) | {"nguon": nguon, "luc": bay_gio()}
    if con_lai:
        for c in s["cho"]:
            if c.get("bo") or c.get("tuSua") or c["id"] in tl:
                continue
            if con_lai == "de-xuat" and c["deXuat"]:
                tl[c["id"]] = dich_tra_loi(c, "+") | {"nguon": "đề xuất (bạn cho phép)", "luc": bay_gio()}
            elif not c.get("tuSua"):
                tl[c["id"]] = {"kieu": "giu", "nguon": "giữ như máy nghe (bạn cho phép)", "luc": bay_gio()}
    ghi_json(pt, {"capNhat": bay_gio(), "traLoi": tl})
    con = [c for c in s["cho"] if not c.get("bo") and not c.get("tuSua") and c["id"] not in tl]
    print(f"Đã ghi {len(tl)} câu trả lời; còn {len(con)} chỗ chưa trả lời.")
    return tl


def dich_tra_loi(c, v):
    if v.lower() in ("ok", "=", "đúng", "dung", "giu", "giữ"):
        return {"kieu": "giu"}
    if v in ("-", "xóa", "xoá", "xoa"):
        return {"kieu": "xoa"}
    if v in ("?", "không rõ", "khong ro"):
        return {"kieu": "khong-ro"}
    m = re.match(r"^\+(\d*)$", v)
    if m:
        k = int(m.group(1) or 1) - 1
        if k >= len(c["deXuat"]):
            sys.exit(f"{c['id']} không có đề xuất thứ {k + 1}")
        d = c["deXuat"][k]
        return {"kieu": "xoa"} if d == "-" else {"kieu": "sua", "chu": d}
    return {"kieu": "sua", "chu": v.strip().strip('"“”')}


# ----------------------------------------------------------------------------- xuất
def thay_noi(gb, n, moi_chu):
    """Thay chữ ở một chỗ, giữ khoảng trắng đầu, dấu câu bao quanh và mốc thời gian."""
    cs = gb["doan"][n["d"]]["chu"]
    if n.get("chen"):
        if moi_chu:
            cs[n["a"]]["w"] = cs[n["a"]]["w"].rstrip() + " " + moi_chu
        return
    dau_w, cuoi_w = cs[n["a"]]["w"], cs[n["b"]]["w"]
    trang = re.match(r"^\s*", dau_w).group(0)
    m_dau = re.match(r"^\s*([\W_]*)", dau_w)
    m_cuoi = re.search(r"([\W_]*)\s*$", cuoi_w)
    tien = m_dau.group(1) if m_dau and tron(dau_w) else ""
    hau = m_cuoi.group(1) if m_cuoi and tron(cuoi_w) else ""
    if not moi_chu:
        moi_w = (tien + hau).strip()
        k = n["a"] - 1
        while k >= 0 and not cs[k]["w"].strip():        # bỏ qua chữ đã bị thay trống ở chỗ sửa trước
            k -= 1
        if moi_w and k >= 0:
            truoc = cs[k]["w"].rstrip()
            if re.search(r"[.!?…]", moi_w):            # dấu hết câu thay dấu phẩy đang treo
                truoc = re.sub(r"[,;:]+$", "", truoc)
            cs[k]["w"] = truoc + moi_w.strip()
        moi_w = ""
    else:
        if hau and re.search(r"[.!?,:;…]$", moi_chu):
            hau = ""
        moi_w = trang + tien + moi_chu + hau
    cs[n["a"]]["w"] = moi_w
    for c in cs[n["a"] + 1:n["b"] + 1]:
        c["w"] = ""


def ap_sua(du_an, con_lai=None, khong_ro="[không rõ]"):
    p, s = nap_soat(du_an)
    tl = tra_loi_da_co(du_an)
    ban = nap_ban(du_an)
    chua = [c for c in s["cho"] if not c.get("bo") and not c.get("tuSua") and c["id"] not in tl]
    if chua and not con_lai:
        sys.exit(f"Còn {len(chua)} chỗ chưa có câu trả lời ({', '.join(str(c.get('so') or c['id']) for c in chua[:12])}"
                 f"{'...' if len(chua) > 12 else ''}). Hỏi bạn tiếp, hoặc bạn cho phép thì thêm --con-lai de-xuat|giu.")
    nhat_ky = {"anhXacNhan": 0, "tuSua": 0, "deXuat": 0, "giuMay": 0, "khongRo": 0, "xoa": 0}
    for c in s["cho"]:
        if c.get("bo"):
            continue
        t = tl.get(c["id"])
        if t:
            if "bạn cho phép" not in t.get("nguon", ""):
                nhat_ky["anhXacNhan"] += 1
            else:
                nhat_ky["giuMay" if t["kieu"] == "giu" else "deXuat"] += 1
        elif c.get("tuSua") and c["deXuat"]:
            t = {"kieu": "sua", "chu": c["deXuat"][0]}
            nhat_ky["tuSua"] += 1
        elif con_lai == "de-xuat" and c["deXuat"]:
            t = dich_tra_loi(c, "+")
            nhat_ky["deXuat"] += 1
        else:
            continue
        gb = ban[c["tep"]][1]
        for n in c["noi"]:
            if t["kieu"] == "sua":
                thay_noi(gb, n, t["chu"])
            elif t["kieu"] == "xoa":
                thay_noi(gb, n, "")
                nhat_ky["xoa"] += 1
            elif t["kieu"] == "khong-ro":
                if n.get("chen"):
                    thay_noi(gb, n, khong_ro)
                else:
                    thay_noi(gb, n, khong_ro.rstrip("]") + ": " + van_noi(n["d"], n["a"], n["b"], gb) + "]")
                nhat_ky["khongRo"] += 1
    for _, gb in ban:
        for d in gb["doan"]:
            d["text"] = re.sub(r"\s+", " ", "".join(c["w"] for c in d["chu"])).strip()
            d["text"] = re.sub(r"\s+([,.!?;:…])", r"\1", d["text"])
        gb["doan"] = [d for d in gb["doan"] if d["text"]]
    return ban, nhat_ky, tl, s


def doan_van(gb):
    """Gom câu thành đoạn văn theo quãng ngừng và độ dài."""
    ra, cur = [], None
    for k, d in enumerate(gb["doan"]):
        ho = (d.get("start") or 0) - (gb["doan"][k - 1].get("end") or 0) if k else 0
        dai = len(cur["text"]) if cur else 0
        het_cau = bool(cur) and re.search(r"[.!?…]$", cur["text"]) is not None
        if cur is None or ho >= 2.5 or (ho >= 1.2 and dai >= 250) or (dai >= 1100 and het_cau):
            cur = {"start": d.get("start"), "text": d["text"]}
            ra.append(cur)
        else:
            cur["text"] += " " + d["text"]
    for p in ra:
        p["text"] = p["text"][:1].upper() + p["text"][1:]
    return ra


def cau_srt(gb, toi_da_giay=7.0, toi_da_chu=84):
    """Câu phụ đề: tách câu dài theo chữ (dùng mốc từng chữ khi có)."""
    ra = []
    for d in gb["doan"]:
        cs = [c for c in d["chu"] if c["w"].strip()]
        if len(d["text"]) <= toi_da_chu and (d.get("end") or 0) - (d.get("start") or 0) <= toi_da_giay or \
                not cs or any(c.get("s") is None for c in cs):
            ra.append((d.get("start"), d.get("end"), d["text"]))
            continue
        cur = []
        for c in cs:
            cur.append(c)
            van = "".join(x["w"] for x in cur).strip()
            if len(van) >= toi_da_chu * 0.8 or (c["e"] - cur[0]["s"]) >= toi_da_giay or re.search(r"[.!?,;:]$", van) \
                    and len(van) > 30:
                ra.append((cur[0]["s"], c["e"], van))
                cur = []
        if cur:
            ra.append((cur[0]["s"], cur[-1]["e"], "".join(x["w"] for x in cur).strip()))
    ra = [(s, e, re.sub(r"\s+([,.!?;:…])", r"\1", t)) for s, e, t in ra if t]
    for k in range(len(ra) - 1):        # không cho hai câu phụ đề chồng nhau
        s, e, t = ra[k]
        if e is not None and ra[k + 1][0] is not None and e > ra[k + 1][0]:
            ra[k] = (s, max(s or 0, ra[k + 1][0] - 0.02), t)
    return ra


def hoc_tu_vung(du_an, s, tl):
    """Chữ đúng bạn xác nhận cho tên riêng, từ nước ngoài, từ vựng: ghi vào từ vựng của xưởng kèm cách máy nghe nhầm."""
    muc_ra = doc_json(TU_VUNG_XUONG, None) or {
        "_huong-dan": "Từ vựng ĐỀ XUẤT cho máy gỡ băng: tên riêng, thuật ngữ, từ nước ngoài bạn đã xác nhận chính tả "
                      "khi soát (tools/go_bang.py xuat tự ghi), kèm các cách máy từng nghe nhầm (bienThe) để lần sau máy "
                      "rà nhận ra. Mục nào muốn dùng chung cho các xưởng thì chuyển sang ngon-ngu/tu-vung.json của kho "
                      "tư liệu (bản kho đè bản này).", "muc": {}}
    hoc = []
    ten_da = os.path.basename(du_an)
    for c in s["cho"]:
        t = tl.get(c["id"])
        if c.get("bo") or not t or "bạn cho phép" in t.get("nguon", "") or \
                c["loai"] not in ("ten-rieng", "tieng-ngoai", "tu-vung"):
            continue
        dung = t.get("chu") if t["kieu"] == "sua" else (c["chu"] if t["kieu"] == "giu" else None)
        if not dung or len(dung) > 60 or (dung.islower() and all(la_am_tiet_viet(x) for x in dung.split())):
            continue
        x = muc_ra["muc"].setdefault(dung, {"bienThe": [], "nguon": []})
        if c["chu"] and c["chu"] != dung and c["chu"] not in x["bienThe"]:
            x["bienThe"].append(c["chu"])
        if ten_da not in x["nguon"]:
            x["nguon"].append(ten_da)
        x["capNhat"] = dt.date.today().isoformat()
        hoc.append(dung)
    if hoc:
        ghi_json(TU_VUNG_XUONG, muc_ra)
    return sorted(set(hoc))


def xuat(du_an, con_lai=None):
    du_an = tim_du_an(du_an)
    tt = thong_tin(du_an)
    ban, nk, tl, s = ap_sua(du_an, con_lai)
    d_ra = os.path.join(du_an, "thanh-pham")
    os.makedirs(d_ra, exist_ok=True)
    tep_ra = []
    for ten, gb in ban:
        goc = slug(os.path.splitext(ten)[0])
        tl_giay = gb.get("thoiLuong") or (gb["doan"][-1]["end"] if gb["doan"] else 0)
        gio = tl_giay >= 3600
        doan = doan_van(gb)
        tieu = tt.get("tieuDe") or ten
        if len(ban) > 1:
            tieu += f" - {os.path.splitext(ten)[0]}"
        ghi = [f"# {tieu}", "",
               f"- Nguồn: {ten} ({moc(tl_giay, gio)})",
               f"- Gỡ băng: Whisper large-v3-turbo chạy tại máy, {(gb.get('luc') or bay_gio())[:10]}",
               f"- Soát: bạn xác nhận {nk['anhXacNhan']} chỗ; tôi chuẩn chính tả {nk['tuSua']} chỗ"
               + (f"; lấy đề xuất {nk['deXuat']} chỗ" if nk["deXuat"] else "")
               + (f"; giữ như máy nghe {nk['giuMay']} chỗ" if nk["giuMay"] else "")
               + (f"; còn {nk['khongRo']} chỗ ghi [không rõ]" if nk["khongRo"] else ""), ""]
        for p in doan:
            ghi += [f"**[{moc(p['start'], gio)}]** {p['text']}", ""]
        ghi_chu(os.path.join(d_ra, goc + ".md"), "\n".join(ghi))
        ghi_chu(os.path.join(d_ra, goc + ".txt"), "\n\n".join(p["text"] for p in doan) + "\n")
        srt = [f"{k}\n{moc_srt(a)} --> {moc_srt(b)}\n{t}\n" for k, (a, b, t) in enumerate(cau_srt(gb), 1)]
        ghi_chu(os.path.join(d_ra, goc + ".srt"), "\n".join(srt))
        ghi_json(os.path.join(d_ra, goc + ".json"), {
            "tieuDe": tieu, "nguon": ten, "thoiLuong": tl_giay, "moHinh": gb.get("moHinh"), "goBangLuc": gb.get("luc"),
            "xuatLuc": bay_gio(), "soat": nk,
            "doan": [{"start": d.get("start"), "end": d.get("end"), "text": d["text"],
                      "chu": [{"w": c["w"], "s": c.get("s"), "e": c.get("e")} for c in d["chu"] if c["w"]]}
                     for d in gb["doan"]]})
        tep_ra += [goc + x for x in (".md", ".txt", ".srt", ".json")]
    hoc = hoc_tu_vung(du_an, s, tl)
    print("Đã xuất vào", d_ra + ":", ", ".join(tep_ra))
    print(f"Soát: bạn xác nhận {nk['anhXacNhan']}, tự chuẩn chính tả {nk['tuSua']}, lấy đề xuất {nk['deXuat']}, "
          f"không rõ {nk['khongRo']}, xóa {nk['xoa']} chỗ.")
    if hoc:
        print("Học thêm từ vựng (du-lieu/tu-vung-de-xuat.json):", ", ".join(hoc))
    return [os.path.join(d_ra, x) for x in tep_ra]


# ----------------------------------------------------------------------------- trạng thái
def trang_thai(du_an):
    du_an = tim_du_an(du_an)
    tt = thong_tin(du_an)
    print(f"{os.path.basename(du_an)}: {tt.get('tieuDe')}")
    for t in tep_nguon(du_an):
        gb, nghe = duong_tho(du_an, t)
        x = doc_json(gb)
        print(f"  {t}: " + (f"đã gỡ băng ({moc(x.get('thoiLuong') or 0)}, {len(x.get('doan', []))} câu)" if x
                            else "chưa gỡ băng") + (", có tệp nghe" if os.path.isfile(nghe) else ""))
    s = doc_json(os.path.join(du_an, "soat", "cho-can-hoi.json"))
    if s:
        tl = tra_loi_da_co(du_an)
        song = [c for c in s["cho"] if not c.get("bo")]
        hoi_ = [c for c in song if not c.get("tuSua")]
        print(f"  soát: {len(song)} chỗ ({len(hoi_)} cần hỏi, {len(song) - len(hoi_)} tự sửa, "
              f"{len(s['cho']) - len(song)} đã bỏ); bạn đã trả lời {len([c for c in hoi_ if c['id'] in tl])}")
    d = os.path.join(du_an, "thanh-pham")
    if os.path.isdir(d) and os.listdir(d):
        print("  thành phẩm:", ", ".join(sorted(os.listdir(d))))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="lenh", required=True)
    a = sp.add_parser("moi")
    a.add_argument("ten")
    a.add_argument("tep", nargs="*")
    a.add_argument("--tieu-de")
    a.add_argument("--ngon-ngu", default="vi")
    a.add_argument("--tu", help="tên riêng, thuật ngữ của bản ghi, cách nhau bằng dấu phẩy")
    a.add_argument("--boi-canh", help="một câu: buổi gì, ai nói, chủ đề")
    for ten in ("xep", "trang-thai"):
        sp.add_parser(ten).add_argument("du_an")
    a = sp.add_parser("soat")
    a.add_argument("du_an")
    a.add_argument("--lai", action="store_true")
    a = sp.add_parser("doc")
    a.add_argument("du_an")
    a.add_argument("--tep", type=int, default=0)
    a.add_argument("--tu", type=float, default=0, help="từ phút")
    a.add_argument("--den", type=float, help="đến phút")
    a = sp.add_parser("them-cho")
    a.add_argument("du_an")
    a.add_argument("--chu", required=True)
    a.add_argument("--moc", type=float, help="giây, gần chỗ đó")
    a.add_argument("--de-xuat", action="append", default=[])
    a.add_argument("--ly-do")
    a.add_argument("--tu-sua", action="store_true", help="lỗi chính tả chắc chắn: sửa, không hỏi")
    a.add_argument("--moi-noi", action="store_true", help="mọi lần xuất hiện trong bản")
    a.add_argument("--tep", type=int, default=0)
    a = sp.add_parser("bo-cho")
    a.add_argument("du_an")
    a.add_argument("ids", nargs="+")
    a.add_argument("--khoi-phuc", action="store_true")
    a = sp.add_parser("de-xuat")
    a.add_argument("du_an")
    a.add_argument("ma")
    a.add_argument("chu", nargs="*")
    a.add_argument("--tu-sua", action="store_true")
    a.add_argument("--hoi", action="store_true", help="bỏ tự sửa, đưa vào danh sách hỏi")
    a = sp.add_parser("hoi")
    a.add_argument("du_an")
    a.add_argument("--toi-da", type=int, default=30)
    a = sp.add_parser("tra-loi")
    a.add_argument("du_an")
    a.add_argument("cap", nargs="*", help='3=+  5=ok  7=-  8=?  c012="chữ đúng"')
    a.add_argument("--con-lai", choices=["de-xuat", "giu"])
    a = sp.add_parser("xuat")
    a.add_argument("du_an")
    a.add_argument("--con-lai", choices=["de-xuat", "giu"])
    a = ap.parse_args()
    if a.lenh == "moi":
        moi(a.ten, a.tep, a.tieu_de, a.ngon_ngu, a.tu, a.boi_canh)
    elif a.lenh == "xep":
        xep(a.du_an)
    elif a.lenh == "soat":
        soat(a.du_an, a.lai)
    elif a.lenh == "doc":
        doc_ban(a.du_an, a.tep, a.tu, a.den)
    elif a.lenh == "them-cho":
        them_cho(a.du_an, a.chu, a.moc, a.de_xuat, a.ly_do, a.tu_sua, a.moi_noi, a.tep)
    elif a.lenh == "bo-cho":
        bo_cho(a.du_an, a.ids, not a.khoi_phuc)
    elif a.lenh == "de-xuat":
        dat_de_xuat(a.du_an, a.ma, a.chu, True if a.tu_sua else (False if a.hoi else None))
    elif a.lenh == "hoi":
        hoi(a.du_an, a.toi_da)
    elif a.lenh == "tra-loi":
        ghi_tra_loi(a.du_an, a.cap, con_lai=a.con_lai)
    elif a.lenh == "xuat":
        xuat(a.du_an, a.con_lai)
    elif a.lenh == "trang-thai":
        trang_thai(a.du_an)


if __name__ == "__main__":
    main()
