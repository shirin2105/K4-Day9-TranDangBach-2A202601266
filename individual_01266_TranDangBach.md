# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin       | Nội dung                          |
| --------------- | --------------------------------- |
| Họ và tên       | Trần Đăng Bách                    |
| MSSV            | 2A202601266                       |
| Khóa/Lớp        | K4                                |
| Vai trò chính   | Lead System Architect & Developer |
| Ngày hoàn thành | 2026-08-05                        |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| ------------------ | ------------------ | -------------- | --------------- | ---------- |
| Multi-Agent Pipeline | `src/supervisor.py`, `main.py` | 50 file `input/EC_*.json` | 50 file `output/EC_*.json` | Hoàn thành |
| Data Retrieval Tool | `src/data_loader.py` | 9 file CSV Olist trong `data/` | Data API tra cứu | Hoàn thành |
| Specialized Sub-Agents | `src/agents/*.py` | Input JSON & Olist Data | Phân tích Delivery, Finance, Context, Policy, Critic, Resolution | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --------- | ----------------------------- | ------- |
| Tối ưu hóa Schema Output | Output Validator | 100% (50/50 cases) khớp định dạng yêu cầu |
| Tích hợp Hugging Face | Config & Resolution Agent | Thiết lập thành công Qwen 3.5 Token & Model ID |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------- | --------------------------- | ----------------- | ------------- |
| Xây dựng hệ thống Multi-Agent | `src/supervisor.py`, `src/agents/` | Khung 6 Agent hoàn chỉnh | `python main.py` |
| Xử lý 50 case khiếu nại | `output/EC_001.json` - `EC_050.json` | 50 file JSON kết quả | Validation Script |
| Viết tài liệu Kiến trúc | `architecture.md` | Bản vẽ kiến trúc & vai trò Agent | Kiểm tra file |

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Bài toán yêu cầu giải quyết 50 khiếu nại thương mại điện tử từ dữ liệu Olist bằng cách đối chiếu thông tin thời gian giao hàng, giá tiền, người bán, người mua và áp dụng chính xác luật `EC_POLICY_V2`.

### Cách triển khai
Áp dụng mô hình Multi-Agent A2A theo sơ đồ:
1. **Supervisor Agent**: Điều phối toàn case.
2. **Claim Triage Agent**: Nhận diện loại khiếu nại.
3. **Data Retrieval Tool**: Tra cứu dữ liệu từ 9 CSV Olist.
4. **Specialized Agents (3A, 3B, 3C)**: Độc lập phân tích Delivery, Finance và Customer/Product Context.
5. **Policy Adjudicator Agent (4)**: Khớp luật `EC_POLICY_V2` (Primary/Secondary Issues, Refunds, Evidence IDs).
6. **Critic Agent (5)**: Thẩm định kết quả & tự động sửa nếu thiếu Evidence.
7. **Resolution Agent (6)**: Tổng hợp câu kết luận & tính chỉ số confidence.

### Input, output và contract

| Thành phần | Mô tả |
| ---------- | ------ |
| Input | `input/EC_xxx.json` chứa `claimed_order_id`, `message` |
| Output | `output/EC_xxx.json` chứa đầy đủ 12 trường thông tin chuẩn Schema |
| Module phụ thuộc | `pandas`, `python-dotenv`, `huggingface-cli` |

### Cách xác minh

```bash
python main.py
```

- **Kết quả mong đợi:** Xử lý 50/50 cases thành công không có lỗi.
- **Kết quả thực tế:** Processed 50/50 cases (`EC_001.json` -> `output/EC_001.json`).

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Cần quyết định cách phân định trách nhiệm khi hàng giao muộn.
- **Phương án đã chọn:** Tách riêng **Delivery Agent (3A)** để tính chính xác cả `delivery_variance_hours` (giao muộn so với ước tính) lẫn `handoff_variance_hours` (bàn giao muộn của seller so với hạn `shipping_limit_date`).
- **Lý do:** Giúp phân biệt chính xác lỗi do **Seller** (`late_delivery_seller`) hay lỗi do **Đơn vị vận chuyển** (`late_delivery_logistics`).

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680'` khi chạy trên Windows PowerShell.
- **Nguyên nhân gốc:** Bảng mã mặc định của Windows Console (CP1252) không hỗ trợ ký tự Emoji Unicode.
- **Cách xử lý:** Thay thế các emoji trong câu lệnh `print` của `main.py` bằng định dạng text chuẩn `[+]`, `[ok]`.
- **Cách xác minh sau khi sửa:** Lệnh `python main.py` chạy hoàn tất 100% mượt mà.

## 7. Hiểu biết về luồng end-to-end

1. Dữ liệu khiếu nại đầu vào chứa `claimed_order_id` được Data Retrieval Tool join chính xác qua 9 bảng dữ liệu Olist.
2. Các Sub-Agent phân tích riêng biệt thời gian, tài chính và bối cảnh trước khi chuyển cho Policy Adjudicator Agent.
3. Policy Agent đối chiếu quy tắc `EC_POLICY_V2` để đưa ra hình thức hoàn tiền và sinh danh sách bằng chứng `evidence_ids`.
4. Critic Agent soát lỗi độc lập trước khi Resolution Agent và Output Validator đóng gói tệp JSON đầu ra.

## 8. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Trần Đăng Bách  
**Ngày xác nhận:** 2026-08-05
