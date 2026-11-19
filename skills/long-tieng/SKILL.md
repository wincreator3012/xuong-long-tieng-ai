---
name: long-tieng
description: Lồng tiếng AI tiếng Việt và tiếng Anh trong xưởng lồng tiếng dựng từ bản thiết kế xuong-long-tieng-ai: soạn lời đọc có thẻ biểu cảm theo khuôn đã thi nghe, đọc bằng giọng riêng của người dùng (Fish Audio Drama 3) hoặc máy đọc khác khi được bật, xếp việc để người dùng bấm đúp chạy trên máy thật, kiểm bằng gỡ băng ngược, Bàn nghe chọn lượt, ghép thành phẩm chuẩn âm lượng, giao sang xưởng phim; thi nghe mù; thu, đưa vào kho và đăng ký giọng riêng. Kích hoạt khi người dùng nói "lồng tiếng", "voice-off", "voiceover", "đọc thành tiếng", "giọng đọc AI", "đọc bằng giọng tôi", "nhân bản giọng", "thi nghe", "so các máy đọc", "làm bản tiếng Anh có giọng", "thu mẫu giọng", hoặc đưa kịch bản cần thành tiếng, kể cả khi không gọi tên skill. Phim từ file voice có sẵn dùng phim-infomotion, phim-hoat-hoa; gỡ băng dùng phim-transcript.
---

# Lồng tiếng AI

Xưởng biến một kịch bản thành tiếng đọc tự nhiên, biểu cảm, đúng ý người dùng, với ít lần người dùng phải nghe lại nhất. Đọc `CLAUDE.md` của repo trước (hai máy, máy đọc, quy tắc cứng).

## Nguyên lý

Người nghe chỉ nhận ra giọng máy ở 3 chỗ: phát âm sai (tên riêng, số, từ tiếng Anh), nhịp sai (đọc đều đều, ngắt sai chỗ, không có hơi thở), và cảm xúc lệch với lời (đọc vui một câu buồn). Vì vậy chất lượng nằm ở khâu soạn lời đọc và khâu kiểm nhiều hơn ở việc chọn mô hình. Xưởng sinh 2 đến 3 lượt mỗi đoạn để có lựa chọn, máy chấm trước, người dùng chỉ nghe chỗ đáng nghe.

## Quy trình một bản lồng tiếng

1. **Nắm việc.** Hỏi gọn những gì chưa rõ: dùng cho đâu (phim của xưởng phim, podcast, học liệu, quảng bá), thứ tiếng, giọng, tinh thần chung (ấm, chậm, hào hứng...), thời lượng mong muốn. Đoán được thì nêu giả định và làm.
2. **Tạo hồ sơ:** `python3 tools/du_an_moi.py "<Ten khong dau>" --tieu-de "<tiêu đề>" --ngon-ngu vi` (máy đọc mặc định là máy đầu tiên trong `mayDung`, giọng mặc định là `giongRieng` của `cau-hinh.json`; đổi bằng `--may`, `--giong`).
3. **Soạn `loi-doc.md`** theo `references/viet-loi-doc.md` và khuôn đã chốt của thứ tiếng đó: chia đoạn theo hơi thở, thẻ biểu cảm có chừng mực, chỉ dẫn diễn xuất song ngữ, phát âm tên riêng. Viết cho tai, không cho mắt.
4. **Người dùng duyệt lời đọc trên chữ** (gửi bản đọc gọn, không gửi cú pháp thô nếu người dùng không cần), trừ khi người dùng bảo làm luôn.
5. **Xếp việc:** `python3 tools/hang_doi.py them "../Du an/<dự án>"`. Đọc các dòng "cảnh báo" (ngoặc vuông bị bỏ, thẻ lạ) và sửa lời đọc nếu cần.
6. **Nhờ người dùng bấm đúp `Long tieng tren Mac.command` (Windows: `Long tieng tren Windows.bat`)**, nói rõ tên tệp và việc sẽ chạy. Người dùng báo xong thì `python3 tools/hang_doi.py trang-thai`.
7. **Kiểm trước khi đưa người dùng nghe:** đọc `luot/<lượt>/kiem.json` (hoặc `python3 tools/kiem_tieng.py`). Đoạn mà mọi lượt đều "lệch lời nhiều", "không có tiếng", "bị xén đỉnh": sửa lời (thường là phát âm, số, câu quá dài) rồi sinh lại riêng đoạn đó: `them ... --doan d004 --so-luot 3`. Cờ "lệch lời" nhẹ có thể do máy nghe sai; xem "chỗ lệch" trước khi kết luận.
8. **Người dùng nghe ở Bàn nghe** (`Mo ban nghe.command` (Windows: `Mo ban nghe tren Windows.bat`)): chọn lượt, ghi chú đọc lại. Người dùng báo xong thì đọc `chon.json`: ghi chú `lamLai` nào cũng phải xử lý (sửa chỉ dẫn, thẻ, cách đọc, đổi máy đọc cho đoạn đó) rồi sinh lại đoạn ấy.
9. **Ghép bản chính:** người dùng bấm "Ghép bản chính" ở Bàn nghe, hoặc `python3 tools/ghep_tieng.py "../Du an/<dự án>"`. Kiểm `thanh-pham/*.moc.json`: không thiếu đoạn, thời lượng hợp lý.
10. **Giao:** cho phim của xưởng phim thì `--giao-phim "<dự án phim>"` (vào `nguon/voice.wav`; xem quy tắc về tiếng AI trong phim ở `CLAUDE.md`). Ghi bài học mới vào `docs/BAI-HOC.md` khi có (phát âm sai lặp lại, máy đọc hợp loại việc nào).

