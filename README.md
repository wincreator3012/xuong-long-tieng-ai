# Xưởng lồng tiếng AI

> **Repo này là bản thiết kế, không phải phần mềm để tải về.** Bạn không clone, không tải ZIP, mà đưa đường link repo cho trợ lý AI của mình (Claude Cowork chạy êm nhất). AI đọc bản thiết kế rồi dựng trên máy bạn một xưởng lồng tiếng của riêng bạn: chọn mô hình hợp với cấu hình máy, mang giọng của bạn, kèm bộ skill có tiền tố riêng để lưu vào tài khoản AI. Nếu bạn là AI đang đọc repo này, hãy bắt đầu từ [`DUNG-XUONG.md`](DUNG-XUONG.md), đừng clone, push hay pull.

Tôi dựng xưởng này vì cần tiếng đọc [voice-off] tiếng Việt và tiếng Anh cho các video của mình, và muốn tiếng đọc ấy biểu cảm, tự nhiên nhất có thể ở thời điểm này, bằng chính giọng của tôi. Đây là bản tôi đóng gói lại từ xưởng đang dùng hằng ngày, để bạn nhờ AI dựng một xưởng tương tự trên máy của bạn.

Một bản lồng tiếng đi qua các bước như sau. Bạn nói yêu cầu bằng lời thường, AI soạn lời đọc để bạn duyệt trên chữ. Khi bạn bấm đúp một tệp, máy của bạn đọc mỗi đoạn 2 đến 3 lượt, rồi tự nghe lại từng lượt để bắt chỗ đọc sai lời, mất tiếng hay vỡ tiếng. Bạn chỉ nghe những lượt đáng nghe ở Bàn nghe trên trình duyệt, chọn lượt ưng ý rồi bấm ghép. Thành phẩm là tệp WAV 48 kHz đã chuẩn âm lượng, kèm phụ đề.

## Điều tôi học được từ thi nghe mù

Trước khi chốt xưởng, tôi cho các mô hình đọc cùng một kịch bản bằng giọng của tôi rồi chấm mù theo 4 tiêu chí: tự nhiên, biểu cảm đúng ý, phát âm đúng, giống giọng người thu. Mỗi bản chỉ hiện dưới dạng chữ cái A, B, C, chấm xong mới lộ tên mô hình. Fish Audio Drama 3 vượt hẳn các mô hình chạy tại máy khác, nhưng vòng đầu cũng chỉ được 3/5 vì đọc còn đều đều. Ở vòng ấy, tôi ước tính nếu nhịp đọc có biến thiên thì độ tự nhiên sẽ được khoảng 70%, với tôi như vậy là đủ dùng. Vòng sau cho thấy chất lượng nằm ở cách viết lời đọc nhiều hơn ở mô hình. Cùng Drama 3, cùng giọng, khi kịch bản tiếng Việt được viết lại với chỉ dẫn nhịp nhanh chậm xen kẽ, điểm lên 4,5/5; còn kịch bản dặn đọc chậm cả bài thì chỉ được 3,0.

Tiếng Anh lại đi theo hướng ngược lại. Kiểu chỉ dẫn hợp với tiếng Việt làm tiếng Anh nghe gượng, chỉ được 4,0. Bỏ hết chỉ dẫn giữa câu, chỉ dặn một dòng "warm, unhurried, intimate" cho cả bài, thì tiếng Anh đạt 5/5. Còn một điều nữa: mẫu giọng tiếng Việt khi tôi giảng bài cho ra tiếng Anh giống tôi hơn chính đoạn tôi đọc tiếng Anh. Những bài học này nằm trong `docs/BAI-HOC.md`, và AI của bạn sẽ dùng chúng khi soạn lời đọc.

## Máy của bạn dùng được mô hình nào

