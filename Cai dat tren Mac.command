#!/bin/bash
# Cài hoặc cập nhật xưởng lồng tiếng trên Mac: đo máy, dựng môi trường Python, tải mô hình của máy đọc đang bật,
# gỡ mô hình không còn dùng, rồi tự kiểm. Bấm lại bao nhiêu lần cũng được. Chi tiết: tools/cai_dat.py.
# Mọi thứ cài vào ~/Library/Application Support/xuong-long-tieng (ngoài repo, không lên git).
# Nếu macOS báo "không mở được vì từ nhà phát triển không xác định": bấm chuột phải vào tệp, chọn Open, rồi Open lần nữa.

cd "$(dirname "$0")" || exit 1
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
dong() {
  echo
  if [ -t 0 ]; then read -r -n 1 -p "Bấm phím bất kỳ để đóng cửa sổ này..."; echo; fi
  exit "$1"
}
if ! command -v uv >/dev/null 2>&1; then
  echo "== Cài công cụ uv (quản lý Python)"
  curl -LsSf https://astral.sh/uv/install.sh | sh || { echo "Không cài được uv: kiểm tra mạng rồi bấm đúp lại."; dong 1; }
  export PATH="$HOME/.local/bin:$PATH"
fi
uv run --no-project --python 3.12 tools/cai_dat.py "$@"
dong $?
