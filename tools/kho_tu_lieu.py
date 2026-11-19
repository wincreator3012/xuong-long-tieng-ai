# -*- coding: utf-8 -*-
"""Tìm KHO GIỌNG của xưởng: thư mục cạnh xưởng chứa hồ sơ giọng riêng và từ điển phát âm đã duyệt. Đó là dữ liệu
riêng của người dùng nên nằm NGOÀI thư mục xưởng: cập nhật xưởng không bao giờ đụng tới, sao lưu chỉ cần dời một thư mục.

    <thư mục mẹ>/Kho giong/
      giong-noi/giong-noi.json      hồ sơ giọng (@<tên>): mẫu, mẫu chính, đồng thuận, mã đăng ký đám mây
      giong-noi/<tên>/*.wav         tệp mẫu giọng, câu đồng thuận ghi âm
      ngon-ngu/phat-am.json         từ điển phát âm đã nghe và duyệt (đè lên du-lieu/phat-am-de-xuat.json của xưởng)

Thứ tự tìm: biến môi trường KHO_GIONG; cau-hinh.json > "khoTuLieu" (đường dẫn tương đối so với xưởng, hoặc false để tắt);
rồi "../Kho giong". tools/dung_xuong.py tạo thư mục này khi dựng xưởng.
"""
import functools
import json
import os
import sys

sys.dont_write_bytecode = True

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAC_DINH = os.path.join(os.path.dirname(_REPO), "Kho giong")


def _la_kho(p):
    return bool(p) and os.path.isdir(os.path.join(p, "giong-noi"))


def _cau_hinh():
    try:
        with open(os.path.join(_REPO, "cau-hinh.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


@functools.lru_cache(None)
def tim():
    """Đường dẫn tuyệt đối của kho giọng, hoặc None."""
    v = os.environ.get("KHO_GIONG")
    if v:
        return os.path.abspath(os.path.expanduser(v))
    ch = _cau_hinh().get("khoTuLieu")
    if ch is False:
        return None
    for v in ([ch] if isinstance(ch, str) else ch or []) + [MAC_DINH]:
        p = os.path.abspath(os.path.join(_REPO, os.path.expanduser(v)))
        if _la_kho(p):
            return p
    return None


def tao(goc=None):
    """Tạo kho giọng rỗng (dùng khi dựng xưởng)."""
    goc = goc or MAC_DINH
    os.makedirs(os.path.join(goc, "giong-noi"), exist_ok=True)
    os.makedirs(os.path.join(goc, "ngon-ngu"), exist_ok=True)
    p = os.path.join(goc, "ngon-ngu", "phat-am.json")
    if not os.path.isfile(p):
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"_huong-dan": "Từ điển phát âm đã nghe và duyệt, đè lên du-lieu/phat-am-de-xuat.json của xưởng. "
                                     "Khóa là chữ viết đúng như trong kịch bản; giá trị theo ngôn ngữ của câu, vd "
                                     "\"Zoom\": {\"vi\": \"dum\"}.", "muc": {}}, f, ensure_ascii=False, indent=1)
            f.write("\n")
    tim.cache_clear()
    return goc


if __name__ == "__main__":
    g = tim()
    print(g or "Không tìm thấy kho giọng.")
    sys.exit(0 if g else 1)