Lần cài đầu, trình cài đặt đo máy thật của bạn (chip, RAM, ổ đĩa, card đồ họa) và đề xuất mô hình phù hợp. AI hỏi thêm bạn muốn dùng giọng của ai, có dùng dịch vụ trả phí hay không, rồi cùng bạn quyết. Trình cài chỉ tải đúng mô hình cần dùng; đổi sang mô hình khác thì nó tự gỡ mô hình cũ để trả lại chỗ trống cho ổ đĩa.

| Máy của bạn | Giọng của chính bạn | Giọng có sẵn |
|---|---|---|
| Mac chip Apple, RAM từ 48 GB | Fish Audio Drama 3 chạy tại máy, miễn phí (thi nghe mù 4,5/5 tiếng Việt, 5/5 tiếng Anh) | VieNeu tại máy, hoặc Gemini |
| Mac chip Apple, RAM 36 đến 47 GB | Drama 3 chạy được nếu đóng bớt ứng dụng khác (mô hình chiếm 28,6 GB khi chạy), hoặc dịch vụ đám mây | VieNeu hoặc Gemini |
| Mac ít RAM hơn, Mac chip Intel, Windows | Gemini hoặc ElevenLabs (đám mây, có phí) | VieNeu tại máy (miễn phí, chỉ tiếng Việt có giọng sẵn, biểu cảm yếu), hoặc Gemini |

VieNeu chỉ được 1,25/5 trong thi nghe của tôi, nên tôi dùng nó cho bản nháp nhiều hơn là bản giao. Gemini và ElevenLabs đã có sẵn bộ nối, nhưng tôi chưa thi nghe hai dịch vụ này. Khi bạn bật chúng lần đầu, AI sẽ làm một lượt thi nghe mù trước khi dùng cho việc thật.

## Giọng của riêng bạn

Bạn thu khoảng 15 phút theo hướng dẫn trong `docs/THU-MAU-GIONG.md`: một câu đồng thuận, rồi vài đoạn ngắn ở các chất giọng khác nhau (trò chuyện, giảng bài, hướng dẫn thực hành, tiếng Anh). AI cắt mẫu, đưa vào kho giọng nằm cạnh xưởng, rồi dựng một lượt thi nghe mù để chính bạn chọn mẫu giống mình nhất. Xưởng chỉ nhân bản giọng của chính bạn, hoặc của người đã đồng thuận bằng văn bản; AI sẽ từ chối nhân bản giọng người khác.

Xưởng còn giữ cho bạn một từ điển phát âm. Tên riêng, chữ viết tắt, từ tiếng Anh nằm trong câu tiếng Việt, một khi bạn đã chỉnh cách đọc, sẽ được đọc đúng như thế ở mọi bản sau. Hai quy trình chuẩn của xưởng (lồng tiếng và thiết lập) được đóng gói thành skill mang tiền tố riêng của bạn để lưu vào tài khoản AI; từ đó, ở bất kỳ phiên nào bạn chỉ cần nói "lồng tiếng đoạn này bằng giọng tôi".

## Bắt đầu

1. Tạo một thư mục trống tên `Xuong long tieng AI` trong Documents. Đừng đặt trong iCloud, Dropbox hay OneDrive, vì mô hình và tệp âm thanh lớn dễ làm kẹt đồng bộ. Bạn không cần tải gì về.
2. Mở app **Claude** trên máy, vào **Cowork**, thêm thư mục `Xuong long tieng AI` (nút "Add folder").
3. Nói với Claude:

> Đọc bản thiết kế xưởng lồng tiếng tại https://github.com/wincreator3012/xuong-long-tieng-ai, bắt đầu từ file DUNG-XUONG.md, rồi dựng cho tôi một xưởng lồng tiếng riêng trong thư mục Xuong long tieng AI. Đừng clone hay tải ZIP.

