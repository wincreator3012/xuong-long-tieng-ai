# Viết lời đọc

Lời đọc là văn để nghe. Người nghe không đọc lại được câu vừa qua, không thấy dấu phẩy, không thấy ngoặc. Mọi điều mắt nhận từ chữ, tai phải nhận từ nhịp và giọng.

## Cú pháp của `loi-doc.md`

| Viết | Nghĩa |
|---|---|
| dòng trống | hết một đoạn đọc (đơn vị sinh tiếng, chọn lượt, làm lại) |
| `# Tiêu đề mục` | không đọc; chèn quãng lặng sau mục (`nghiSauMuc`, mặc định 1 giây) |
| `{ngừng 1.5}` đứng riêng một dòng | thêm 1,5 giây lặng trước đoạn kế |
| `> trìu mến, chậm | tender, slow` | chỉ dẫn diễn xuất cho đoạn ngay dưới; vế sau dấu `|` là bản tiếng Anh đưa cho máy đọc |
| `{> tò mò, lên giọng | curious, rising}` giữa câu | chỉ dẫn từ chỗ đó trở đi (Drama 3, ElevenLabs hiểu; Higgs v3 dịch từ khóa; Gemini, VieNeu bỏ qua): cách chính để nhịp có nhanh có chậm |
| `{ngừng}`, `{ngừng dài}`, `{ngừng 1.2}` trong câu | quãng ngắt bên trong đoạn |
| `{cười}`, `{cười nhẹ}`, `{thở dài}`, `{hít thở}`, `{hắng giọng}` | âm thanh không lời; máy nào không có thì bỏ qua |
| `{{AI|ây ai}}` | phụ đề ghi "AI", máy đọc "ây ai" |
| `<!-- ghi chú -->` | không đọc |

Đầu tệp (giữa hai dòng `---`): `tieuDe`, `ngonNgu` (vi, en), `may`, `giong`, `soLuot`, `phongCach` (chỉ dẫn chung, song ngữ như trên), `nghiGiuaDoan` (giây lặng giữa hai đoạn, mặc định 0,6).

Không dùng ngoặc vuông trong lời đọc: máy đọc như ElevenLabs, Drama 3 hiểu `[...]` là chỉ dẫn. Chú thích tiếng Anh kiểu "hệ thần kinh giao cảm [sympathetic nervous system]" bị bỏ tự động và có cảnh báo; muốn đọc thuật ngữ tiếng Anh thì viết ra thành lời.

## Chia đoạn

- Mỗi đoạn 1 đến 3 câu, khoảng 10 đến 25 giây khi đọc. Đoạn ngắn thì dễ làm lại và máy ít "trôi" giọng; đoạn quá ngắn thì nhịp rời rạc.
- Ngắt đoạn ở chỗ người nói thật sẽ lấy hơi: đổi ý, chuyển từ ví dụ sang nhận định, trước một câu hỏi.
- Câu dài trên 30 tiếng thì tách, hoặc thêm dấu phẩy ở chỗ lấy hơi.

## Viết cho tai

- Số, ngày, đơn vị: xưởng tự đổi sang chữ cho máy cần (`chuanHoaSo` trong `may-doc.json`). Viết số như bình thường; số dễ đọc sai (năm học "2025-2026", phân số "1/2", số hiệu) thì viết hẳn thành lời.
- Tên riêng, viết tắt, thương hiệu: tra `du-lieu/phat-am-de-xuat.json` và kho; chưa có thì đặt `{{chữ|cách đọc}}` ngay trong lời, rồi đề xuất thêm vào từ điển.
- Từ tiếng Anh trong câu tiếng Việt: giữ khi người dùng vẫn nói như vậy trên lớp (coaching, workshop); chọn cách đọc kiểu Việt hay kiểu Anh theo thói quen của người dùng, hỏi khi không chắc.
- Tránh ký hiệu: "→", "&", "/", "%" trong câu văn thường (trừ con số phần trăm).

## Thẻ biểu cảm và chỉ dẫn diễn xuất

