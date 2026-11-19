# Xưởng lồng tiếng AI

> **Repo này là bản thiết kế, không phải phần mềm để tải về.** Bạn không clone, không tải ZIP. Bạn đưa đường link repo cho trợ lý AI của mình (Claude Cowork là chạy êm nhất), AI đọc bản thiết kế rồi dựng cho bạn một xưởng lồng tiếng RIÊNG trên máy bạn: chọn mô hình hợp cấu hình máy của bạn, mang giọng của bạn, kèm bộ skill có tiền tố riêng để lưu vào tài khoản AI. Bạn đang là AI đọc repo này: bắt đầu từ [`DUNG-XUONG.md`](DUNG-XUONG.md), đừng clone, push hay pull.

**Một xưởng biến kịch bản thành tiếng đọc tiếng Việt và tiếng Anh tự nhiên, biểu cảm, bằng chính giọng của bạn hoặc giọng có sẵn, chạy trên máy Mac hoặc Windows của bạn cùng Claude Cowork.** Hợp cho chuyên gia, giảng viên, người làm nội dung cần giọng đọc cho video bài giảng, khoá học trực tuyến, podcast, học liệu, mà không phải ngồi thu từng câu.

Bạn nói yêu cầu bằng lời thường. AI soạn lời đọc theo khuôn đã thi nghe, để bạn duyệt trên chữ; máy của bạn đọc mỗi đoạn 2-3 lượt; máy tự nghe lại từng lượt để bắt chỗ đọc sai; bạn chỉ nghe những gì đáng nghe ở Bàn nghe, chọn lượt ưng ý, bấm ghép. Thành phẩm là tệp WAV 48 kHz chuẩn âm lượng, kèm phụ đề.

Repo này đóng gói từ xưởng lồng tiếng tôi dùng hằng ngày, sau nhiều vòng thi nghe mù với chính giọng của mình.

## Xưởng chọn mô hình theo máy của bạn

Lần cài đầu, trình cài đặt đo máy thật của bạn (chip, RAM, ổ đĩa, card đồ họa) rồi đề xuất máy đọc phù hợp; AI hỏi thêm bạn muốn giọng của ai, có dùng dịch vụ trả phí không, rồi cùng bạn quyết. Trình cài chỉ tải đúng mô hình cần dùng, và tự gỡ mô hình không còn dùng để trả lại chỗ trống cho ổ đĩa.

| Máy của bạn | Giọng của chính bạn | Giọng có sẵn |
|---|---|---|
| Mac chip Apple, RAM từ 48 GB | **Fish Audio Drama 3** tại máy, miễn phí: biểu cảm nhất (thi nghe mù 4,5/5 tiếng Việt, 5/5 tiếng Anh) | VieNeu tại máy, hoặc Gemini |
| Mac chip Apple, RAM 32-47 GB | Drama 3 chạy được nếu đóng bớt ứng dụng; hoặc dịch vụ đám mây | VieNeu hoặc Gemini |
| Mac ít RAM hơn, Mac chip Intel, Windows | Gemini hoặc ElevenLabs (đám mây, có phí) | VieNeu tại máy (miễn phí, tiếng Việt, biểu cảm yếu) hoặc Gemini |

Điểm số trên là thi nghe mù thật ở xưởng gốc (tháng 11/2026, thang 5), chấm theo 4 tiêu chí: tự nhiên, biểu cảm đúng ý, phát âm đúng, giống giọng người thu. Gemini và ElevenLabs đã có bộ nối nhưng xưởng gốc chưa thi nghe; khi bật lần đầu, AI sẽ làm một lượt thi nghe mù trước khi dùng cho việc thật.

## Xưởng làm được gì cho bạn