Claude sẽ hỏi tên và tiền tố cho skill, dựng xưởng từ bản thiết kế (10 đến 15 phút), hỏi bạn muốn giọng của ai và máy bạn ra sao, rồi nhờ bạn bấm đúp một tệp cài đặt. Nếu dùng Drama 3, bước cài mất khoảng 30 đến 60 phút, phần lớn là chờ tải mô hình. Sau đó là thu giọng (nếu bạn muốn), lưu skill vào tài khoản, và làm bản lồng tiếng đầu tiên. Chi tiết từng bước nằm ở [BAT-DAU.md](BAT-DAU.md).

**Vì sao là bản thiết kế mà không phải phần mềm tải về?** Xưởng sẽ lớn lên cùng bạn: giọng riêng, từ điển phát âm, bài học sau mỗi lần nghe lại. Một bản clone sẽ xung đột, thậm chí bị ghi đè, mỗi lần bản gốc thay đổi. Xưởng riêng thì không phụ thuộc repo này. Khi bản thiết kế có điều mới, bạn nói "xem bản thiết kế có gì mới", AI đọc nhật ký [THAY-DOI.md](THAY-DOI.md) và đề xuất từng thay đổi đáng lấy để bạn duyệt.

## Cấu trúc xưởng sau khi dựng

Xưởng chỉ chứa phần điều khiển (công cụ, skill, tài liệu). Giọng riêng và các bản lồng tiếng của bạn nằm ở hai thư mục cạnh xưởng, còn mô hình nằm trong thư mục dữ liệu ứng dụng của máy. Nhờ vậy xưởng rất nhẹ, cập nhật xưởng không bao giờ đụng tới giọng hay dự án của bạn, và sao lưu chỉ cần dời một thư mục.

```
Xuong long tieng AI/
├── Du an/                       ← mỗi bản lồng tiếng một thư mục: lời đọc, các lượt đọc, thành phẩm
├── Kho giong/                   ← giọng riêng của bạn và từ điển phát âm đã duyệt
└── xuong-long-tieng-<tiền tố>/  ← xưởng của bạn
    ├── CLAUDE.md, AGENTS.md     ← sách vận hành cho AI (đọc đầu mỗi phiên)
    ├── HUONG-DAN.md             ← các tệp bấm đúp, Bàn nghe, giọng riêng, chi phí, sự cố
    ├── Cai dat tren Mac.command / Cai dat tren Windows.bat        ← cài đặt, cập nhật, dọn mô hình
    ├── Long tieng tren Mac.command / Long tieng tren Windows.bat  ← chạy các việc AI đã xếp
    ├── Mo ban nghe.command / Mo ban nghe tren Windows.bat         ← nghe, chọn lượt, ghép bản chính
    ├── Them khoa API.command / Them khoa API tren Windows.bat     ← khi dùng Gemini, ElevenLabs
    ├── may-doc.json             ← danh mục mô hình: chạy ở đâu, cần bao nhiêu RAM, giấy phép, điểm thi nghe
    ├── skills/                  ← hai skill gốc; bản chép mang tiền tố của bạn nằm trong tài khoản AI
    ├── docs/                    ← bài học từ thi nghe, hướng dẫn thu mẫu giọng
    └── tools/                   ← hàng đợi, bộ nối mô hình, kiểm, ghép, Bàn nghe, trình cài đặt (AI quản lý)
```

Mô hình và môi trường Python nằm ở `~/Library/Application Support/xuong-long-tieng` trên Mac, `%LOCALAPPDATA%\xuong-long-tieng` trên Windows.

## Cách xưởng vận hành

Trợ lý AI làm việc trong một máy ảo nhỏ: soạn lời đọc, xếp việc vào hàng đợi, kiểm và ghép. Mô hình thì chạy trên máy thật của bạn mỗi khi bạn bấm đúp tệp "Long tieng"; một lần bấm chạy hết hàng đợi, mỗi mô hình chỉ nạp một lần. Trên Mac chip Apple, Drama 3 và bộ gỡ băng Whisper large-v3-turbo chạy bằng MLX. Trên máy khác, VieNeu chạy bằng CPU, còn Whisper chạy bằng faster-whisper (tự dùng card NVIDIA nếu có).