## Chọn máy đọc

Máy đọc đang bật nằm ở `cau-hinh.json` > `mayDung` (trình cài đặt đề xuất theo cấu hình máy, xem `skills/long-tieng-thiet-lap/references/chon-may-doc.md`); giọng riêng mặc định ở `giongRieng`. Chỉ xếp việc cho máy đang bật; muốn bật thêm máy thì thêm vào `mayDung` rồi nhờ người dùng chạy lại trình cài đặt trên máy thật.

Kết quả thi nghe mù đã có (thang 5, tháng 11/2026, chi tiết ở `docs/BAI-HOC.md`):

| Máy | Tiếng Việt | Tiếng Anh | Chạy ở đâu |
|---|---|---|---|
| `drama3` giọng riêng | 4,5 (khuôn nhịp mạnh) | 5,0 (khuôn ấm và chậm) | Mac chip Apple, nên có 48 GB RAM; luôn cần mẫu giọng |
| `vieneu` | 1,25 (giọng có sẵn), 1,0 (giọng riêng) | 1,25 | mọi máy, CPU; 25 giọng có sẵn tiếng Việt |
| `higgs3` giọng riêng | chưa chấm | 1,5 | Mac chip Apple; giấy phép chỉ cho video, podcast có ghi công |
| `gemini`, `elevenlabs` | chưa thi | chưa thi | đám mây, mọi máy; cần khóa API, tính phí |

Khuôn lời đọc đã thi với Drama 3: tiếng Việt theo `references/mau-nhip-manh.md` (không dặn chậm cả bài), tiếng Anh theo `references/mau-tieng-anh-am.md` (một dòng phong cách, không chỉ dẫn giữa câu). Với máy khác, thi nghe lại trước khi chốt khuôn.

Có thể trộn máy theo đoạn khi xưởng bật nhiều máy: sinh riêng đoạn khó bằng máy khác (`them --may ... --doan ...`), ghép vẫn theo thứ tự kịch bản; giọng riêng trộn nhiều máy thì nghe kỹ độ khớp giọng giữa các đoạn.

Điều kiện: Drama 3 cho sản phẩm có thu tiền cần người dùng xác nhận doanh thu năm (tính cả công ty liên kết) dưới 500.000 USD; Higgs v3 khi phát hành ghi công Boson AI; Gemini và ElevenLabs cần khóa API (`tools/them_khoa.py`, chạy trên máy thật).

## Thi nghe mù

Dùng khi chốt máy đọc lần đầu, khi có mô hình mới, hoặc khi có mẫu giọng mới.

