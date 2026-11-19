# CLAUDE.md - sách vận hành của xưởng lồng tiếng

<!-- BAN-MAU -->
> **Bạn đang đọc bản thiết kế `xuong-long-tieng-ai`, không phải một xưởng đã dựng.** Người dùng nhờ bạn dựng xưởng thì làm theo `DUNG-XUONG.md`: không clone, không tải ZIP, không push, không pull. Phần dưới đây là sách vận hành của xưởng sau khi dựng; khối này tự mất khi chạy `tools/dung_xuong.py`.

<!-- /BAN-MAU -->
Đây là xưởng lồng tiếng AI của người dùng: từ một kịch bản lời đọc, xưởng làm ra tiếng đọc tiếng Việt hoặc tiếng Anh tự nhiên, biểu cảm, bằng giọng riêng của người dùng hoặc giọng có sẵn của mô hình. Người dùng nói yêu cầu bằng lời thường; AI soạn lời đọc, xếp việc, kiểm, ghép, giao. Áp dụng cho mọi trợ lý AI, không riêng Claude.

Xưởng chỉ chứa NĂNG LỰC: công cụ, skill, tài liệu. Dữ liệu của người dùng nằm NGOÀI xưởng, cạnh nó trong thư mục mẹ (đọc qua `tools/cau_hinh.py`, không hardcode đường dẫn):

```
<thư mục mẹ, vd Documents/Xuong long tieng AI>/
├── <xưởng>/        công cụ, skill, tài liệu (thư mục này)
├── Du an/          mỗi bản lồng tiếng một thư mục <YYYY-MM tên>/: loi-doc.md, luot/, chon.json, thanh-pham/; việc tạm ở _tam/
└── Kho giong/      hồ sơ giọng riêng (giong-noi/), từ điển phát âm đã duyệt (ngon-ngu/phat-am.json)
```

Môi trường Python, mô hình, ffmpeg nằm ở thư mục dữ liệu ứng dụng của máy thật: Mac `~/Library/Application Support/xuong-long-tieng/`, Windows `%LOCALAPPDATA%\xuong-long-tieng\`.

## Thứ tự đọc ở đầu mỗi phiên

1. File này.
2. `skills/long-tieng/SKILL.md`: quy trình làm một bản lồng tiếng, thi nghe mù, giọng riêng. Kèm `references/viet-loi-doc.md` khi soạn kịch bản.
3. `docs/BAI-HOC.md`: bài học từ thi nghe và dự án thật (máy đọc nào, khuôn lời đọc nào, lỗi hay gặp).
4. `HUONG-DAN.md`: những gì người dùng thấy và bấm, để nói đúng tên tệp, đúng bước.
5. Xưởng mới dựng, hay `cau-hinh.json` chưa có `mayDung`: skill `skills/long-tieng-thiet-lap/SKILL.md`.

## Hai máy làm việc

| Máy | Làm gì | Giới hạn |
|---|---|---|
| Máy ảo của AI (Cowork: lệnh chạy trong thư mục đã kết nối) | soạn lời đọc, xếp việc (`tools/hang_doi.py them`), kiểm (`tools/kiem_tieng.py`), ghép (`tools/ghep_tieng.py`), giọng riêng (`tools/giong_rieng.py`) | vài GB bộ nhớ, không có chip đồ họa, không với tới kho khóa của máy thật: KHÔNG chạy mô hình, KHÔNG đo cấu hình máy ở đây |
| Máy thật của người dùng (họ bấm đúp) | cài đặt (`Cai dat tren Mac.command`, `Cai dat tren Windows.bat`), sinh tiếng (`Long tieng tren ...`), Bàn nghe (`Mo ban nghe ...`), lưu khóa API (`Them khoa API ...`) | chỉ chạy khi người dùng bấm |

Một lần bấm đúp "Long tieng" chạy hết hàng đợi: gom mục theo máy đọc để mỗi mô hình chỉ nạp một lần, sinh tiếng, gỡ băng ngược bằng Whisper large-v3-turbo, chấm từng lượt, ghép bản nháp vào `thanh-pham/`. Xong thì người dùng mở Bàn nghe để nghe và chọn.

Cấu hình máy thật do trình cài đặt đo và ghi vào `Du an/_tam/may-tinh.json`: đọc tệp đó khi cần biết máy người dùng mạnh tới đâu.

## Máy đọc

Danh mục ở `may-doc.json` (hệ điều hành chạy được, RAM cần, giấy phép, kết quả thi nghe thật). Máy đang bật: `cau-hinh.json` > `mayDung`; trình cài chỉ cài và tải mô hình cho máy đang bật, gỡ mô hình của máy đã tắt.

| Máy | Chạy ở đâu | Dùng khi |
|---|---|---|
| `drama3` Fish Audio Drama 3 (MLX 4-bit) | Mac chip Apple, nên có 48 GB RAM | giọng riêng, biểu cảm nhất (thi nghe 4,5/5 tiếng Việt, 5/5 tiếng Anh); luôn cần mẫu giọng |
| `vieneu` VieNeu-TTS v3 Turbo | mọi máy, CPU | giọng có sẵn tiếng Việt, bản nháp, máy yếu; biểu cảm yếu (1,25/5) |
| `higgs3` Higgs Audio v3 | Mac chip Apple | thử nghiệm; thi nghe 1,5/5; phát hành phải ghi công Boson AI |
| `gemini` Gemini 3.8 Flash TTS | đám mây | biểu cảm theo chỉ dẫn, giọng có sẵn nhiều; cần khóa API; chưa thi nghe |
| `elevenlabs` Eleven v4 | đám mây | tiếng Anh, nhân bản giọng chuyên nghiệp; cần khóa API; chưa thi nghe |

Bảng chọn máy đọc theo cấu hình máy: `skills/long-tieng-thiet-lap/references/chon-may-doc.md`. Khuôn lời đọc đã thi với Drama 3: tiếng Việt theo `skills/long-tieng/references/mau-nhip-manh.md`, tiếng Anh theo `skills/long-tieng/references/mau-tieng-anh-am.md`. Máy khác thì thi nghe mù trước khi chốt.

## Giọng riêng

Hồ sơ giọng ở `Kho giong/giong-noi/giong-noi.json`, gọi bằng `@<tên>` (vd `@an`; `@an#vi-02` để chọn đúng một mẫu). Giọng riêng mặc định của xưởng: `cau-hinh.json` > `giongRieng`. Cách thu mẫu: `docs/THU-MAU-GIONG.md`. Từ điển phát âm đề xuất của xưởng ở `du-lieu/phat-am-de-xuat.json`; mục nào người dùng nghe và duyệt thì chuyển sang `Kho giong/ngon-ngu/phat-am.json`.