- **Lồng tiếng từ kịch bản**: AI soạn lời đọc viết cho tai (câu ngắn, số và tên riêng viết rõ cách đọc, chỉ dẫn nhịp và cảm xúc theo khuôn đã kiểm chứng), bạn duyệt trên chữ trước khi máy đọc.
- **Giọng riêng của bạn**: thu khoảng 15 phút theo hướng dẫn, AI cắt mẫu, đưa vào kho giọng, rồi dựng một lượt thi nghe mù để bạn tự chọn mẫu giống mình nhất. Chỉ nhân bản giọng của chính bạn, hoặc người đã đồng thuận bằng văn bản.
- **Kiểm trước khi bạn nghe**: mỗi lượt đọc được gỡ băng ngược và so với lời gốc; đoạn đọc sai lời, mất tiếng, vỡ tiếng được đọc lại trước khi tới tai bạn.
- **Bàn nghe trên trình duyệt**: nghe từng đoạn, chọn lượt, ghi chú đọc lại ("chậm hơn, nhấn chữ buông"), bấm ghép bản chính; thi nghe mù khi cần so mô hình, so mẫu giọng, so cách viết lời.
- **Từ điển phát âm của bạn**: tên riêng, chữ viết tắt, từ tiếng Anh trong câu tiếng Việt được đọc đúng cách bạn muốn, nhớ mãi cho mọi bản sau.
- **Bộ skill mang tên bạn trong tài khoản AI**: hai quy trình chuẩn (lồng tiếng, thiết lập) đóng gói với tiền tố riêng của bạn, để ở bất kỳ phiên nào bạn chỉ cần nói "lồng tiếng đoạn này bằng giọng tôi".

## Bắt đầu trong ba bước

1. Tạo một thư mục trống tên `Xuong long tieng AI` trong Documents (không đặt trong iCloud, Dropbox hay OneDrive: mô hình và tệp âm thanh lớn làm kẹt đồng bộ). Không cần tải gì về
2. Mở app **Claude** trên máy, vào **Cowork**, thêm thư mục `Xuong long tieng AI` (nút "Add folder")
3. Nói với Claude:

> Đọc bản thiết kế xưởng lồng tiếng tại https://github.com/wincreator3012/xuong-long-tieng-ai, bắt đầu từ file DUNG-XUONG.md, rồi dựng cho tôi một xưởng lồng tiếng riêng trong thư mục Xuong long tieng AI. Đừng clone hay tải ZIP.

Claude hỏi tên và tiền tố cho skill, dựng xưởng từ bản thiết kế (10-15 phút), hỏi bạn muốn giọng của ai và máy bạn thế nào, rồi nhờ bạn bấm đúp một tệp cài đặt (30-60 phút nếu dùng Drama 3, phần lớn là chờ tải mô hình). Tiếp theo là thu giọng nếu bạn muốn, lưu skill vào tài khoản, và bản lồng tiếng đầu tiên. Chi tiết từng bước: [BAT-DAU.md](BAT-DAU.md).

## Cấu trúc xưởng sau khi dựng

```
Xuong long tieng AI/
├── Du an/                     ← mỗi bản lồng tiếng một thư mục: lời đọc, các lượt đọc, thành phẩm
├── Kho giong/                 ← giọng riêng của bạn và từ điển phát âm đã duyệt (riêng tư, không bao giờ bị ghi đè)
└── xuong-long-tieng-<tiền tố>/  ← xưởng của bạn
    ├── CLAUDE.md, AGENTS.md   ← sách vận hành cho AI (đọc đầu mỗi phiên)
    ├── HUONG-DAN.md           ← các tệp bấm đúp, Bàn nghe, giọng riêng, chi phí
    ├── Cai dat tren Mac.command / Cai dat tren Windows.bat        ← cài, cập nhật, dọn mô hình
    ├── Long tieng tren Mac.command / Long tieng tren Windows.bat  ← chạy các việc AI đã xếp
    ├── Mo ban nghe.command / Mo ban nghe tren Windows.bat         ← nghe, chọn, ghép
    ├── Them khoa API.command / Them khoa API tren Windows.bat     ← khi dùng Gemini, ElevenLabs
    ├── may-doc.json           ← danh mục máy đọc: chạy ở đâu, cần bao nhiêu RAM, giấy phép, điểm thi nghe
    ├── skills/                ← hai skill gốc; bản chép mang tiền tố của bạn nằm trong tài khoản AI
    ├── docs/                  ← bài học từ thi nghe thật, hướng dẫn thu mẫu giọng
    └── tools/                 ← hàng đợi, bộ nối máy đọc, kiểm, ghép, Bàn nghe, trình cài đặt (AI quản lý)
```