1. Hồ sơ riêng cho mỗi thứ tiếng, kịch bản 60 đến 90 giây gồm câu kể, câu hỏi, một quãng lắng, thuật ngữ chuyên môn, một tên riêng, một con số. Nên dùng đoạn thật người dùng sắp cần.
2. `python3 tools/thi_nghe.py tao "../Du an/<dự án>" --ung-vien "drama3:@an#vi-03" "drama3:@an#vi-02"` (so mẫu giọng), hoặc `"drama3:@an:nhip" "drama3:@an:am"` (so cách viết lời đọc, đọc tệp `kich-ban-<biến thể>.md`), hoặc nhiều máy đang bật (`"vieneu:Thiện Minh" "gemini:Charon"`). Ứng viên chưa có khóa hay chưa đăng ký giọng thì thêm sau bằng `them`.
3. Người dùng bấm đúp `Long tieng tren Mac.command` (Windows: `Long tieng tren Windows.bat`), rồi `Mo ban nghe.command` (Windows: `Mo ban nghe tren Windows.bat`), thẻ "Thi nghe mù": chấm 4 tiêu chí, lưu rồi mới lộ tên.
4. `python3 tools/thi_nghe.py ket-qua ...`; cùng người dùng chốt máy chính và máy dự phòng cho mỗi thứ tiếng, ghi vào `docs/BAI-HOC.md` kèm điểm và ngày.

## Giọng riêng

Hồ sơ ở kho: `giong-noi/giong-noi.json`, tệp ở `giong-noi/<tên>/`. Chỉ giọng của người dùng hoặc người đã đồng thuận bằng văn bản (quy tắc 1). Hồ sơ mới: `python3 tools/giong_rieng.py tao <tên> --ho-ten "<họ tên>" --dong-thuan "<ai cho phép, cho việc gì, ngày nào>"`.

- **Mẫu tạm từ bản ghi sẵn có:** `python3 tools/giong_rieng.py trich <tệp> --transcript <x.transcript.json> --ra <thư mục tạm>` (transcript dạng xưởng phim); nghe hoặc cho người dùng nghe các ứng viên, rồi `them-mau an <tệp> --loi "<lời đúng như trong mẫu>" --ngon-ngu vi --nguon "<gốc>"`. Lời phải khớp từng chữ với tiếng; transcript tự động có thể sai, soát lại trước khi thêm.
- **Mẫu chuẩn:** người dùng thu theo `docs/THU-MAU-GIONG.md` (thu liền cả buổi vào một tệp cũng được). Cắt theo quãng lặng (ffmpeg `silencedetect`), mỗi phần thành mẫu 10 đến 30 giây, gỡ băng rồi soát lời (người đọc hay nói khác bản in một vài chữ: lời mẫu phải theo tiếng thật), `them-mau ...`; câu đồng thuận: `them-dong-thuan an <tệp> --ngon-ngu vi`. Chọn mẫu chính bằng thi nghe mù so mẫu (mục trên), rồi `chon-chinh` và đánh dấu mẫu đã duyệt.
- **Đăng ký đám mây:** `python3 tools/giong_rieng.py dang-ky an --may gemini` (cần câu đồng thuận ghi âm, đọc đúng nguyên văn) hoặc `--may elevenlabs`; việc chạy trên máy thật ở lần bấm đúp kế tiếp, mã giọng tự ghi vào hồ sơ trong kho.

## Khi một khâu hỏng

- Việc báo lỗi: đọc `Du an/_tam/long-tieng/log/<ngày>-<máy>.log` (qua `device_bash`), sửa nguyên nhân, xếp lại. Không đổi máy đọc khi chưa hiểu lỗi.
- Bộ nối mô hình tại máy hỏng sau khi cập nhật thư viện: kiểm phiên bản ghim trong `tools/cai_dat.py` (GOI), đọc lại API mới của thư viện trước khi sửa `tools/may_doc/`.
- Thiếu môi trường hay mô hình ("chưa có môi trường ...", máy đọc đang tắt): nhờ người dùng chạy lại trình cài đặt; trình cài tự đo máy, cài đúng những gì `mayDung` cần, gỡ phần thừa, rồi tự kiểm.
- Máy đọc đọc sai một từ lặp lại: thêm vào `du-lieu/phat-am-de-xuat.json`; người dùng nghe và duyệt thì chuyển sang `ngon-ngu/phat-am.json` của kho.
