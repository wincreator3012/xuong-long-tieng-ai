# Skill trong tài khoản AI: giải thích cho người dùng và cách lưu

Đọc ở Bước 6 của skill long-tieng-thiet-lap, và mỗi khi người dùng hỏi "skill là gì", "lưu skill thế nào", "sao AI không nhận ra việc", "skill nào cần lưu lại". Người dùng thường chưa từng nghe chữ "skill": giải thích bằng lời thường, ví dụ gần đời, mỗi lượt một ý, kết bằng một câu hỏi.

## Bốn ý cần người dùng hiểu

**1. Skill là gì.** Một skill là bản quy trình chuẩn viết cho AI, giống cuốn sổ tay nghề của một người thợ lành nghề: khi nào dùng, làm từng bước ra sao, kiểm gì trước khi giao. Xưởng có hai skill: lồng tiếng (soạn lời đọc, sinh tiếng, kiểm, ghép, thi nghe, giọng riêng) và thiết lập xưởng. Nhờ skill, lần nào AI cũng làm theo cùng một cách đã kiểm chứng.

**2. Skill sống ở hai nơi.** Bản gốc nằm trong thư mục xưởng (`skills/`): AI đọc và sửa bản này khi bạn góp ý, nó lớn lên theo bạn. Bản trong tài khoản AI là bản chép: nhờ nó, ở BẤT KỲ phiên làm việc nào, AI tự nhận ra việc bạn nhờ (bạn chỉ cần nói "lồng tiếng đoạn này bằng giọng tôi") và mở đúng quy trình.

**3. Tên mang dấu của bạn.** Trong tài khoản, mỗi skill mang tiền tố riêng của bạn (ví dụ `tma-long-tieng`): nhìn danh sách là biết skill nào của xưởng mình, và không trùng với skill người khác chia sẻ cho bạn.

**4. Skill cần xưởng.** Skill chỉ chứa CÁCH LÀM. Công cụ, mô hình, giọng riêng, dự án nằm trong thư mục xưởng và máy của bạn, nên mỗi phiên lồng tiếng hãy thêm thư mục mẹ (chứa xưởng, `Du an`, `Kho giong`) vào phiên làm việc. Skill không chứa giọng hay thông tin riêng của bạn.

## Cách lưu (app Claude; tên mục có thể đổi theo phiên bản app)

1. Bật một lần: Settings > Capabilities, bật "Code execution and file creation". Gói Team hoặc Enterprise: chủ tổ chức bật ở Organization settings.
2. Với mỗi tệp `.skill` AI gửi trong cuộc trò chuyện: bấm nút lưu skill trên thẻ tệp, nếu app có nút này.
3. Không có nút lưu: tải tệp về, vào Customize > Skills, bấm "+", chọn "Create skill", rồi "Upload a skill", chọn tệp. Hộp chọn tệp không nhận đuôi `.skill` thì đổi đuôi thành `.zip` (nội dung giống hệt).
4. Skill cùng tên đã có: chọn thay bản cũ. App tạo thành hai bản thì xoá bản cũ, để AI không bị hai quy trình lệch nhau.
5. Bật công tắc của skill trong danh sách. Lưu xong, báo AI "đã lưu skill" để nó ghi sổ.

Hướng dẫn chính thức: trang trợ giúp "Use skills in Claude" ở support.claude.com. Trợ lý AI khác: lưu theo cách nền tảng đó hỗ trợ (thư mục skill, tệp hướng dẫn dự án); không có thì bỏ qua, xưởng vẫn chạy vì `CLAUDE.md` và `AGENTS.md` trỏ thẳng tới `skills/`.

## Việc của AI (không đọc cho người dùng)

1. `python3 tools/dong_goi_skill.py --lam --tat-ca` (lần đầu) hoặc `--lam` (chỉ skill đã đổi so với lần lưu cuối). Tệp ra ở `Du an/_tam/goi-skill/<ngày giờ>/`, kèm `DOC-TRUOC.md`.
2. Gửi tệp cho người dùng theo cách nền tảng cho phép (Cowork: gửi tệp vào cuộc trò chuyện, mỗi tệp một thẻ).
3. Họ lưu xong: `python3 tools/dong_goi_skill.py --da-luu`.
4. Mỗi lần sửa một SKILL.md hay tệp trong `references/`: `python3 tools/dong_goi_skill.py --lam` rồi nhờ người dùng lưu lại. Không để bản trong tài khoản cũ hơn bản gốc quá một phiên.
