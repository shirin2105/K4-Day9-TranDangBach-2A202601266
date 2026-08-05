# Architecture Overview - Day 9: Multi-Agent E-commerce Dispute Resolution

Hệ thống được thiết kế theo mô hình **Multi-Agent (Agent-to-Agent - A2A)** phối hợp giữa các Agent chuyên biệt, lớp tra cứu dữ liệu chính xác (Pandas Data Retrieval Tool) và Engine quy tắc nghiệp vụ (`EC_POLICY_V2`).

## 1. Multi-Agent Workflow Diagram

```text
                    ┌─────────────────────┐
                    │ EC_xxx.json         │
                    │ Customer Complaint  │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ 1. Supervisor Agent │
                    │ Điều phối toàn case │
                    └──────────┬──────────┘
                               ▼
                 ┌──────────────────────────┐
                 │ 2. Claim Triage Agent    │
                 │ Hiểu nội dung khiếu nại  │
                 │ Xác định claim_type      │
                 └────────────┬─────────────┘
                              ▼
                    ┌─────────────────────┐
                    │ Data Retrieval Tool │
                    │ Tra cứu Olist data  │
                    └──────────┬──────────┘
                               ▼
                ┌──────── Conditional Router ────────┐
                │                                    │
                ▼                                    ▼
       ┌──────────────────┐                ┌──────────────────┐
       │ 3A. Delivery     │                │ 3B. Financial    │
       │ Investigation    │                │ Investigation    │
       │ Agent            │                │ Agent            │
       └────────┬─────────┘                └────────┬─────────┘
                │                                    │
                └───────────────┬────────────────────┘
                                ▼
                     ┌─────────────────────┐
                     │ 3C. Context Agent   │
                     │ Customer, seller,   │
                     │ product, history    │
                     └──────────┬──────────┘
                                ▼
                     ┌─────────────────────┐
                     │ 4. Policy           │
                     │ Adjudicator Agent   │
                     │ Áp dụng EC_POLICY   │
                     └──────────┬──────────┘
                                ▼
                     ┌─────────────────────┐
                     │ 5. Critic Agent     │
                     │ Kiểm tra quyết định │
                     │ và bằng chứng       │
                     └──────────┬──────────┘
                         Sai ───┤ ├── Đúng
                               │ ▼
                               │ ┌─────────────────────┐
                               └►│ 6. Resolution Agent │
                                 │ Viết kết luận cuối  │
                                 └──────────┬──────────┘
                                            ▼
                                 ┌─────────────────────┐
                                 │ Output Validator    │
                                 │ output/EC_xxx.json  │
                                 └─────────────────────┘
```

## 2. Vai trò chi tiết của từng Agent & Module

### 1. Supervisor Agent & Output Validator (`src/supervisor.py`)
- **Nhiệm vụ**: Đóng vai trò trưởng nhóm điều phối toàn bộ vòng đời phân tích case từ Bước 1 đến Bước 6.
- **Output Validator**: Đảm bảo cấu trúc đầu ra tuân thủ 100% Output Schema JSON yêu cầu trước khi lưu file.

### 2. Claim Triage Agent (`src/agents/triage_agent.py`)
- **Nhiệm vụ**: Phân tích tin nhắn khiếu nại của khách hàng (`customer_request.message`) và gắn tag loại khiếu nại (`delivery_delay`, `cancellation`, `payment_dispute`, ...).

### 3. Data Retrieval Tool (`src/data_loader.py`)
- **Nhiệm vụ**: Tải và lưu cache 9 tệp CSV Olist. Cung cấp API tra cứu dữ liệu cực nhanh theo `order_id`, `customer_id`, `seller_id`, `product_id`.

### 4. Specialized Investigation Agents
- **3A. Delivery Agent (`src/agents/delivery_agent.py`)**: Tính chính xác `delivery_variance_hours` (giờ giao muộn), `handoff_variance_hours` (giờ seller bàn giao muộn) và xác định `late_handoff_seller_ids`.
- **3B. Financial Agent (`src/agents/financial_agent.py`)**: Tính tổng tiền item, phí freight, tiền thanh toán thực tế, kiểm tra chênh lệch `difference_brl` và trạng thái đối soát `reconciled` ($\le 0.10$ BRL).
- **3C. Context Agent (`src/agents/context_agent.py`)**: Lấy thông tin lịch sử khách hàng (`customer_unique_id`, `related_order_ids`), danh mục sản phẩm và danh sách seller liên quan.

### 5. Policy Adjudicator Agent (`src/agents/policy_agent.py`)
- **Nhiệm vụ**: Áp dụng quy tắc ưu tiên `EC_POLICY_V2` để xác định:
  - **Primary Issue**: (`canceled_order_paid`, `unavailable_order_paid`, `late_delivery_seller`, `late_delivery_logistics`, `valid_split_payment`, `unsupported_late_claim`).
  - **Secondary Issues**: (`multi_item_order`, `multi_seller_order`, `split_payment`, `repeat_customer`, `multiple_categories`).
  - **Responsible Parties** & **Financial Resolution** (loại refund và số tiền).
  - **Evidence IDs**: Tạo mã bằng chứng chuẩn (`order:<id>`, `item:<id>:<seq>`, `payment:<id>:<seq>`, `seller:<id>`, `policy:<code >`).

### 6. Critic Agent (`src/agents/critic_agent.py`)
- **Nhiệm vụ**: Đánh giá độc lập quyết định của Policy Agent. Nếu phát hiện thiếu bằng chứng hoặc sai định dạng, gửi tín hiệu phản hồi để điều chỉnh lại.

### 7. Resolution Agent (`src/agents/resolution_agent.py`)
- **Nhiệm vụ**: Tổng hợp kết quả phân tích, kết nối LLM (Qwen 3.5) / Logic để tạo câu tóm tắt `investigation_summary` và tính điểm tin cậy `confidence`.
