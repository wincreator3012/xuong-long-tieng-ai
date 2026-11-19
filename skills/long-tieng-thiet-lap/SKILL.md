---
name: long-tieng-thiet-lap
description: Dựng và thiết lập xưởng lồng tiếng AI cho người dùng mới từ bản thiết kế xuong-long-tieng-ai - cá nhân hoá xưởng (tên, tiền tố skill), hỏi mục đích và cấu hình máy để chọn máy đọc phù hợp (Drama 3 cho Mac mạnh, VieNeu hoặc dịch vụ đám mây cho máy khác), nhờ người dùng chạy trình cài đặt trên Mac hoặc Windows, lưu khóa API, thu và đưa mẫu giọng riêng vào kho, thi nghe mù chọn mẫu chính, đóng gói skill để lưu vào tài khoản, rồi làm bản lồng tiếng đầu tiên. Kích hoạt khi người dùng nói "dựng xưởng lồng tiếng", "thiết lập xưởng lồng tiếng", "cài đặt xưởng", "máy tôi dùng được mô hình nào", "đổi máy đọc", "thu giọng của tôi", "skill là gì", "lưu skill vào tài khoản", "xưởng làm được gì", hoặc khi xưởng chưa có tools/.dung-xuong.json, cau-hinh.json chưa có mayDung, hay Kho giong chưa có hồ sơ giọng nào.
---

# Thiết lập xưởng lồng tiếng lần đầu

Mục tiêu: sau 45-90 phút (phần lớn là chờ tải mô hình), người dùng có một xưởng RIÊNG chạy được trên máy của họ, với máy đọc hợp cấu hình máy và mục đích; giọng riêng của họ đã vào kho (nếu họ muốn); các skill đã nằm trong tài khoản AI; họ hiểu xưởng làm được gì, giới hạn ở đâu, và đã nghe bản lồng tiếng đầu tiên. Nguyên tắc: hỏi ít, mỗi lượt tối đa 4 câu, luôn có phương án mặc định, giải thích bằng lời thường. Người dùng vắng mặt thì chọn mặc định và ghi rõ giả định.

## Bước 0 - định vị

Đọc `CLAUDE.md` ở gốc xưởng. Xác định nơi chạy lệnh (shell trong thư mục đã kết nối của người dùng). Chưa kết nối thư mục thì dừng, hướng dẫn người dùng tạo thư mục mẹ (ví dụ `Documents/Xuong long tieng AI`, không đặt trong iCloud, Dropbox, OneDrive) và thêm vào phiên (Cowork: nút "Add folder").

Xưởng phải là xưởng RIÊNG dựng theo `DUNG-XUONG.md` của bản thiết kế (GitHub: wincreator3012/xuong-long-tieng-ai), không phải bản clone. Chưa có `tools/.dung-xuong.json` thì làm Bước 1-3 của `DUNG-XUONG.md` trước. `python3 tools/dung_xuong.py --kiem` cho biết trạng thái.

## Bước 1 - hỏi mục đích và máy (một lượt)

Hỏi bằng lựa chọn có sẵn (AskUserQuestion nếu có):

1. **Giọng nào:** giọng của chính bạn (cần thu mẫu khoảng 15 phút), giọng có sẵn của mô hình, hay cả hai.
2. **Thứ tiếng:** tiếng Việt, tiếng Anh, cả hai.
3. **Máy:** Mac hay Windows; Mac thì chip và RAM (menu Apple > About This Mac), Windows thì RAM và có card NVIDIA không. Người dùng không biết thì để trình cài đặt đo.
4. **Dịch vụ trả phí:** sẵn lòng dùng Gemini hoặc ElevenLabs (tính phí theo lượng chữ, cần tạo khóa API) hay chỉ muốn chạy miễn phí tại máy.

## Bước 2 - chọn máy đọc

Đọc `references/chon-may-doc.md` và đề xuất bằng lời thường: máy đọc nào, vì sao, giới hạn gì (nói thẳng điểm thi nghe; VieNeu biểu cảm yếu; Gemini, ElevenLabs chưa được xưởng gốc thi nghe). Người dùng đồng ý thì ghi vào `cau-hinh.json`:

