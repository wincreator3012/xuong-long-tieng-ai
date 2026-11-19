# Chọn máy đọc theo cấu hình máy và mục đích

Đọc ở Bước 2 của skill long-tieng-thiet-lap, và mỗi khi người dùng hỏi "máy tôi dùng được gì", "sao giọng nghe như máy", "có cách nào hay hơn không". Số liệu ở đây lấy từ thi nghe mù thật ở xưởng gốc (tháng 11/2026, thang 5, chi tiết ở `docs/BAI-HOC.md`), không phải từ quảng cáo của mô hình.

## Hai câu hỏi quyết định

1. **Người dùng muốn giọng của ai?** Giọng của chính họ (cần thu mẫu khoảng 15 phút), hay giọng có sẵn của mô hình (dùng được ngay).
2. **Máy thật của họ mạnh tới đâu?** Đọc `Du an/_tam/may-tinh.json` sau lần cài đầu (trình cài đo trên máy thật). Chưa cài thì hỏi người dùng: Mac hay Windows; Mac thì chip gì, bao nhiêu RAM (menu Apple > About This Mac); Windows thì RAM bao nhiêu, có card NVIDIA không (Settings > System > About). Không đo trong máy ảo của AI: số ra sai.

## Bảng chọn

| Máy thật | Giọng của chính mình | Giọng có sẵn |
|---|---|---|
| Mac chip Apple, RAM từ 48 GB (thường là M Max, M Ultra, một số M Pro) | **Drama 3** (`drama3`): biểu cảm nhất, thi nghe 4,5/5 tiếng Việt, 5/5 tiếng Anh. Tải 24 GB, nạp khoảng 30 giây, đọc nhanh hơn thời gian thực | VieNeu (tại máy, miễn phí, biểu cảm yếu) hoặc Gemini (đám mây, có phí) |
| Mac chip Apple, RAM 36 đến 47 GB | Drama 3 chạy được nếu đóng bớt ứng dụng khác (đo thật ở xưởng gốc: 28,6 GB bộ nhớ đỉnh), máy 32 GB thì quá sát. Không ổn thì ElevenLabs hoặc Gemini với giọng đã đăng ký | như trên |
| Mac chip Apple, RAM dưới 36 GB | Gemini hoặc ElevenLabs với giọng đã đăng ký (đám mây, có phí); VieNeu nhân bản được nhưng giống giọng kém (thi nghe 1,0/5) | VieNeu hoặc Gemini |
| Mac chip Intel, Windows, Linux | như dòng trên: Gemini hoặc ElevenLabs; VieNeu tại máy | VieNeu hoặc Gemini |

Ghi chú:

- **VieNeu** chạy trên CPU ở mọi máy (ONNX), 25 giọng có sẵn tiếng Việt ba miền, tải dưới 1 GB. Hợp làm bản nháp nghe nhịp, nội dung cần riêng tư, máy yếu. Đừng hứa biểu cảm: thi nghe chỉ 1,25/5.
- **Gemini, ElevenLabs** chạy trên máy chủ của hãng, máy nào cũng dùng được, cần khóa API và mạng, tính phí theo lượng chữ. Xưởng gốc chưa thi nghe hai máy này (chưa chạy thử lần nào): khi bật lần đầu, làm một lượt thi nghe mù trước khi dùng cho việc thật, và nói rõ với người dùng điều này. Gemini cần câu đồng thuận ghi âm khi đăng ký giọng riêng; ElevenLabs nhân bản nhanh từ mẫu dưới 2 phút (gói Starter).
- **Higgs v3** chạy trên Mac chip Apple, thi nghe tiếng Anh chỉ 1,5/5, giấy phép chỉ cho làm video, podcast có ghi công. Không đề xuất, trừ khi người dùng muốn thử.
- **Windows có card NVIDIA:** bộ gỡ băng ngược (faster-whisper) tự dùng GPU. Drama 3 bản gốc của Fish Audio chạy được trên GPU NVIDIA mạnh, nhưng xưởng chưa có bộ nối cho đường đó; người dùng rành kỹ thuật có thể tự thêm (viết `tools/may_doc/<bộ nối>.py`, thêm mục vào `may-doc.json`).
- **Ổ đĩa:** Drama 3 cần khoảng 26 GB trống (mô hình cộng bộ gỡ băng), VieNeu và đám mây khoảng 3 GB.

## Đổi máy đọc về sau

Sửa `cau-hinh.json` > `mayDung` (danh sách, máy đầu tiên là mặc định cho dự án mới), rồi nhờ người dùng bấm đúp trình cài đặt trên máy thật: nó cài thêm máy mới, gỡ mô hình của máy đã bỏ để trả chỗ trống, rồi tự kiểm. Bật máy đám mây thì nhờ họ chạy thêm tệp "Them khoa API".

Thử xem trước kế hoạch mà không cài gì: người dùng chạy trình cài với tham số `--xem` (trong Terminal: `uv run --no-project --python 3.12 tools/cai_dat.py --xem`). Thường không cần.

## Vì sao không tự chọn máy mạnh nhất cho mọi người

Máy đọc tốt nhất đòi máy mạnh và mẫu giọng; máy đọc chạy mọi nơi thì biểu cảm yếu; máy đọc đám mây thì tốn phí và gửi lời đọc ra ngoài. Không có lựa chọn đúng cho mọi người, nên trình cài chỉ đề xuất theo phần cứng; AI hỏi thêm mục đích rồi cùng người dùng quyết, và nói thẳng giới hạn của lựa chọn ấy.
