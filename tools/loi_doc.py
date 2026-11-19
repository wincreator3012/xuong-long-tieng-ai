# -*- coding: utf-8 -*-
"""LỜI ĐỌC: đọc kịch bản lồng tiếng (loi-doc.md) thành các đoạn, rồi dịch mỗi đoạn sang lời riêng cho từng máy đọc.

Kịch bản là một tệp markdown người đọc được:

    ---
    tieuDe: Giới thiệu khóa học
    ngonNgu: vi                  # vi | en
    may: gemini                  # máy đọc mặc định (khóa trong may-doc.json)
    giong: Charon                # giọng có sẵn của máy đó, hoặc @an (giọng riêng trong kho)
    soLuot: 2                    # số lượt đọc mỗi đoạn để chọn
    phongCach: ấm áp, chậm rãi | warm, unhurried, gentle
    nghiGiuaDoan: 0.6            # giây lặng giữa hai đoạn
    ---

    # Mở đầu                     (tiêu đề mục: không đọc, chèn quãng lặng dài hơn)

    > trìu mến | tender, close    (chỉ dẫn diễn xuất cho đoạn ngay dưới; vế sau dấu | là bản cho máy đọc)
    Chào bạn. {ngừng} Hôm nay mình cùng thực hành {{AI|ây ai}} trong 3 phút. {cười nhẹ}

    {ngừng 1.5}                  (đứng riêng một dòng: thêm 1,5 giây lặng trước đoạn sau)

    Đoạn thứ hai...

Mỗi đoạn văn (cách nhau bằng dòng trống) là một ĐOẠN: đơn vị sinh tiếng, chọn lượt và làm lại.
Mỗi đoạn có hai bản chữ: `chu` (bản viết, dùng cho phụ đề) và `doc` (bản đọc, đã thay phát âm).
Thẻ biểu cảm viết trong ngoặc nhọn {…}; ngoặc vuông […] (chú thích tiếng Anh) bị bỏ khỏi lời đọc và được cảnh báo.

    import loi_doc as L
    kb = L.doc_kich_ban("…/loi-doc.md")        # {"thongTin": {...}, "doan": [...], "canhBao": [...]}
    L.cho_may(doan, "drama3", may_doc_json)    # lời và tham số đã dịch cho máy đọc đó
    L.so_thanh_chu("2026")                      # "hai nghìn không trăm hai mươi sáu"
"""
import json
import os
import re
import unicodedata

# ----------------------------------------------------------------------------- thẻ biểu cảm
# Tên trung tính (tiếng Việt) -> cách viết của từng máy đọc. None = máy đó không có, bỏ thẻ.
# "{ngừng}" và "{ngừng dài}" trong câu là quãng ngắt bên trong đoạn (khác "{ngừng 1.5}" đứng riêng dòng).
THE = {
    "cười": {"gemini": "<laugh>", "elevenlabs": "[laughs]", "drama3": "[laughing]",
             "higgs3": "<|sfx:laughter|>Haha,", "vieneu": "[cười]"},
    "cười nhẹ": {"gemini": "<laugh>", "elevenlabs": "[chuckles]", "drama3": "[chuckle]",
                 "higgs3": "<|sfx:laughter|>Hì,", "vieneu": "[cười]"},
    "thở dài": {"gemini": "<sigh>", "elevenlabs": "[sighs]", "drama3": "[sigh]",
                "higgs3": "<|sfx:sigh|>Haah,", "vieneu": "[thở dài]"},
    "hít thở": {"gemini": "<breath>", "elevenlabs": "[inhales deeply]", "drama3": "[inhale]",
                "higgs3": None, "vieneu": None},
    "hắng giọng": {"gemini": "<throat-clearing>", "elevenlabs": "[clears throat]", "drama3": "[clears throat]",
                   "higgs3": "<|sfx:cough|>E hèm,", "vieneu": "[hắng giọng]"},
    "ngừng": {"gemini": "<short pause>", "elevenlabs": "[pause]", "drama3": "[pause]",
              "higgs3": "<|prosody:pause|>", "vieneu": "…"},
    "ngừng dài": {"gemini": "<long pause>", "elevenlabs": "[long pause]", "drama3": "[long pause]",
                  "higgs3": "<|prosody:long_pause|>", "vieneu": "…"},
}
# Chỉ dẫn diễn xuất (vế tiếng Anh) -> thẻ câu của Higgs v3 (máy này chỉ hiểu danh mục cố định).
HIGGS_TU_KHOA = [
    (r"whisper", "<|style:whispering|>"),
    (r"very slow", "<|prosody:speed_very_slow|>"), (r"slow|unhurried|calm pace", "<|prosody:speed_slow|>"),
    (r"fast|brisk|quick", "<|prosody:speed_fast|>"),
    (r"tender|warm|affection|caring|loving", "<|emotion:affection|>"),
    (r"reflect|contemplat|thoughtful|calm|serene|meditat", "<|emotion:contemplation|>"),
    (r"excit|enthusias|energetic", "<|emotion:enthusiasm|>"), (r"joy|delight|elat|cheer", "<|emotion:elation|>"),
    (r"sad|grief|sorrow", "<|emotion:sadness|>"), (r"proud|pride", "<|emotion:pride|>"),
    (r"relie", "<|emotion:relief|>"), (r"determin|resolute|firm", "<|emotion:determination|>"),
    (r"awe|wonder", "<|emotion:awe|>"), (r"amus|playful|humor", "<|emotion:amusement|>"),
    (r"expressive|lively", "<|prosody:expressive_high|>"), (r"low[- ]key|subdued|soft", "<|prosody:expressive_low|>"),
]

