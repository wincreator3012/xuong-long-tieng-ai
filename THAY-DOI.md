# Nhật ký thay đổi của bản thiết kế

Mỗi mục: ngày, điều thay đổi, tệp liên quan, có cần chạy lại trình cài đặt trên máy thật không. AI của xưởng đã dựng đọc tệp này khi người dùng nói "xem bản thiết kế có gì mới" (xem mục cuối `DUNG-XUONG.md`).

## 2026-11-19: bản đầu tiên

- Xưởng lồng tiếng tiếng Việt, tiếng Anh: hàng đợi chạy trên máy thật, năm máy đọc (Drama 3, VieNeu, Higgs v3, Gemini, ElevenLabs), kiểm bằng gỡ băng ngược, Bàn nghe, thi nghe mù, giọng riêng có đồng thuận, ghép thành phẩm chuẩn âm lượng kèm phụ đề.
- Trình cài đặt đa nền tảng (`tools/cai_dat.py`, gọi từ `Cai dat tren Mac.command` hoặc `Cai dat tren Windows.bat`): đo máy, đề xuất máy đọc theo cấu hình (`tools/do_may.py`), chỉ cài đúng máy đọc đang bật, tự gỡ mô hình và môi trường không còn dùng, tự kiểm cả khâu gỡ băng ngược.
- Khuôn lời đọc đã thi nghe mù với Drama 3: tiếng Việt "nhịp mạnh" (4,5/5), tiếng Anh "ấm và chậm" (5/5).
- Drama 3 đo thật trên Mac M4 Max: 28,6 GB bộ nhớ đỉnh, nạp khoảng 12 giây, đọc nhanh hơn thời gian thực khoảng 2,5 lần.
- Đã chạy thật: Mac M4 Max 64 GB (Drama 3, VieNeu, Higgs v3, Whisper MLX); Linux (VieNeu, faster-whisper, trọn trình cài và tự kiểm). Chưa chạy thật: tệp bấm đúp trên Windows, Gemini, ElevenLabs.
