# AGENTS.md - điểm vào cho mọi trợ lý AI (Codex, ChatGPT, Antigravity, Gemini, Claude...)

<!-- BAN-MAU -->
## Bạn đang đọc một BẢN THIẾT KẾ, không phải phần mềm để clone

Repo `wincreator3012/xuong-long-tieng-ai` là bản thiết kế của một xưởng lồng tiếng cùng AI. Người dùng nhờ bạn đọc nó để **dựng một xưởng riêng trên máy của họ**, không phải để lấy repo về dùng nguyên.

- Không `git clone`, không fork, không tải ZIP vào thư mục của người dùng, không tạo remote trỏ về đây.
- Không push, không pull, không mở issue hay pull request thay người dùng.
- Làm theo `DUNG-XUONG.md`: chép phần năng lực theo `BAN-DO-TEP.json`, cá nhân hoá, chọn máy đọc theo cấu hình máy, nhờ người dùng chạy trình cài đặt trên máy thật, giọng riêng, đóng gói skill, bản lồng tiếng đầu tiên.
<!-- /BAN-MAU -->

## Xưởng này vận hành thế nào

Sách vận hành của xưởng là `CLAUDE.md`: áp dụng cho mọi trợ lý AI, không riêng Claude. Đọc nó đầu mỗi phiên, rồi `skills/long-tieng/SKILL.md` khi lồng tiếng, `skills/long-tieng-thiet-lap/SKILL.md` khi thiết lập hay đổi máy đọc.

- Lệnh trong tài liệu chạy từ gốc xưởng. Dự án và giọng riêng nằm NGOÀI xưởng: `../Du an/`, `../Kho giong/`.
- Mô hình chạy trên máy thật của người dùng (Mac hoặc Windows) khi họ bấm đúp tệp "Long tieng"; bạn xếp việc vào hàng đợi (`tools/hang_doi.py`), không chạy mô hình trong máy ảo của mình.
- Giữ nguyên các cổng kiểm và quy tắc cứng trong `CLAUDE.md`, nhất là: chỉ nhân bản giọng của chính chủ hoặc người đã đồng thuận bằng văn bản; khóa API chỉ nằm trong kho khóa của máy.