- `mayDung`: danh sách máy đọc, máy đầu là mặc định cho dự án mới (vd `["drama3"]`, `["vieneu", "gemini"]`).
- Chưa rõ máy mạnh tới đâu: để trống `mayDung`; trình cài đặt sẽ đo máy thật, đề xuất theo phần cứng và ghi vào. Sau khi cài, đọc `Du an/_tam/may-tinh.json` rồi điều chỉnh cùng người dùng nếu mục đích của họ cần máy khác.

## Bước 3 - cài trên máy thật

Nhờ người dùng bấm đúp trong thư mục xưởng: `Cai dat tren Mac.command` (Mac) hoặc `Cai dat tren Windows.bat` (Windows). Báo trước:

- Lần đầu mở, Mac có thể báo "không mở được vì từ nhà phát triển không xác định": bấm chuột phải vào tệp, chọn Open, rồi Open lần nữa. Windows có thể hiện hộp xanh SmartScreen: bấm "More info" rồi "Run anyway".
- Thời gian: Drama 3 tải khoảng 26 GB (30-60 phút tùy mạng); VieNeu và đám mây khoảng 3 GB (10-15 phút). Cửa sổ chạy xong tự kiểm: mỗi máy đọc tại máy đọc một câu tiếng Việt, một câu tiếng Anh, rồi gỡ băng ngược.
- Lỗi thì chụp màn hình hoặc chép vài dòng cuối gửi AI. Bấm lại bao nhiêu lần cũng được: bước đã xong tự bỏ qua.

Người dùng báo xong: đọc `Du an/_tam/may-tinh.json` (cấu hình thật), `python3 tools/hang_doi.py trang-thai`, và `kiem.json` trong `Du an/_kiem-may/*/luot/*/` (lệch lời, tốc độ). Mời người dùng nghe hai câu thử ở đó nếu muốn.

Bật Gemini hoặc ElevenLabs: nhờ người dùng bấm đúp `Them khoa API.command` (Mac) hoặc `Them khoa API tren Windows.bat`, dán khóa vào cửa sổ đó (khóa không hiện ra, lưu vào kho khóa của máy). Không bao giờ nhờ dán khóa vào khung chat.

## Bước 4 - giọng riêng (nếu người dùng muốn)

1. **Đồng thuận trước.** Chỉ nhân bản giọng của chính người dùng, hoặc người đã đồng thuận bằng văn bản. Tạo hồ sơ: `python3 tools/giong_rieng.py tao <tên> --ho-ten "<họ tên>" --dong-thuan "<chủ giọng tự yêu cầu dùng giọng mình cho sản phẩm của mình, ngày ...>"`, rồi ghi `"giongRieng": "@<tên>"` vào `cau-hinh.json`. Tên hồ sơ: chữ thường không dấu (vd `an`, `minh-anh`).
2. **Thu mẫu** theo `docs/THU-MAU-GIONG.md` (gửi người dùng nội dung cần đọc). Thu liền một tệp cũng được. Nhờ họ thả tệp vào `Du an/_tam/thu-giong/`.
3. **Cắt và gỡ băng.** Tìm quãng lặng (`ffmpeg -af silencedetect=noise=-35dB:d=1.2`), cắt mỗi phần thành mẫu 10 đến 30 giây (WAV mono 48 kHz). Gỡ băng trên máy thật: `python3 tools/hang_doi.py go-bang <các tệp mẫu> --ngon-ngu vi` rồi nhờ người dùng bấm đúp tệp "Long tieng"; kết quả ở `<tệp>.gb.json`. Soát lời theo bản in, nhưng giữ đúng chữ người dùng thật sự nói (người đọc hay nói khác bản in vài chữ; lời mẫu phải khớp tiếng). Bỏ câu "cảm ơn các bạn đã theo dõi" nếu bộ gỡ băng tự thêm ở cuối.
4. **Đưa vào kho:** `python3 tools/giong_rieng.py them-mau <tên> <tệp> --loi "<lời>" --ngon-ngu vi --ma vi-01 --nguon "<ghi chú>"`; câu đồng thuận: `them-dong-thuan <tên> <tệp> --ngon-ngu vi` (Gemini cần).
5. **Chọn mẫu chính bằng thi nghe mù:** mỗi thứ tiếng một dự án, kịch bản theo khuôn đã chốt (`skills/long-tieng/references/mau-nhip-manh.md` cho tiếng Việt, `mau-tieng-anh-am.md` cho tiếng Anh), ứng viên là từng mẫu: `python3 tools/thi_nghe.py tao "../Du an/<dự án>" --ung-vien "drama3:@<tên>#vi-01" "drama3:@<tên>#vi-02" ...`. Với tiếng Anh, cho cả mẫu tiếng Việt dự thi: ở xưởng gốc, mẫu tiếng Việt giọng giảng bài cho tiếng Anh giống người thu hơn chính đoạn họ đọc tiếng Anh. Người dùng bấm "Long tieng" rồi "Mo ban nghe", thẻ "Thi nghe mù", chấm 4 tiêu chí. Xong: `python3 tools/thi_nghe.py ket-qua ...`, `giong_rieng.py chon-chinh <tên> <mã> --ngon-ngu vi|en`, đánh dấu mẫu thắng là đã duyệt (sửa `trangThai` thành `duyet` trong `Kho giong/giong-noi/giong-noi.json`), ghi kết quả vào `docs/BAI-HOC.md`.

