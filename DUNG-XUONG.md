# DỰNG XƯỞNG: hướng dẫn cho AI dựng một xưởng lồng tiếng riêng từ bản thiết kế này

Tài liệu này viết cho trợ lý AI (Claude Cowork, Claude Code, Codex, ChatGPT, Antigravity...) mà một người dùng nhờ "dựng xưởng lồng tiếng theo repo xuong-long-tieng-ai". Đọc trọn một lượt trước khi ghi bất cứ tệp nào. Người dùng thường mới dùng AI: nói với họ bằng lời thường, hỏi ít, mỗi lượt tối đa bốn câu, luôn có phương án mặc định.

## Repo này là gì, và không phải là gì

Repo này là **bản thiết kế** [blueprint] của một xưởng lồng tiếng cùng AI đã vận hành thật: công cụ, quy trình (skill), khuôn lời đọc đã thi nghe mù, bài học. Việc của bạn là dựng cho người dùng **một xưởng riêng** trên máy họ: máy đọc hợp cấu hình máy của họ, giọng riêng của họ, bộ skill có tiền tố riêng trong tài khoản AI của họ.

Repo này **không phải** phần mềm để clone, fork, push hay pull:

- Không `git clone`, không fork, không tải ZIP vào thư mục của người dùng.
- Không tạo remote trỏ về repo này, không push, không pull, không mở issue hay pull request thay người dùng.
- Xưởng dựng xong không có liên kết git nào với repo này.

Vì sao: xưởng sẽ lớn lên theo chính người dùng (giọng riêng, từ điển phát âm, bài học, skill được tinh chỉnh). Một bản clone sẽ xung đột hoặc bị ghi đè mỗi lần bản thiết kế đổi; một xưởng riêng thì tiếp nhận cái mới có chọn lọc, từng thay đổi do người dùng duyệt (mục cuối).

## Kết quả cần có khi xong

```
<thư mục mẹ, mặc định Documents/Xuong long tieng AI>/
├── <tên xưởng>/    ← xưởng riêng: công cụ, skill, tài liệu (không có .git trỏ về đây)
├── Du an/          ← hồ sơ mỗi bản lồng tiếng
└── Kho giong/      ← hồ sơ giọng riêng, từ điển phát âm đã duyệt
```

Cùng với đó: trình cài đặt đã chạy trên máy thật và tự kiểm đạt; máy đọc đã chọn theo cấu hình máy và mục đích; giọng riêng đã vào kho nếu người dùng muốn; hai skill đã đóng gói với tiền tố riêng và người dùng đã lưu vào tài khoản; người dùng đã nghe bản lồng tiếng đầu tiên.

## Bước 0: hiểu bản thiết kế (chỉ đọc)

Đọc trên GitHub, theo thứ tự: `README.md`, `CLAUDE.md` (cách xưởng vận hành, quy tắc cứng), `skills/long-tieng-thiet-lap/SKILL.md` (thiết lập sau khi dựng), `skills/long-tieng-thiet-lap/references/chon-may-doc.md` (chọn máy đọc theo máy), `BAN-DO-TEP.json` (danh sách tệp). Địa chỉ đọc nguyên văn một tệp: `https://raw.githubusercontent.com/wincreator3012/xuong-long-tieng-ai/main/<đường dẫn>`.

Kiểm môi trường của chính bạn:

- Có shell chạy trong thư mục người dùng đã kết nối không. Chưa có thư mục nào thì nhờ người dùng tạo thư mục mẹ và thêm vào (Cowork: nút "Add folder").
- Shell đó ra được GitHub không: thử lấy `https://raw.githubusercontent.com/wincreator3012/xuong-long-tieng-ai/main/BAN-DO-TEP.json`.
- Có `python3` không.

Lưu ý quan trọng: shell của bạn thường chạy trong một máy ảo, không phải máy thật của người dùng. Mô hình lồng tiếng chạy trên máy thật, qua các tệp người dùng bấm đúp. Đừng đo RAM hay chip trong máy ảo rồi kết luận về máy của họ.

## Bước 1: hỏi người dùng (một lượt)

1. **Thư mục mẹ** đặt xưởng: mặc định `Documents/Xuong long tieng AI`. Không đặt trong iCloud, Dropbox, OneDrive: mô hình và tệp âm thanh lớn làm kẹt đồng bộ.
2. **Tiền tố skill**: 2-6 chữ thường không dấu, mặc định chữ cái đầu họ tên (Trần Minh An thành `tma`). Giải thích một câu: hai skill của xưởng khi lưu vào tài khoản sẽ mang tiền tố này (`tma-long-tieng`).
3. **Tên xưởng** (tên thư mục): mặc định `xuong-long-tieng-<tiền tố>`.

Người dùng vắng mặt: dùng mặc định, ghi rõ giả định trong tin nhắn cuối.

## Bước 2: dựng khung và chép năng lực

