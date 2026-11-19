# Hướng dẫn dùng xưởng lồng tiếng

Bạn nói với AI cần lồng tiếng gì (kịch bản, thứ tiếng, giọng nào, dùng cho đâu). AI soạn lời đọc để bạn duyệt trên chữ, xếp việc vào hàng đợi, rồi nhờ bạn bấm đúp một tệp trên máy. Mô hình chạy ngay trên máy bạn; tiếng không rời máy, trừ khi bạn chọn dịch vụ đám mây (Gemini, ElevenLabs).

## Các tệp bấm đúp

Mở thư mục xưởng (Finder trên Mac, File Explorer trên Windows):

| Mac | Windows | Khi nào bấm | Mất bao lâu |
|---|---|---|---|
| `Cai dat tren Mac.command` | `Cai dat tren Windows.bat` | lần đầu trên mỗi máy; khi AI báo có cập nhật hay vừa đổi máy đọc | lần đầu 15-60 phút tùy mô hình; những lần sau vài phút |
| `Long tieng tren Mac.command` | `Long tieng tren Windows.bat` | mỗi khi AI báo "đã xếp việc" | một trang lời đọc thường dưới 5 phút trên máy mạnh |
| `Mo ban nghe.command` | `Mo ban nghe tren Windows.bat` | để nghe, chọn lượt, ghi chú đọc lại, ghép bản chính, thi nghe mù | đóng cửa sổ đen để tắt |
| `Them khoa API.command` | `Them khoa API tren Windows.bat` | khi dùng Gemini hoặc ElevenLabs | 2 phút |

Lần đầu mở một tệp: trên Mac, nếu bị báo "từ nhà phát triển không xác định", bấm chuột phải vào tệp, chọn Open, rồi Open lần nữa; trên Windows, nếu hiện "Windows protected your PC", bấm More info rồi Run anyway. Chỉ cần làm một lần cho mỗi tệp.

Trình cài đặt chỉ giữ những gì xưởng đang dùng. Đổi máy đọc thì bấm lại nó: mô hình mới được tải, mô hình không còn dùng được gỡ.

## Đặt yêu cầu sao cho hay

- **Nói đủ bốn điều trong một câu:** đoạn lời nào, thứ tiếng, giọng (của bạn hay có sẵn), dùng cho đâu. Ví dụ: "Lồng tiếng phần mở đầu bài 2, tiếng Anh, giọng tôi, cho video khoá học trên YouTube."
- **Duyệt lời đọc trên chữ trước.** Sửa ở bước này chỉ mất một câu nói; sửa sau khi máy đã đọc mất cả lượt chờ.
- **Viết cho tai.** Câu ngắn, một ý một câu. Số, ngày, tên riêng, chữ viết tắt: AI viết rõ cách đọc, bạn xem lại chỗ đó.
- **Góp ý theo đoạn:** "đoạn 3 chậm hơn, nhấn chữ buông", "đoạn 5 đọc vui hơn". Ghi chú thẳng trong Bàn nghe là gọn nhất.
- **Dặn "từ nay luôn..."** khi muốn xưởng nhớ một điều cho mọi bản sau (ví dụ "từ nay luôn đọc SEL là ét e eo"): AI ghi vào từ điển phát âm hoặc bài học.

## Bàn nghe

Trang mở trong trình duyệt, chỉ chạy trên máy bạn.

- **Nghe duyệt:** mỗi đoạn có 2 hoặc 3 lượt đọc. Máy đã chấm sẵn (lệch lời, tốc độ, cờ cảnh báo) và đánh dấu lượt tốt nhất. Chọn lượt ưng, ghi chú đoạn cần đọc lại, bấm "Lưu lựa chọn". Bấm "Ghép bản chính" để có thành phẩm.
- **Thi nghe mù:** nhiều cách đọc cùng một kịch bản (nhiều mô hình, nhiều mẫu giọng, hay nhiều cách viết lời), hiện theo chữ cái A, B, C. Chấm 4 tiêu chí (tự nhiên, biểu cảm đúng ý, phát âm đúng, giống giọng bạn) rồi mới thấy tên.

## Giọng riêng của bạn

Thu mẫu theo `docs/THU-MAU-GIONG.md` (khoảng 15 phút), gửi AI. AI cắt mẫu, đưa vào `Kho giong`, rồi dựng một lượt thi nghe mù để bạn chọn mẫu giống mình nhất. Bạn có thể giữ hai mẫu cho hai sắc thái (ví dụ giọng giảng bài và giọng trò chuyện trầm hơn) và dặn AI dùng mẫu nào cho bản nào.

Chỉ nhân bản giọng của chính bạn, hoặc của người đã đồng thuận bằng văn bản; AI ghi rõ đồng thuận ấy vào hồ sơ giọng.

## Thành phẩm nằm ở đâu

`Du an/<tên dự án>/thanh-pham/`: tệp WAV 48 kHz đã chuẩn âm lượng (-16 LUFS), phụ đề `.srt`, mốc thời gian từng đoạn `.moc.json` (có ghi mô hình đã đọc từng đoạn).

## Chi phí

- Mô hình tại máy (Drama 3, VieNeu): miễn phí. Drama 3 miễn phí cho cá nhân, tổ chức có doanh thu năm (tính cả công ty liên kết) dưới 500.000 USD; vượt ngưỡng cần giấy phép thương mại của Fish Audio.
- Gemini, ElevenLabs: tính phí theo lượng chữ, theo bảng giá hiện hành của hãng; nhân bản giọng chuyên nghiệp trên ElevenLabs cần gói trả phí. Hỏi AI tra giá mới nhất trước khi dùng nhiều.

## Khi có gì lạ

| Bạn thấy | Thường là | Làm gì |
|---|---|---|
| Cửa sổ cài đặt báo "không đủ chỗ" | ổ đĩa đầy | dọn bớt rồi bấm lại; phần đã tải được giữ |
| "Máy đọc ... đang tắt" | máy đọc chưa được bật cho xưởng | nhờ AI bật rồi bấm lại tệp cài đặt |
| Bàn nghe không mở | Bàn nghe đang chạy sẵn trong cửa sổ khác | mở trình duyệt vào `http://127.0.0.1:8768/` |
| Giọng nghe đều đều | lời đọc dặn chậm cả bài | nhờ AI viết lại theo khuôn nhịp đã chốt của thứ tiếng đó |
| Đọc sai một tên riêng | thiếu cách đọc | nói "từ nay luôn đọc X là ..." |

Còn lại: nói với AI điều bạn thấy, kèm ảnh chụp cửa sổ. AI đọc nhật ký ở `Du an/_tam/long-tieng/log/` để tìm nguyên nhân.
