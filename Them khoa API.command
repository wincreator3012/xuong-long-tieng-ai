#!/bin/bash
# Lưu khóa API của Gemini và ElevenLabs vào Keychain của macOS (dịch vụ "xuong-long-tieng").
# Khóa không bao giờ nằm trong tệp nào của xưởng. Để trống rồi Enter để bỏ qua một dịch vụ.

cd "$(dirname "$0")" || exit 1
ENV="$HOME/Library/Application Support/xuong-long-tieng"
PY="$ENV/venv-mlx/bin/python"; [ -x "$PY" ] || PY="$ENV/venv-chung/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"
"$PY" tools/them_khoa.py
echo
if [ -t 0 ]; then read -r -n 1 -p "Bấm phím bất kỳ để đóng cửa sổ này..."; echo; fi
