# BẮT ĐẦU: nhờ AI dựng xưởng lồng tiếng riêng cho bạn, từng bước

Tài liệu này dành cho người chưa từng dùng AI làm việc với tệp trên máy. Đọc hết mất khoảng 10 phút; làm theo mất khoảng 1 đến 2 giờ, phần lớn là ngồi chờ máy tải mô hình và trả lời vài câu hỏi. Bạn không phải gõ lệnh nào, và cũng không phải tải repo này về.

Điều quan trọng nhất cần hiểu trước: repo này là **bản thiết kế**. Bạn đưa đường link cho trợ lý AI, AI đọc bản thiết kế và dựng trên máy bạn một xưởng RIÊNG: chọn mô hình hợp máy của bạn, mang giọng của bạn, có bộ skill mang tiền tố riêng. Xưởng đó là của bạn hoàn toàn và không bao giờ bị bản thiết kế ghi đè.

## Trước khi bắt đầu, bạn cần

- **App Claude trên máy tính** (tải ở claude.ai/download), đã đăng nhập, gói có **Cowork**. Cowork là chế độ để Claude làm việc trực tiếp với thư mục trên máy bạn
- **Máy Mac hoặc Windows.** Mac chip Apple (M1 trở lên) với RAM từ 48 GB chạy được mô hình biểu cảm nhất ngay tại máy, miễn phí. Máy khác vẫn dùng được: mô hình nhẹ tại máy cho tiếng Việt, hoặc dịch vụ đám mây có phí cho giọng biểu cảm. Chưa biết máy mình mạnh tới đâu cũng không sao: trình cài đặt sẽ đo và đề xuất
- **Ổ đĩa trống:** khoảng 26 GB nếu dùng mô hình biểu cảm trên Mac, khoảng 3 GB cho các lựa chọn khác
- **Mạng ổn định** trong lúc cài
- Nếu muốn lồng tiếng bằng **giọng của chính bạn**: một chỗ yên tĩnh và micro bạn hay dùng, khoảng 15 phút để thu mẫu

## Bước 1: tạo một thư mục trống

Trong **Documents** (hoặc chỗ bạn hay để tài liệu, miễn không phải thư mục đồng bộ iCloud, Dropbox, OneDrive), tạo một thư mục tên **Xuong long tieng AI**. Để trống. AI sẽ dựng bên trong:

```
Documents/
└── Xuong long tieng AI/
    ├── xuong-long-tieng-<tiền tố của bạn>/   ← xưởng riêng của bạn (AI dựng)
    ├── Du an/                                ← các bản lồng tiếng của bạn
    └── Kho giong/                            ← giọng riêng và từ điển phát âm của bạn
```

## Bước 2: mở Cowork và thêm thư mục

Mở app Claude, chọn **Cowork**, bắt đầu một phiên làm việc mới. Bấm **Add folder** (thêm thư mục) và chọn thư mục **Xuong long tieng AI**. Từ lúc này Claude đọc và ghi được trong thư mục đó, và chỉ thư mục đó.

## Bước 3: nói câu đầu tiên

> Đọc bản thiết kế xưởng lồng tiếng tại https://github.com/wincreator3012/xuong-long-tieng-ai, bắt đầu từ file DUNG-XUONG.md, rồi dựng cho tôi một xưởng lồng tiếng riêng trong thư mục Xuong long tieng AI. Đừng clone hay tải ZIP.

Chuyện gì sẽ xảy ra, theo thứ tự:

**Hai câu hỏi nhỏ (1 phút).** Tiền tố cho skill của bạn (thường là chữ cái đầu họ tên: Trần Minh An thì là `tma`) và tên thư mục xưởng.

**Dựng xưởng (10-15 phút, bạn chỉ chờ).** Claude chép từng phần năng lực đã kiểm chứng vào xưởng mới, kiểm mã từng tệp cho chắc nguyên vẹn, gắn tiền tố, tạo hai thư mục `Du an` và `Kho giong`.

**Vài câu hỏi về mục đích và máy của bạn (3 phút).** Bạn muốn giọng của chính mình hay giọng có sẵn; tiếng Việt, tiếng Anh hay cả hai; máy Mac hay Windows; có sẵn lòng dùng dịch vụ trả phí không. Claude đề xuất mô hình phù hợp, nói rõ điểm mạnh và giới hạn của nó, rồi cùng bạn quyết.

**Cài trên máy của bạn (15-60 phút, bạn chỉ chờ).** Claude nhờ bạn bấm đúp một tệp trong thư mục xưởng: `Cai dat tren Mac.command` trên Mac, `Cai dat tren Windows.bat` trên Windows. Một cửa sổ đen hiện ra, tự đo máy, cài Python, tải mô hình, rồi tự kiểm bằng cách đọc thử hai câu. Lần đầu mở:

- Mac báo "không mở được vì từ nhà phát triển không xác định": bấm chuột phải vào tệp, chọn **Open**, rồi **Open** lần nữa
- Windows hiện hộp xanh "Windows protected your PC": bấm **More info**, rồi **Run anyway**