- Chỉ dẫn diễn xuất (`>`) quan trọng hơn thẻ. Viết vế tiếng Anh cụ thể như dặn diễn viên: "lively yet grounded, like an engaging teacher" tốt hơn "warm".
- Tiếng Việt: nhịp phải biến thiên, không dặn "chậm" cho cả bài. Câu giảng giải dặn nhanh hơn một chút, chữ then chốt dặn chậm lại và nhấn, câu hướng dẫn thở dặn chậm hẳn, rồi dặn trở lại nhịp thường. Drama 3 đọc theo chỉ dẫn rất sát, dặn chậm cả bài thì sẽ đều đều (thi nghe vòng 1, 19/11/2026).
- Thẻ âm thanh dùng thưa: 1 đến 2 lần mỗi phút là nhiều. Tiếng cười, tiếng thở dài phải có lý do trong lời.
- Đồng hướng: chỉ dẫn, thẻ và chính câu văn phải cùng một cảm xúc. Lời buồn mà dặn "cheerful" thì máy đọc lưỡng lự.
- Mỗi máy hiểu chỉ dẫn khác nhau: Gemini nhận vào `style` của lượt; ElevenLabs, Drama 3 nhận thẻ tự do `[...]` đầu đoạn; Higgs v3 chỉ nhận danh mục cố định nên xưởng dịch từ khóa (warm, slow, calm, whisper...) sang thẻ của nó; VieNeu bỏ qua chỉ dẫn (giọng theo mẫu).

## Khuôn đã chốt cho tiếng Việt

`mau-nhip-manh.md` (cạnh tệp này) là kịch bản đạt 4,5/5 ở thi nghe vòng 2 với Drama 3 giọng riêng. Soạn kịch bản tiếng Việt mới thì theo cách đặt chỉ dẫn của nó: phong cách chung sôi nổi mà điềm tĩnh; nhanh ở câu giảng giải; chậm lại và nhấn ở ý then chốt; chậm hẳn ở câu hướng dẫn thở rồi trở lại nhịp thường; chậm lại, mở ở câu hỏi kết.

## Khuôn đã chốt cho tiếng Anh

Tiếng Anh ngược với tiếng Việt. `mau-tieng-anh-am.md` (cạnh tệp này) đạt 5/5 ở thi nghe tiếng Anh vòng 2 (19/11/2026, Drama 3, mẫu vi-03): chỉ một dòng `phongCach: ấm, chậm, gần gũi | warm, unhurried, intimate`, không có chỉ dẫn `>` hay `{> ...}` nào, chỉ giữ thẻ `{ngừng}`, `{ngừng dài}`, `{cười nhẹ}`. Cùng lời ấy, bỏ hết chỉ dẫn được 4,75; viết theo khuôn nhịp mạnh chỉ được 4,0 (tự nhiên 3). Có vẻ Drama 3 tự đọc tiếng Anh đã có nhịp biến thiên, chỉ dẫn giữa câu làm nó gượng.

## Bài đọc dài (từ 20 đoạn trở lên)

- Đầu tệp đặt `nghiGiuaDoan: 1.0`, `nghiSauMuc: 1.2`; quãng ngắn hơn làm bài nghe liền, gấp.
- Trong đoạn: `{ngừng 0.8}` sau dấu chấm giữa đoạn; quanh ngoặc chú thích và gạch ngang `{ngừng 0.4}` đến `{ngừng 0.5}`; từ ghép nối bằng gạch viết tách ra, như `Tâm {ngừng 0.25} Thể`.
- Từ viết tắt, tên tổ chức, từ dễ đọc sai: `{{UNESCO|du nét scô}}`, `{{AI|ây ai}}`. Chữ ngắn trùng từ tiếng Anh (như "do" nghĩa là "bởi") phải đặt cách đọc: `{{do|gio}}`. Âm cuối nhẹ viết liền chữ ("scô"), không viết "xờ".
- Số, ngày, phần trăm viết thành chữ. Chú thích tiếng Anh trong ngoặc vuông máy bỏ, nên viết thêm nếu người đọc chữ cần.
- Chỉ dẫn cho đoạn số liệu: giảng giải, rõ từng ý, nhịp vừa; không "nhịp đều". Hai cảm xúc trái nhau trong một chỉ dẫn làm hỏng đoạn.

## Ví dụ

```
---
tieuDe: Mở đầu bài thực hành hít thở
ngonNgu: vi
may: drama3
giong: @an
soLuot: 3
phongCach: sôi nổi mà điềm tĩnh, gần gũi | lively yet grounded, dynamic pacing, warm
---

# Mở đầu

Chào bạn. {ngừng} Trong 3 phút tới, mình cùng làm một việc rất nhỏ: thở, và để ý mình đang thở.

> nhẹ, nhiều quãng lặng | soft, slow, leaving space between phrases
Mời bạn ngồi thoải mái. {ngừng dài} Hít vào... {ngừng} và thở ra, buông lỏng đôi vai.

{ngừng 2}

Nếu tâm trí trôi đi, cũng không sao. {cười nhẹ} Nhẹ nhàng đưa sự chú ý trở về.
```
