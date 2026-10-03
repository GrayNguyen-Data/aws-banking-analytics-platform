# Danh sách công việc — Kho dữ liệu ngân hàng trên Cloud

> Phạm vi: dự án cuối kỳ. Tập trung xây dựng quy trình dữ liệu đầu-cuối có thể chạy và giải thích được, thay vì viết tài liệu quá chi tiết hoặc xây dựng hạ tầng đạt tiêu chuẩn production.

## Giai đoạn 1 — Thiết lập dự án
- [ ] Tạo repository GitHub `cloud-banking-dwh`
- [ ] Tạo cấu trúc thư mục đã thống nhất
- [ ] Thêm README, `.gitignore`, `.env.example` và LICENSE
- [ ] Thêm sơ đồ kiến trúc vào `docs/diagrams/`
- [ ] Tạo Git commit đầu tiên

## Giai đoạn 2 — Tìm hiểu bộ dữ liệu
- [ ] Tải bộ dữ liệu ngân hàng tổng hợp đã chọn từ Kaggle
- [ ] Kiểm tra các tệp, cột, kiểu dữ liệu và số lượng bản ghi
- [ ] Xác định khóa chính, các mối quan hệ, trường ngày tháng và chỉ số đo lường
- [ ] Kiểm tra giá trị thiếu, bản ghi trùng lặp và giá trị không hợp lệ
- [ ] Ghi lại từ điển dữ liệu thực tế
- [ ] Xác nhận các chỉ số nghiệp vụ mà bộ dữ liệu có thể hỗ trợ

## Giai đoạn 3 — Thiết lập nền tảng PostgreSQL
- [ ] Cài đặt PostgreSQL cục bộ hoặc chọn cơ sở dữ liệu mục tiêu
- [ ] Cấu hình biến môi trường và không commit thông tin bí mật
- [ ] Tạo các schema `staging`, `warehouse` và `mart`
- [ ] Tạo các bảng staging dựa trên bộ dữ liệu thực tế
- [ ] Khởi tạo cơ sở dữ liệu và xác minh kết nối

## Giai đoạn 4 — Data Lake trên S3
- [ ] Tạo S3 bucket với tên duy nhất
- [ ] Quy định prefix `raw/` và quy ước đặt tên object
- [ ] Cấu hình quyền IAM theo nguyên tắc đặc quyền tối thiểu
- [ ] Tải các tệp CSV nguồn lên S3
- [ ] Xác minh các object đã tải lên và quyền truy cập

## Giai đoạn 5 — ETL và Staging
- [ ] Triển khai bước thu thập dữ liệu
- [ ] Triển khai quy trình làm sạch và chuẩn hóa kiểu dữ liệu
- [ ] Xác định cách xử lý giá trị null, bản ghi trùng lặp và bản ghi không hợp lệ
- [ ] Nạp dữ liệu vào các bảng staging trên PostgreSQL
- [ ] Đối chiếu số lượng bản ghi ở nguồn với số lượng đã nạp
- [ ] Bổ sung log hữu ích và cơ chế xử lý lỗi rõ ràng
- [ ] Kiểm thử logic làm sạch và kiểm tra chất lượng dữ liệu

## Giai đoạn 6 — Kho dữ liệu
- [ ] Hoàn thiện Star Schema dựa trên bộ dữ liệu đã kiểm tra
- [ ] Tạo các bảng dimension
- [ ] Tạo bảng fact giao dịch
- [ ] Nạp dữ liệu vào các bảng dimension trước bảng fact
- [ ] Kiểm tra khóa, mối quan hệ và số lượng bản ghi
- [ ] Thêm index khi phù hợp với các mẫu truy vấn

## Giai đoạn 7 — Data Mart
- [ ] Xây dựng mart số dư khách hàng nếu các trường dữ liệu hiện có hỗ trợ
- [ ] Xây dựng mart giao dịch/doanh thu theo ngày và định nghĩa chỉ số rõ ràng
- [ ] Xây dựng mart hiệu quả chi nhánh nếu có dữ liệu về chi nhánh
- [ ] Đối chiếu tổng số liệu trong mart với kết quả truy vấn kho dữ liệu

## Giai đoạn 8 — Tự động hóa và giám sát trên AWS
- [ ] Đóng gói và triển khai các Lambda function cần thiết
- [ ] Cấu hình biến môi trường và IAM role cho Lambda
- [ ] Cấu hình lịch chạy EventBridge
- [ ] Kiểm tra log CloudWatch và thiết lập giám sát lỗi cơ bản
- [ ] Cấu hình cảnh báo email qua SNS và xác nhận đăng ký nhận tin
- [ ] Kiểm thử một lần chạy thành công và một tình huống lỗi có kiểm soát
- [ ] Kiểm tra chi phí AWS và xóa các tài nguyên không sử dụng

## Giai đoạn 9 — Dashboard và trình diễn cuối kỳ
- [ ] Kết nối công cụ BI với dữ liệu mart
- [ ] Xây dựng biểu đồ dashboard để trả lời các câu hỏi nghiệp vụ mà dữ liệu hỗ trợ
- [ ] Đối chiếu số liệu trên dashboard với kết quả truy vấn SQL
- [ ] Kiểm thử quy trình dữ liệu đầu-cuối
- [ ] Hoàn thiện hướng dẫn phát triển và triển khai ngắn gọn
- [ ] Chuẩn bị phần trình bày kiến trúc và demo cuối kỳ
- [ ] Chụp ảnh màn hình hoặc lưu kết quả cuối cùng để đưa vào báo cáo

## Tiêu chí hoàn thành
- [ ] Dữ liệu nguồn được lưu trữ trên S3
- [ ] ETL nạp các bản ghi đã được kiểm tra vào PostgreSQL
- [ ] Kho dữ liệu và các mart cho kết quả truy vấn có thể tái lập
- [ ] Các chỉ số trên dashboard khớp với kết quả SQL
- [ ] Có thể kiểm tra quá trình chạy và lỗi của quy trình dữ liệu
- [ ] README và hướng dẫn cài đặt/triển khai dễ hiểu
- [ ] Tài nguyên AWS được rà soát và dọn dẹp sau buổi demo