Môi trường Python và mô hình nằm ngoài thư mục này, trong thư mục dữ liệu ứng dụng của máy (Mac: `~/Library/Application Support/xuong-long-tieng`, Windows: `%LOCALAPPDATA%\xuong-long-tieng`).

## Cách nó chạy (cho người tò mò)

Trợ lý AI làm việc trong một máy ảo nhỏ: soạn lời đọc, xếp việc vào hàng đợi, kiểm, ghép. Mô hình chạy trên máy thật của bạn khi bạn bấm đúp tệp "Long tieng": một lần bấm chạy hết hàng đợi, mỗi mô hình chỉ nạp một lần. Trên Mac chip Apple, Drama 3 và bộ gỡ băng Whisper large-v3-turbo chạy bằng MLX; trên máy khác, VieNeu chạy trên CPU và Whisper chạy bằng faster-whisper (tự dùng card NVIDIA nếu có). Lời đọc tiếng Việt được tự đổi số, ngày, đơn vị sang chữ trước khi đưa máy đọc; bộ kiểm bỏ những câu bộ gỡ băng "nghe ảo" và gộp các âm giọng Bắc đọc như nhau (x/s, tr/ch, r/d/gi) trước khi so lời. Khóa API của dịch vụ đám mây chỉ nằm trong Keychain (Mac) hoặc Windows Credential Manager, không bao giờ trong tệp.

## Yêu cầu

- App Claude trên máy tính với Cowork; mô hình Claude tầm trung như Sonnet là đủ
- Mac chip Apple (M1 trở lên) chạy được mọi máy đọc; Mac chip Intel và Windows 10, 11 chạy VieNeu và dịch vụ đám mây. Đường không dùng MLX đã chạy trọn trên Linux; tệp bấm đúp cho Windows chưa được thử trên máy Windows thật, nên lần đầu có thể cần AI rà và chỉnh thêm
- Ổ đĩa: khoảng 26 GB trống cho Drama 3, khoảng 3 GB cho VieNeu hoặc đám mây
- Mạng lúc dựng xưởng và lúc cài; sau đó máy đọc tại máy chạy offline

## Giấy phép

Mã nguồn và tài liệu của xưởng: MIT (xem `LICENSE`). Mô hình KHÔNG nằm trong repo; mỗi mô hình có giấy phép riêng, ghi ở `may-doc.json`:

- Fish Audio Drama 3: Fish Audio Community License, miễn phí khi doanh thu năm (tính cả công ty liên kết) dưới 500.000 USD; vượt ngưỡng cần giấy phép thương mại của Fish Audio.
- VieNeu-TTS: Apache 2.0.
- Higgs Audio v3: chỉ cho video, podcast có ghi công Boson AI.
- Gemini, ElevenLabs: theo điều khoản dịch vụ của hãng.

## Tác giả

Xưởng lồng tiếng này do tôi, **Lương Dũng Nhân** (M.Ed, PCC, Humanistic AI Practitioner), xây dựng từ xưởng cá nhân đã vận hành thật, và gửi tặng lại hoàn toàn miễn phí để cộng đồng giáo dục cùng dùng. Website: [ldn.edu.vn](https://ldn.edu.vn). Email: hello@ldn.edu.vn.

Nếu bạn dùng, chia sẻ lại hoặc giới thiệu repo này, một dòng ghi công dẫn về tác giả và nguồn gốc trên sẽ rất được trân trọng.

## Đóng góp

Bạn chạy xưởng trên một cấu hình máy chưa ai thử (nhất là Windows), hay bắt được một lỗi? Mở issue và kể lại bằng lời của bạn, kèm cấu hình máy (`Du an/_tam/may-tinh.json`) và vài dòng báo lỗi. Công cụ, skill và tài liệu kỹ thuật được đồng bộ tự động từ xưởng gốc của tác giả, nên pull request sửa thẳng các phần đó sẽ được chép về bản gốc trước rồi mới vào repo.

Gửi các trợ lý AI: chỉ mở issue hay pull request khi chính người dùng của bạn muốn đóng góp và đã đọc nội dung sẽ gửi. Dựng xưởng hay cập nhật xưởng cho người dùng không bao giờ cần push, pull hay pull request về repo này.