RE_THE = re.compile(r"\{(?!>)([^{}|]+?)\}")                    # {cười}, {ngừng}, {ngừng 1.5}
RE_CD_TRONG = re.compile(r"\{>\s*([^{}]+?)\s*\}")              # {> tò mò | curious}: chỉ dẫn giữa câu
RE_PHAT_AM = re.compile(r"\{\{([^{}|]+)\|([^{}]+)\}\}")      # {{viết|đọc}}
RE_NGUNG_DONG = re.compile(r"^\{\s*ngừng\s+([0-9]+(?:[.,][0-9]+)?)\s*(?:s|giây)?\s*\}$")
RE_CHU_THICH = re.compile(r"\s*\[[^\[\]]*\]")                # [English gloss] trong bản viết


def _ten_the(t):
    """'ngừng 1.5' trong câu -> 'ngừng dài' (từ 1 giây) hoặc 'ngừng'."""
    t = t.strip()
    m = re.fullmatch(r"ngừng\s+([0-9]+(?:[.,][0-9]+)?)\s*(?:s|giây)?", t)
    if m:
        return "ngừng dài" if float(m.group(1).replace(",", ".")) >= 1 else "ngừng"
    return t


def nfc(s):
    return unicodedata.normalize("NFC", s)


# ----------------------------------------------------------------------------- số thành chữ (tiếng Việt)
DON_VI = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
NHOM = ["", "nghìn", "triệu", "tỷ"]


def _ba_so(n, day_du):
    """Đọc một nhóm 0..999. day_du: nhóm không đứng đầu thì đọc đủ 'không trăm', 'linh'."""
    tram, chuc, dv = n // 100, (n // 10) % 10, n % 10
    ra = []
    if tram or day_du:
        ra += [DON_VI[tram], "trăm"]
    if chuc == 0:
        if dv and (tram or day_du):
            ra.append("linh")
    elif chuc == 1:
        ra.append("mười")
    else:
        ra += [DON_VI[chuc], "mươi"]
    if dv:
        if dv == 1 and chuc >= 2:
            ra.append("mốt")
        elif dv == 5 and chuc >= 1:
            ra.append("lăm")
        elif dv == 4 and chuc >= 2:
            ra.append("tư")
        else:
            ra.append(DON_VI[dv])
    return ra


