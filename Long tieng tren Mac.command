#!/bin/bash
# Chạy mọi việc lồng tiếng Claude đã xếp: sinh tiếng, gỡ băng ngược để kiểm, chấm lượt, ghép bản nháp.
# Cách dùng: mở Finder, vào thư mục xưởng, bấm đúp tệp này. Chạy xong thì quay lại Claude.

cd "$(dirname "$0")" || exit 1
ENV="$HOME/Library/Application Support/xuong-long-tieng"
export PATH="$ENV/bin:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
export HF_HOME="$ENV/hf" HF_HUB_DISABLE_TELEMETRY=1

ket_thuc() {
  echo
  if [ -t 0 ]; then read -r -n 1 -p "Bấm phím bất kỳ để đóng cửa sổ này..."; echo; fi
  exit "$1"
}

PY="$ENV/venv-mlx/bin/python"; [ -x "$PY" ] || PY="$ENV/venv-chung/bin/python"
if [ ! -x "$PY" ]; then
  echo "Máy này chưa cài xưởng: bấm đúp 'Cai dat tren Mac.command' trước."; ket_thuc 1
fi
"$PY" tools/hang_doi.py chay
RC=$?
echo
if [ $RC -eq 0 ]; then
  echo "Lồng tiếng xong. Bấm đúp 'Mo ban nghe.command' để nghe, hoặc quay lại Claude và nhắn: đã lồng tiếng xong."
elif [ $RC -eq 75 ]; then
  echo "Hàng đợi đang được chạy ở nơi khác (Trạm Mac hoặc một cửa sổ khác). Bạn không cần làm gì thêm."
else
  echo "Có việc bị lỗi. Quay lại Claude và nhắn: lồng tiếng bị lỗi (log ở Du an/_tam/long-tieng/log/)."
fi
ket_thuc $RC