Máy đọc đám mây cần đăng ký giọng một lần: `python3 tools/giong_rieng.py dang-ky <tên> --may gemini|elevenlabs`, chạy ở lần bấm "Long tieng" kế tiếp.

## Bước 5 - skill vào tài khoản

Đọc `references/skill-trong-tai-khoan.md`. Giải thích bốn ý (skill là gì; hai nơi skill sống; tên mang tiền tố của bạn; skill cần thư mục xưởng), mỗi lượt một ý ngắn. Rồi `python3 tools/dong_goi_skill.py --lam --tat-ca`, gửi các tệp `.skill` kèm hướng dẫn lưu, chờ người dùng lưu xong, `python3 tools/dong_goi_skill.py --da-luu --tat-ca`. Người dùng muốn để sau: vẫn đóng gói sẵn, nói rõ tệp nằm ở đâu và câu để gọi lại ("lưu skill vào tài khoản").

## Bước 6 - giới thiệu và bản lồng tiếng đầu tiên

Trình bày ngắn (một lượt), cá nhân hoá theo lựa chọn ở Bước 1:

- **Xưởng làm được gì:** từ kịch bản ra tiếng đọc tiếng Việt, tiếng Anh, bằng giọng riêng hoặc giọng có sẵn; sinh 2-3 lượt mỗi đoạn, máy tự chấm bằng gỡ băng ngược, người dùng chỉ nghe chỗ đáng nghe ở Bàn nghe; ghép thành phẩm WAV 48 kHz chuẩn âm lượng kèm phụ đề.
- **Một bản chạy thế nào:** nói yêu cầu, duyệt lời đọc trên chữ, bấm đúp "Long tieng", nghe và chọn ở Bàn nghe, bấm "Ghép bản chính".
- **Dùng hiệu quả:** chất lượng nằm ở lời đọc nhiều hơn ở mô hình (viết cho tai, câu ngắn, số và tên riêng viết rõ cách đọc); góp ý theo đoạn ("đoạn 3 chậm hơn, nhấn chữ buông"); dặn "từ nay luôn..." để AI ghi vào bài học.
- **Giới hạn nói thẳng:** máy đọc tại máy chỉ chạy khi người dùng bấm đúp; Drama 3 cần Mac mạnh; VieNeu biểu cảm yếu; dịch vụ đám mây tốn phí và gửi lời đọc ra ngoài; giọng AI chưa thay được giọng thật ở những chỗ cần cảm xúc sâu.

Rồi mời làm ngay một bản thật ngắn (30-60 giây, đoạn họ sắp cần), theo skill `long-tieng`. Câu gợi ý: "Lồng tiếng đoạn giới thiệu này bằng giọng của tôi, tiếng Việt, dùng cho video khoá học".

## Khi người dùng muốn đổi máy đọc về sau

Theo mục "Đổi máy đọc về sau" của `references/chon-may-doc.md`: sửa `mayDung`, nhờ chạy lại trình cài đặt (tự tải máy mới, gỡ mô hình máy đã bỏ), làm một lượt thi nghe mù nếu máy mới chưa được thi.