Xong, cửa sổ báo "Cài xong". Quay lại Claude và nhắn "đã cài xong". Có lỗi thì chụp màn hình cửa sổ gửi Claude.

**Khóa API (chỉ khi dùng Gemini hoặc ElevenLabs, 5 phút).** Claude chỉ bạn chỗ lấy khóa, rồi nhờ bạn bấm đúp `Them khoa API` và dán khóa vào cửa sổ đó. Khóa được cất trong kho khóa của máy (Keychain trên Mac, Credential Manager trên Windows). Đừng bao giờ dán khóa vào khung chat.

**Thu giọng của bạn (nếu muốn, khoảng 30 phút).** Claude gửi bạn 5 đoạn ngắn để đọc: câu đồng thuận, giọng trò chuyện, giọng giảng bài, giọng hướng dẫn thực hành, một đoạn tiếng Anh. Thu bằng phần mềm ghi âm có sẵn (QuickTime trên Mac, Voice Recorder trên Windows), thu liền một tệp cũng được, rồi thả vào thư mục Claude chỉ. Claude cắt mẫu, đưa vào kho giọng, rồi dựng một lượt **thi nghe mù**: máy đọc cùng một đoạn bằng từng mẫu, hiện theo chữ cái A, B, C để bạn chấm mà không biết mẫu nào. Mẫu được điểm cao nhất thành giọng chính của bạn.

**Lưu skill vào tài khoản (khoảng 10 phút).** Skill là bản quy trình chuẩn viết cho AI, giống cuốn sổ tay nghề. Claude đóng gói hai skill mang tiền tố của bạn (ví dụ `tma-long-tieng`) để bạn lưu vào tài khoản Claude: bấm nút lưu trên thẻ tệp, hoặc vào **Customize > Skills**, bấm **+**, chọn **Create skill** rồi **Upload a skill**. Lưu rồi thì ở bất kỳ phiên nào, bạn chỉ cần nói "lồng tiếng đoạn này bằng giọng tôi".

## Bước 4: bản lồng tiếng đầu tiên

Chọn một đoạn bạn sắp cần thật (30-60 giây), dán vào khung chat và nói:

> Lồng tiếng đoạn này bằng giọng của tôi, tiếng Việt, dùng cho video khoá học.

Claude soạn lời đọc (chia đoạn theo hơi thở, viết rõ cách đọc số và tên riêng, đặt chỉ dẫn nhịp) để bạn duyệt trên chữ. Bạn gật đầu thì Claude xếp việc và nhờ bạn bấm đúp `Long tieng tren Mac.command` (hoặc `Long tieng tren Windows.bat`). Xong, bấm đúp `Mo ban nghe.command` (hoặc `Mo ban nghe tren Windows.bat`): trang Bàn nghe mở trong trình duyệt, mỗi đoạn có 2-3 lượt đọc, máy đã đánh dấu lượt tốt nhất. Bạn chọn lượt ưng, ghi chú đoạn cần đọc lại, bấm **Ghép bản chính**. Thành phẩm nằm ở `Du an/<tên dự án>/thanh-pham/`.

Cách đặt yêu cầu, cách góp ý cho giọng tự nhiên hơn, và xử lý khi có gì lạ: [HUONG-DAN.md](HUONG-DAN.md).

## Những điều nên biết

- **Mô hình chỉ chạy khi bạn bấm đúp.** Claude làm việc trong một máy ảo nhỏ, không chạy được mô hình; nó xếp việc, còn máy của bạn đọc khi bạn bấm "Long tieng". Giữ máy không ngủ trong lúc chạy
- **Tiếng của bạn không rời máy** khi dùng mô hình tại máy. Chỉ khi chọn Gemini hoặc ElevenLabs, lời đọc mới được gửi tới máy chủ của hãng
- **Chất lượng nằm ở lời đọc nhiều hơn ở mô hình.** Câu ngắn, viết cho tai, số và tên riêng viết rõ cách đọc; xưởng có khuôn lời đọc đã thi nghe cho từng thứ tiếng, Claude tự dùng
- **Chỉ nhân bản giọng của chính bạn**, hoặc của người đã đồng thuận bằng văn bản. Claude sẽ từ chối nhân bản giọng người khác
- **Đổi mô hình về sau:** nói với Claude, nó sửa cấu hình rồi nhờ bạn bấm lại tệp cài đặt; mô hình cũ được gỡ để trả chỗ trống cho ổ đĩa

## Khi có gì không chạy

Nói với Claude điều bạn thấy, bằng lời thường ("cửa sổ cài đặt báo lỗi", "Bàn nghe không mở"), kèm ảnh chụp cửa sổ nếu có. Ba việc bạn tự kiểm được: thư mục xưởng còn được thêm vào phiên Cowork không; máy còn mạng không (lúc cài); ổ đĩa còn chỗ không.
