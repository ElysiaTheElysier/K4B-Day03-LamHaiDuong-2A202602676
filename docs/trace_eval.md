# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Lâm Hải Dương  
> **Mã Sinh Viên / Mã Học viên:** 2A202602676  
> **Chủ đề Lựa chọn:** Đề tài Mở (Open Choice) — Banking Investigator: Phân tích & Điều tra Giao dịch Ngân hàng Bất thường (Fraud Detection)  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 5 / 5 | Để kết luận một giao dịch có bất thường hay không, Agent phải suy luận qua nhiều bước nối tiếp: Kiểm tra hồ sơ tài chính -> Truy vấn lịch sử giao dịch -> So sánh mức chi tiêu trung bình -> Đối chiếu mã ngành hàng (MCC) và vị trí địa lý. |
| **2. Tool Interaction** | 5 / 5 | Bắt buộc phải kết nối với MCP Server để truy vấn dữ liệu thực tế từ cơ sở dữ liệu giao dịch (12M dòng), thông tin thẻ và danh mục MCC theo thời gian thực; LLM thuần không thể tự suy diễn dữ liệu này. |
| **3. Dynamic Decision** | 5 / 5 | Hành động của bước tiếp theo phụ thuộc hoàn toàn vào kết quả quan sát (Observation) của bước trước: nếu chi tiêu bình thường thì dừng và kết luận an toàn; nếu phát hiện giao dịch lạ/lỗi lặp lại thì kích hoạt tool phân tích chi tiết và đề xuất khóa thẻ. |
| **4. Long Horizon Goal** | 4 / 5 | Hệ thống duy trì mục tiêu điều tra xuyên suốt chuỗi hội thoại: từ lúc nhận nghi vấn từ người dùng đến khi xác minh chứng cứ và xuất được biên bản xử lý rủi ro cuối cùng. |
| **TỔNG ĐIỂM AGENTIC FIT** | **19 / 20** | *Đạt 19/20 điểm (> 12/20): Bài toán hoàn toàn phù hợp và phát huy tối đa sức mạnh của hệ thống ReAct Agent.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "Hãy tra cứu hồ sơ tài chính và thông tin thẻ của khách hàng có mã ID 1081.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "get_customer_profile",
    "arguments": {
      "client_id": "1081"
    },
    "observation": {
      "status": "SUCCESS",
      "client_id": "1081",
      "data": {
        "age": "31",
        "gender": "Female",
        "yearly_income": "$50666",
        "total_debt": "$102318",
        "credit_score": "617",
        "address": "9633 Mill Lane",
        "cards_count": 3,
        "cards": [
          {
            "card_id": "404",
            "brand": "Amex",
            "type": "Credit",
            "credit_limit": "$21200",
            "has_chip": "YES",
            "card_on_dark_web": "No"
          },
          {
            "card_id": "3427",
            "brand": "Mastercard",
            "type": "Credit",
            "credit_limit": "$10400",
            "has_chip": "YES",
            "card_on_dark_web": "No"
          },
          {
            "card_id": "3892",
            "brand": "Mastercard",
            "type": "Debit",
            "credit_limit": "$27377",
            "has_chip": "YES",
            "card_on_dark_web": "No"
          }
        ]
      }
    },
    "latency_ms": 1548.74
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (OpenAI `gpt-4o-mini`).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 4 lượt (TC02, TC03, TC04, TC05).
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