def so_nguyen_thanh_chu(n):
    n = int(n)
    if n == 0:
        return "không"
    if n < 0:
        return "âm " + so_nguyen_thanh_chu(-n)
    nhom = []
    while n:
        nhom.append(n % 1000)
        n //= 1000
    ra = []
    for i in range(len(nhom) - 1, -1, -1):
        if nhom[i] == 0:
            continue
        ra += _ba_so(nhom[i], day_du=bool(ra))
        ten = " ".join(x for x in [NHOM[i % 3]] + ["tỷ"] * (i // 3) if x)
        if ten:
            ra.append(ten)
    return " ".join(ra)


def so_thanh_chu(chuoi):
    """'2026' -> chữ; '3,5' -> 'ba phẩy năm'; '1.200.000' -> 'một triệu hai trăm nghìn'."""
    s = chuoi.strip()
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):            # dấu chấm phân nhóm nghìn kiểu Việt
        return so_nguyen_thanh_chu(s.replace(".", ""))
    m = re.fullmatch(r"(\d+)[,.](\d+)", s)
    if m:
        nguyen, le = m.groups()
        le_doc = " ".join(DON_VI[int(c)] for c in le) if le.startswith("0") or len(le) > 2 \
            else so_nguyen_thanh_chu(le)
        return f"{so_nguyen_thanh_chu(nguyen)} phẩy {le_doc}"
    if re.fullmatch(r"\d+", s):
        if len(s) > 1 and s.startswith("0"):              # số điện thoại, mã: đọc từng chữ số
            return " ".join(DON_VI[int(c)] for c in s)
        return so_nguyen_thanh_chu(s)
    return chuoi


THANG = {str(i): f"tháng {so_nguyen_thanh_chu(i) if i != 4 else 'tư'}" for i in range(1, 13)}
THANG["1"] = "tháng một"
DON_VI_DO = {"%": "phần trăm", "km": "ki lô mét", "kg": "ki lô gam", "cm": "xen ti mét", "m": "mét",
             "h": "giờ", "ph": "phút", "USD": "đô la Mỹ", "đ": "đồng", "VND": "đồng", "GB": "gi ga bai",
             "MB": "mê ga bai", "kHz": "ki lô hét", "Hz": "hét"}


def chuan_hoa_so_vi(s):
    """Đổi ngày, giờ, khoảng, phần trăm, đơn vị và số trong câu tiếng Việt sang chữ."""
    def ngay(m):
        d, th, n = m.group(1), m.group(2), m.group(3)
        ra = f"{'Ngày' if m.group(0).startswith('N') else 'ngày'} {so_nguyen_thanh_chu(d)} {THANG.get(str(int(th)), 'tháng ' + so_nguyen_thanh_chu(th))}"
        return ra + (f" năm {so_nguyen_thanh_chu(n)}" if n else "")
    s = re.sub(r"(?:\b[Nn]gày\s+)?\b(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b", ngay, s)
    s = re.sub(r"\b(\d{1,2})/(\d{4})\b",
               lambda m: f"{THANG.get(str(int(m.group(1))), 'tháng')} năm {so_nguyen_thanh_chu(m.group(2))}", s)
    s = re.sub(r"\b(\d{1,2}):(\d{2})\b", lambda m: f"{so_nguyen_thanh_chu(m.group(1))} giờ"
               + (f" {so_nguyen_thanh_chu(m.group(2))} phút" if int(m.group(2)) else ""), s)
    so = r"\d{1,3}(?:\.\d{3})+(?!\d)|\d+(?:[.,]\d+)?"
    s = re.sub(r"\b(" + so + r")\s*[-–]\s*(" + so + r")\b",
               lambda m: f"{so_thanh_chu(m.group(1))} đến {so_thanh_chu(m.group(2))}", s)
    don_vi = "|".join(sorted((re.escape(k) for k in DON_VI_DO), key=len, reverse=True))
    s = re.sub(r"(" + so + r")\s*(" + don_vi + r")(?![\wÀ-ỹ])",
               lambda m: f"{so_thanh_chu(m.group(1))} {DON_VI_DO[m.group(2)]}", s)
    s = re.sub(r"\d{1,3}(?:\.\d{3})+(?!\d)|\d+[,.]\d+|\d+", lambda m: so_thanh_chu(m.group(0)), s)
    return s


# ----------------------------------------------------------------------------- phát âm
def doc_tu_dien(*duong_dan):
    """Gộp các từ điển phát âm (sau đè trước). Tệp: {"muc": {"AI": {"vi": "ây ai", ...}, ...}}."""
    tu = {}
    for p in duong_dan:
        if not p or not os.path.isfile(p):
            continue
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        for k, v in (d.get("muc") or {}).items():
            tu[nfc(k)] = v if isinstance(v, dict) else {"vi": v}
    return tu


def ap_tu_dien(s, tu, ngon_ngu):
    """Thay từ theo từ điển (nguyên từ, phân biệt hoa thường). Trả (chuỗi, [từ đã thay])."""
    da = []
    for k in sorted(tu, key=len, reverse=True):
        doc = tu[k].get(ngon_ngu)
        if not doc:
            continue
        mau = r"(?<![\wÀ-ỹ])" + re.escape(k) + r"(?![\wÀ-ỹ])"
        s2 = re.sub(mau, doc, s)
        if s2 != s:
            da.append(k)
            s = s2
    return s, da


# ----------------------------------------------------------------------------- đọc kịch bản
def _gia_tri(v):
    v = v.strip()
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+[.,]\d+", v):
        return float(v.replace(",", "."))
    return v


def _tach_chi_dan(s):
    """'ấm áp | warm' -> ('ấm áp', 'warm'); 'warm' -> ('warm', 'warm')."""
    if "|" in s:
        a, b = s.split("|", 1)
        return a.strip(), b.strip()
    return s.strip(), s.strip()


def doc_kich_ban(duong_dan=None, van_ban=None, tu_dien=None):
    if van_ban is None:
        with open(duong_dan, encoding="utf-8") as f:
            van_ban = f.read()
    van_ban = nfc(van_ban).replace("\r\n", "\n")
    thong_tin = {"ngonNgu": "vi", "soLuot": 2, "nghiGiuaDoan": 0.6, "nghiSauMuc": 1.0}
    canh_bao = []
    m = re.match(r"^---\n(.*?)\n---\n", van_ban, re.S)
    if m:
        for dong in m.group(1).splitlines():
            dong = re.sub(r"\s+#.*$", "", dong).strip()
            if ":" in dong:
                k, v = dong.split(":", 1)
                thong_tin[k.strip()] = _gia_tri(v)
        van_ban = van_ban[m.end():]
    van_ban = re.sub(r"<!--.*?-->", "", van_ban, flags=re.S)
    chi_dan_chung = _tach_chi_dan(thong_tin["phongCach"]) if thong_tin.get("phongCach") else None
    nn = thong_tin["ngonNgu"]

    doan, khoi = [], []
    nghi_them, muc, chi_dan = 0.0, None, None

    def chot():
        nonlocal khoi, nghi_them, chi_dan
        if not khoi:
            return
        chu_goc = " ".join(x.strip() for x in khoi).strip()
        khoi = []
        if RE_CHU_THICH.search(chu_goc):
            canh_bao.append(f"đoạn {len(doan) + 1}: bỏ chú thích ngoặc vuông khỏi lời đọc: "
                            + ", ".join(RE_CHU_THICH.findall(chu_goc)).strip())
        chu_goc = RE_CHU_THICH.sub("", chu_goc)
        # bản viết (phụ đề): {{viết|đọc}} -> viết, bỏ thẻ
        chu = RE_PHAT_AM.sub(lambda m: m.group(1), chu_goc)
        chu = re.sub(r"\s+([,.!?;:…])", r"\1", re.sub(r"\s+", " ", RE_THE.sub("", RE_CD_TRONG.sub("", chu)))).strip()
        # bản đọc trung tính: {{viết|đọc}} -> đọc, giữ thẻ {..}
        doc_tt = RE_PHAT_AM.sub(lambda m: m.group(2), chu_goc)
        da_thay = []
        if tu_dien:
            # chỉ áp từ điển lên phần chữ, không áp vào thẻ
            phan = re.split(r"(\{[^{}]*\})", doc_tt)
            for i in range(0, len(phan), 2):
                phan[i], d = ap_tu_dien(phan[i], tu_dien, nn)
                da_thay += d
            doc_tt = "".join(phan)
        the_la = [t for t in RE_THE.findall(doc_tt) if _ten_the(t) not in THE]
        for t in the_la:
            canh_bao.append(f"đoạn {len(doan) + 1}: thẻ lạ {{{t}}}, máy đọc sẽ bỏ qua")
        if chu:
            doan.append({
                "id": f"d{len(doan) + 1:03d}", "chu": chu, "docTrungTinh": re.sub(r"\s+", " ", doc_tt).strip(),
                "chiDan": chi_dan or chi_dan_chung, "nghiTruoc": nghi_them, "muc": muc,
                "tuDienDaThay": sorted(set(da_thay)),
            })
            nghi_them = 0.0
        chi_dan = None

    for dong in van_ban.split("\n"):
        s = dong.strip()
        if not s:
            chot()
            continue
        if s.startswith("#"):
            chot()
            muc = s.lstrip("#").strip()
            nghi_them = max(nghi_them, float(thong_tin["nghiSauMuc"]))
            continue
        mn = RE_NGUNG_DONG.match(s)
        if mn:
            chot()
            nghi_them += float(mn.group(1).replace(",", "."))
            continue
        if s.startswith(">"):
            chot()
            chi_dan = _tach_chi_dan(s.lstrip("> ").strip())
            continue
        khoi.append(s)
    chot()
    return {"thongTin": thong_tin, "doan": doan, "canhBao": canh_bao}


# ----------------------------------------------------------------------------- dịch cho máy đọc
def cho_may(doan, may, cau_hinh_may, ngon_ngu="vi"):
    """Lời và tham số cho một máy đọc: {"text": ..., "style": ... (gemini), ...}."""
    s = doan["docTrungTinh"]
    if cau_hinh_may.get("chuanHoaSo") and ngon_ngu == "vi":
        phan = re.split(r"(\{[^{}]*\})", s)
        for i in range(0, len(phan), 2):
            phan[i] = chuan_hoa_so_vi(phan[i])
        s = "".join(phan)

    def doi_cd(m):
        en = _tach_chi_dan(m.group(1))[1]
        if may in ("drama3", "elevenlabs"):
            return f" [{en}] "
        if may == "higgs3":
            return " " + "".join(t for mau, t in HIGGS_TU_KHOA if re.search(mau, en, re.I))[:120] + " "
        return " "
    s = RE_CD_TRONG.sub(doi_cd, s)

    def doi(m):
        ten = _ten_the(m.group(1))
        cach = THE.get(ten, {}).get(may)
        return f" {cach} " if cach else " "
    s = RE_THE.sub(doi, s)
    s = re.sub(r"\s+([,.!?;:…])", r"\1", re.sub(r"\s+", " ", s)).strip()
    s = re.sub(r"([.!?…])[…,]+", r"\1", s)
    s = re.sub(r",$", ".", s)
    ra = {"text": s}
    cd = doan.get("chiDan")
    if cd:
        en = cd[1]
        if may == "gemini":
            ra["style"] = en
        elif may in ("elevenlabs", "drama3"):
            ra["text"] = f"[{en}] {s}"
        elif may == "higgs3":
            the = []
            for mau, tag in HIGGS_TU_KHOA:
                if re.search(mau, en, re.I) and tag not in the:
                    the.append(tag)
            # tối đa một thẻ cảm xúc, một thẻ nhịp, một thẻ kiểu
            chon, loai = [], set()
            for t in the:
                l = t.split(":")[0]
                if l not in loai:
                    chon.append(t)
                    loai.add(l)
            ra["text"] = "".join(chon) + s
    return ra


def lam_sach_de_so(s, ngon_ngu="vi"):
    """Chữ để so với bản gỡ băng: bỏ thẻ, dấu câu, đổi số thành chữ, viết thường."""
    s = nfc(s)
    s = re.sub(r"<\|[^|>]*\|>|<[^<>]*>|\[[^\[\]]*\]|\{[^{}]*\}", " ", s)
    if ngon_ngu == "vi":
        s = chuan_hoa_so_vi(s)
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# Câu Whisper hay "nghe ảo" ở quãng lặng cuối (học từ phụ đề YouTube); bỏ nếu lời gốc không có.
NGHE_AO = ["cảm ơn các bạn đã theo dõi", "hãy đăng ký kênh", "hãy subscribe cho kênh", "đăng ký kênh để ủng hộ",
           "hẹn gặp lại các bạn trong những video tiếp theo", "ghiền mì gõ", "thanks for watching",
           "thank you for watching", "please subscribe", "subtitles by"]


def bo_nghe_ao(goc, nghe):
    """Bỏ câu nghe ảo của Whisper khỏi bản gỡ băng (cả hai đã qua lam_sach_de_so)."""
    for c in NGHE_AO:
        c = lam_sach_de_so(c, "vi" if any(ord(x) > 127 for x in c) else "en")
        if c in nghe and c not in goc:
            nghe = nghe.replace(c, " ")
    return re.sub(r"\s+", " ", nghe).strip()


def gop_am_vi(s):
    """Gộp các phụ âm đầu giọng Bắc đọc như nhau (x/s, tr/ch, r/d/gi) để máy nghe không bắt lỗi oan."""
    ra = []
    for t in s.split():
        t = re.sub(r"^tr", "ch", t)
        t = re.sub(r"^x", "s", t)
        t = re.sub(r"^(gi|r)", "d", t)
        ra.append(t)
    return " ".join(ra)


def ty_le_loi(goc, nghe):
    """Tỷ lệ lỗi theo âm tiết (từ) giữa lời gốc và bản gỡ băng, kèm danh sách chỗ lệch."""
    a, b = goc.split(), nghe.split()
    n, m = len(a), len(b)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    lech, i, j = [], n, m
    while i > 0 or j > 0:
        if i and j and d[i][j] == d[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            if a[i - 1] != b[j - 1]:
                lech.append(("thay", a[i - 1], b[j - 1]))
            i, j = i - 1, j - 1
        elif i and d[i][j] == d[i - 1][j] + 1:
            lech.append(("thieu", a[i - 1], None))
            i -= 1
        else:
            lech.append(("thua", None, b[j - 1]))
            j -= 1
    return (d[n][m] / max(n, 1)), list(reversed(lech))