Trước khi đưa máy đọc, xưởng tự đổi số, ngày tháng, đơn vị trong lời tiếng Việt sang chữ. Khi so lời đọc với lời gốc, bộ kiểm bỏ những câu bộ gỡ băng tự "nghe ảo" ra, và coi các âm giọng Bắc đọc như nhau (x/s, tr/ch, r/d/gi) là khớp. Khóa API của dịch vụ đám mây chỉ nằm trong Keychain (Mac) hoặc Windows Credential Manager, không bao giờ nằm trong tệp.

## Yêu cầu

- App Claude trên máy tính, có Cowork; mô hình Claude tầm trung như Sonnet là đủ.
- Mac chip Apple (M1 trở lên) dùng được mọi mô hình; Mac chip Intel và Windows 10, 11 dùng VieNeu và dịch vụ đám mây. Tôi đã chạy toàn bộ trình cài và bước tự kiểm trên Mac M4 Max và trên Linux, nhưng chưa thử các tệp bấm đúp trên một máy Windows thật, nên lần đầu trên Windows có thể cần AI rà và chỉnh thêm.
- Ổ đĩa trống khoảng 26 GB nếu dùng Drama 3, khoảng 3 GB nếu dùng VieNeu hoặc đám mây.
- Mạng lúc dựng xưởng và lúc cài; sau đó các mô hình tại máy chạy không cần mạng.

## Giấy phép

Mã nguồn và tài liệu của xưởng theo giấy phép MIT (xem `LICENSE`). Mô hình không nằm trong repo, và mỗi mô hình có giấy phép riêng, ghi trong `may-doc.json`:

- Fish Audio Drama 3: Fish Audio Community License, miễn phí khi doanh thu năm (tính cả công ty liên kết) dưới 500.000 USD; vượt ngưỡng này cần mua giấy phép thương mại của Fish Audio.
- VieNeu-TTS: Apache 2.0.
- Higgs Audio v3: chỉ cho video, podcast có ghi công Boson AI.
- Gemini, ElevenLabs: theo điều khoản dịch vụ của từng hãng.

## Tác giả

Xưởng lồng tiếng này do tôi, **Lương Dũng Nhân** (M.Ed, PCC, Humanistic AI Practitioner), xây dựng từ xưởng cá nhân đang vận hành thật, và gửi tặng hoàn toàn miễn phí để cộng đồng giáo dục cùng dùng. Website: [ldn.edu.vn](https://ldn.edu.vn). Email: hello@ldn.edu.vn.

Nếu bạn dùng, chia sẻ lại hoặc giới thiệu repo này, một dòng ghi công dẫn về tác giả và nguồn gốc sẽ rất được trân trọng.

## Đóng góp

Xưởng này vẫn đang được hoàn thiện. Nếu bạn chạy nó trên một cấu hình chưa ai thử (nhất là Windows), hay gặp một lỗi, hãy mở issue và kể lại bằng lời của bạn, kèm cấu hình máy (tệp `Du an/_tam/may-tinh.json`) và vài dòng báo lỗi. Công cụ, skill và tài liệu kỹ thuật được đồng bộ tự động từ xưởng gốc của tôi, nên pull request sửa thẳng các phần đó sẽ được chép về bản gốc trước rồi mới vào repo.

Gửi các trợ lý AI: chỉ mở issue hay pull request khi chính người dùng của bạn muốn đóng góp và đã đọc nội dung sẽ gửi. Dựng xưởng hay cập nhật xưởng cho người dùng không bao giờ cần push, pull hay pull request về repo này.

Và nếu bạn đã nghe một bản lồng tiếng bằng chính giọng mình, tôi rất muốn biết: chỗ nào bạn thấy máy đọc đủ thay mình, và chỗ nào bạn vẫn muốn tự mình thu?