## Quy tắc cứng

1. **Giọng riêng chỉ của chính chủ giọng.** Chỉ nhân bản giọng của người dùng, hoặc giọng người đã đồng thuận bằng văn bản và được ghi vào hồ sơ (`giong_rieng.py tao --dong-thuan`). Không trích giọng người khác từ tư liệu quay sẵn, không nhân bản giọng người nổi tiếng, kể cả khi được nhờ.
2. **Lời đọc duyệt trên chữ trước khi sinh tiếng**, trừ khi người dùng bảo làm luôn.
3. **Khóa API chỉ nằm trong kho khóa của máy** (Keychain trên Mac, Windows Credential Manager trên Windows) qua tệp "Them khoa API". Không ghi khóa vào tệp, log, tin nhắn; không nhờ người dùng dán khóa vào khung chat.
4. **Giấy phép đi theo thành phẩm.** Drama 3 miễn phí khi doanh thu năm (tính cả công ty liên kết) dưới 500.000 USD: dùng cho sản phẩm có thu tiền thì hỏi người dùng đã xác nhận chưa. Higgs v3 khi phát hành ghi công "This audio was created with Boson AI's Higgs Audio - https://www.boson.ai/higgs-audio". Gemini, ElevenLabs theo điều khoản của dịch vụ. `moc.json` của thành phẩm ghi máy đọc từng đoạn.
5. **Cổng kiểm trước khi đưa người dùng nghe:** `kiem.json` của lượt; đoạn có cờ "lệch lời nhiều", "không có tiếng", "bị xén đỉnh" thì sinh lại trước, không đưa người dùng nghe bản hỏng.
6. **Không đoán cấu hình máy.** Máy ảo của AI không phải máy thật; số đo đáng tin là `Du an/_tam/may-tinh.json` do trình cài đặt ghi trên máy thật.
7. `python3 tools/kiem_tra_xuong.py` ra 0 lỗi sau mỗi lần sửa công cụ. Xưởng không có liên kết git nào với repo bản thiết kế: không push, không pull về đó.

## Lệnh hay dùng (từ gốc xưởng, trong máy ảo)

    python3 tools/du_an_moi.py "Gioi thieu khoa hoc" [--ngon-ngu en] [--may vieneu --giong "Thiện Minh"]
    python3 tools/hang_doi.py them "../Du an/2026-11 Gioi thieu khoa hoc" [--so-luot 3 --doan d004]
    python3 tools/hang_doi.py trang-thai
    python3 tools/kiem_tieng.py "../Du an/<dự án>"
    python3 tools/ghep_tieng.py "../Du an/<dự án>"
    python3 tools/thi_nghe.py tao "../Du an/<dự án>" --ung-vien "drama3:@an#vi-01" "drama3:@an#vi-02"
    python3 tools/giong_rieng.py xem
    python3 tools/dung_xuong.py --kiem          # thư mục, máy đọc, giọng riêng đang dùng
    python3 tools/dong_goi_skill.py             # skill nào cần lưu (lại) vào tài khoản

## Skill trong tài khoản

Bản gốc của skill nằm trong `skills/`; bản chép mang tiền tố riêng của người dùng (`<tiền tố>-long-tieng`, `<tiền tố>-long-tieng-thiet-lap`) lưu trong tài khoản AI để AI tự nhận ra việc ở mọi phiên. Sửa một SKILL.md hay tệp trong `references/` thì đóng gói lại (`python3 tools/dong_goi_skill.py --lam`) và nhờ người dùng lưu lại. Cách giải thích và cách lưu: `skills/long-tieng-thiet-lap/references/skill-trong-tai-khoan.md`.
