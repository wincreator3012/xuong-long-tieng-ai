#!/bin/bash
# Mở Bàn nghe trong trình duyệt: nghe từng đoạn, chọn lượt đọc, ghi chú đọc lại, ghép bản chính, thi nghe mù.
# Đóng cửa sổ Terminal này để tắt Bàn nghe.

cd "$(dirname "$0")" || exit 1
ENV="$HOME/Library/Application Support/xuong-long-tieng"
export PATH="$ENV/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
PY="$ENV/venv-mlx/bin/python"; [ -x "$PY" ] || PY="$ENV/venv-chung/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"
"$PY" tools/ban_nghe/may_chu.py --cong 8768