1. Lấy mã commit mới nhất: `https://api.github.com/repos/wincreator3012/xuong-long-tieng-ai/commits/main`, trường `sha`. Không gọi được thì dùng `main` và ghi rõ.
2. Đọc `BAN-DO-TEP.json` ở đúng mã đó. Với MỖI tệp có `"vai": "chep"`:
   - lấy nội dung theo mẫu địa chỉ `raw` (thay `{ref}` bằng mã commit, `{p}` bằng đường dẫn đã mã hoá URL, khoảng trắng thành `%20`), lấy theo byte. Không dùng công cụ "đọc trang web" có tóm tắt: nó không trả nguyên văn;
   - kiểm `sha`: sha1 của `blob <cỡ>\0` nối với nội dung (giống `git hash-object`). Lệch thì lấy lại; ba lần vẫn lệch thì dừng và báo người dùng;
   - ghi vào `<tên xưởng>/<đường dẫn>` theo đúng byte (tệp `.bat` giữ xuống dòng kiểu Windows), tạo thư mục cha nếu thiếu; tệp có `"chay": true` thì cấp quyền chạy.

   Cách gọn nhất: một vòng lặp ngắn bằng python (`urllib`, `hashlib`) chạy trong shell. Shell giới hạn thời gian mỗi lệnh thì chia lượt: bỏ qua tệp đã có và đúng `sha`, chạy lại tới khi đủ.
3. Không chép tệp `"vai": "ban-mau"`. Không tạo `.git`.
4. Kiểm: số tệp đã ghi bằng `so_tep_chep`, mọi `sha` khớp.

Vì sao chép nguyên văn phần công cụ mà không tự viết lại: hàng đợi, bộ nối máy đọc, bộ kiểm bằng gỡ băng ngược và trình cài đặt đã chạy thật trên Mac và Linux, có máy tự kiểm đi kèm; viết lại từ đầu rất dễ sinh lỗi khó thấy (đọc sai số, lệch lời, gỡ nhầm mô hình). Phần làm nên một xưởng RIÊNG nằm ở bước 3 đến 5: máy đọc, giọng, từ điển phát âm, skill có tiền tố.

Shell trên máy người dùng không ra được GitHub: lấy tệp từ môi trường khác bạn có (ví dụ sandbox đám mây) rồi chuyển từng tệp vào thư mục người dùng bằng công cụ truyền tệp của nền tảng.

## Bước 3: cá nhân hoá

Từ gốc xưởng mới:

```
python3 tools/dung_xuong.py --ten-xuong "<tên xưởng>" --tien-to <tiền tố> --ban-mau <mã commit>
```

Lệnh này bỏ các khối chỉ dành cho bản thiết kế, tạo `cau-hinh.json` (có `tienToSkill`), tạo `Du an/` và `Kho giong/` cạnh xưởng, viết `README.md` của xưởng (ghi công bản thiết kế, giấy phép MIT), ghi bản thiết kế đã dùng vào `tools/.dung-xuong.json`. Chạy `python3 tools/kiem_tra_xuong.py`: phải ra 0 lỗi.

Từ đây `CLAUDE.md` trong xưởng mới là sách vận hành. Đọc lại nó trước khi làm tiếp.

## Bước 4: thiết lập

Làm theo skill `skills/long-tieng-thiet-lap/SKILL.md` của xưởng mới, từ Bước 1: hỏi mục đích và máy, chọn máy đọc, nhờ người dùng chạy trình cài đặt trên máy thật (Mac: `Cai dat tren Mac.command`; Windows: `Cai dat tren Windows.bat`), giọng riêng, skill vào tài khoản, bản lồng tiếng đầu tiên.

Bạn không phải Claude, hoặc nền tảng không có khái niệm skill: đặt skill theo cách nền tảng đó hỗ trợ; không có thì bỏ qua bước đóng gói, xưởng vẫn chạy vì `CLAUDE.md` trỏ thẳng tới `skills/`.

## Bước 5: nghiệm thu việc dựng xưởng

- `python3 tools/kiem_tra_xuong.py` ra 0 lỗi; `python3 tools/dung_xuong.py --kiem` có dòng "Bản thiết kế" với đúng mã commit.
- Trình cài đặt trên máy thật báo "Cài xong"; `Du an/_tam/may-tinh.json` có cấu hình thật; các lượt trong `Du an/_kiem-may/` có `kiem.json`.
- `python3 tools/dong_goi_skill.py` báo mọi skill đã lưu (hoặc người dùng chọn để sau).
- Trong xưởng không có `.git` trỏ về repo bản thiết kế.

## Về sau: tiếp nhận cái mới từ bản thiết kế

Người dùng nói "xem bản thiết kế có gì mới":

1. Đọc `THAY-DOI.md` trên GitHub, lấy các mục sau ngày `banMau.ngay` trong `tools/.dung-xuong.json` của xưởng.
2. Với mỗi thay đổi, so tệp trong xưởng với bản thiết kế CŨ (ở mã `banMau.commit`). Giống nhau: người dùng chưa sửa, lấy bản mới được. Khác: đã tinh chỉnh, phải hợp nhất có chọn lọc.
3. Trình người dùng danh sách: lấy gì, vì sao đáng lấy, ảnh hưởng gì. Họ duyệt rồi mới ghi.
4. Không bao giờ ghi đè: `cau-hinh.json`, `docs/BAI-HOC.md` (hợp nhất, không thay), `du-lieu/phat-am-de-xuat.json` đã thêm mục, skill người dùng đã tinh chỉnh; không đụng `Du an/` và `Kho giong/`.
5. Ghi xong: chạy lại `python3 tools/dung_xuong.py --ten-xuong "<tên xưởng>" --tien-to <tiền tố> --ban-mau <mã mới>`, `python3 tools/kiem_tra_xuong.py`, `python3 tools/dong_goi_skill.py --lam` để người dùng lưu lại skill đã đổi; đổi công cụ hay thư viện thì nhờ người dùng chạy lại trình cài đặt trên máy thật.
