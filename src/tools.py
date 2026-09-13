"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer kết nối dữ liệu thực tế.
"""

import json
import os
import csv
from typing import Dict, Any, List

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Tra cứu hồ sơ tài chính & thẻ khách hàng
    {
        "name": "get_customer_profile",
        "description": "Tra cứu hồ sơ tài chính, điểm tín dụng, thu nhập, nợ và danh sách thẻ của khách hàng qua mã ID (client_id).",
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "Mã định danh khách hàng (ví dụ: '1081', '845')"
                }
            },
            "required": ["client_id"]
        }
    },
    
    # Tool 2: Tra cứu lịch sử giao dịch gần đây và giải mã MCC
    {
        "name": "query_recent_transactions",
        "description": "Tra cứu các giao dịch gần đây của khách hàng, giải mã ngành hàng kinh doanh (MCC) và kiểm tra lỗi giao dịch.",
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "Mã định danh khách hàng cần kiểm tra giao dịch (ví dụ: '1081', '845')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Số lượng giao dịch cần lấy (mặc định: 10)"
                }
            },
            "required": ["client_id"]
        }
    },

    # Tool 3: Lập biên bản điều tra rủi ro / Khóa thẻ khẩn cấp (Action Tool)
    {
        "name": "file_investigation_report",
        "description": "Lập biên bản kết luận điều tra rủi ro gian lận hoặc phát hành lệnh xử lý (khóa thẻ, cảnh báo SMS).",
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "Mã khách hàng được lập biên bản (ví dụ: '1081')"
                },
                "risk_level": {
                    "type": "string",
                    "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                    "description": "Mức độ rủi ro đánh giá"
                },
                "action": {
                    "type": "string",
                    "enum": ["BLOCK_CARD", "ALERT_CUSTOMER", "MONITOR", "CLEAR_FLAG"],
                    "description": "Biện pháp xử lý đề xuất"
                },
                "findings": {
                    "type": "string",
                    "description": "Tóm tắt ngắn gọn các phát hiện bất thường từ dữ liệu"
                }
            },
            "required": ["client_id", "risk_level", "action", "findings"]
        }
    },

    # --------------------------------------------------------------------------
    # TODO 1.2: HOÀN THIỆN TOOL SCHEMA CHO 'schedule_appointment' THEO CHUẨN LAB
    # --------------------------------------------------------------------------
    {
        "name": "schedule_appointment",
        "description": "Đặt lịch hẹn tư vấn giải quyết rủi ro với Chuyên viên An ninh Ngân hàng.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "Mã khách hàng cần đặt lịch (ví dụ: '1081' hoặc 'SV2026001')"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian hẹn (ví dụ: '14:00 15/09/2026')"
                },
                "advisor_name": {
                    "type": "string",
                    "description": "Tên chuyên viên tiếp nhận (ví dụ: 'Chuyên viên An ninh Thẻ')"
                }
            },
            "required": ["student_id", "datetime_str"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

_USERS_CACHE: Dict[str, Dict[str, Any]] = {}
_CARDS_CACHE: Dict[str, List[Dict[str, Any]]] = {}
_MCC_CACHE: Dict[str, str] = {}
_TRANSACTIONS_CACHE: Dict[str, List[Dict[str, Any]]] = {}

def _init_caches():
    """Tải dữ liệu danh mục người dùng, thẻ và MCC vào bộ nhớ để truy vấn cực nhanh"""
    global _USERS_CACHE, _CARDS_CACHE, _MCC_CACHE
    if _USERS_CACHE:
        return
    
    users_file = os.path.join(BASE_DATA_DIR, "users_data.csv")
    if os.path.exists(users_file):
        with open(users_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                _USERS_CACHE[row["id"].strip()] = row
                
    cards_file = os.path.join(BASE_DATA_DIR, "cards_data.csv")
    if os.path.exists(cards_file):
        with open(cards_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                c_id = row["client_id"].strip()
                _CARDS_CACHE.setdefault(c_id, []).append(row)
                
    mcc_file = os.path.join(BASE_DATA_DIR, "mcc_codes.json")
    if os.path.exists(mcc_file):
        with open(mcc_file, "r", encoding="utf-8") as f:
            _MCC_CACHE = json.load(f)

_init_caches()

def execute_get_customer_profile(client_id: str = None, student_id: str = None) -> str:
    """Thực thi tra cứu hồ sơ tài chính & danh sách thẻ"""
    raw_id = client_id if client_id is not None else student_id
    c_id = str(raw_id).strip() if raw_id is not None else ""
    user = _USERS_CACHE.get(c_id)
    if not user:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy dữ liệu khách hàng có mã '{c_id}' trong hệ thống ngân hàng."
        }, ensure_ascii=False)
    
    user_cards = _CARDS_CACHE.get(c_id, [])
    cards_summary = [
        {
            "card_id": c["id"],
            "brand": c["card_brand"],
            "type": c["card_type"],
            "credit_limit": c["credit_limit"],
            "has_chip": c["has_chip"],
            "card_on_dark_web": c.get("card_on_dark_web", "No")
        } for c in user_cards
    ]
    
    return json.dumps({
        "status": "SUCCESS",
        "client_id": c_id,
        "data": {
            "age": user.get("current_age"),
            "gender": user.get("gender"),
            "yearly_income": user.get("yearly_income"),
            "total_debt": user.get("total_debt"),
            "credit_score": user.get("credit_score"),
            "address": user.get("address"),
            "cards_count": len(user_cards),
            "cards": cards_summary
        }
    }, ensure_ascii=False)

def execute_query_recent_transactions(client_id: str, limit: int = 10) -> str:
    """Thực thi tra cứu lịch sử giao dịch gần đây và giải mã MCC"""
    c_id = str(client_id).strip()
    if c_id not in _USERS_CACHE:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Khách hàng '{client_id}' không tồn tại trong hệ thống."
        }, ensure_ascii=False)
        
    if c_id not in _TRANSACTIONS_CACHE:
        tx_file = os.path.join(BASE_DATA_DIR, "transactions_data.csv")
        results = []
        if os.path.exists(tx_file):
            with open(tx_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["client_id"].strip() == c_id:
                        mcc_val = row.get("mcc", "")
                        results.append({
                            "tx_id": row["id"],
                            "date": row["date"],
                            "amount": row["amount"],
                            "method": row["use_chip"],
                            "merchant_city": row["merchant_city"],
                            "merchant_state": row["merchant_state"],
                            "mcc": mcc_val,
                            "mcc_category": _MCC_CACHE.get(mcc_val, "Other"),
                            "errors": row.get("errors", "")
                        })
                        if len(results) >= 20:
                            break
        _TRANSACTIONS_CACHE[c_id] = results

    records = _TRANSACTIONS_CACHE.get(c_id, [])[:int(limit)]
    return json.dumps({
        "status": "SUCCESS",
        "client_id": c_id,
        "total_fetched": len(records),
        "transactions": records
    }, ensure_ascii=False)

def execute_file_investigation_report(client_id: str, risk_level: str, action: str, findings: str) -> str:
    """Thực thi lập biên bản rủi ro gian lận / khóa thẻ"""
    c_id = str(client_id).strip()
    ticket_id = f"IR-BANK-{c_id}-2026"
    return json.dumps({
        "status": "SUCCESS",
        "ticket_id": ticket_id,
        "client_id": c_id,
        "risk_level": risk_level,
        "action_taken": action,
        "findings": findings,
        "message": f"Đã lập biên bản điều tra thành công mã {ticket_id} cho khách hàng {c_id}. Lệnh '{action}' với mức rủi ro {risk_level} đã được kích hoạt."
    }, ensure_ascii=False)

def execute_schedule_appointment(student_id: str, datetime_str: str, advisor_name: str = "Chuyên viên An ninh Thẻ") -> str:
    """Hàm tương thích cho appointment"""
    return json.dumps({
        "status": "SUCCESS",
        "booking_id": f"BK-{student_id}-99",
        "student_id": student_id,
        "datetime": datetime_str,
        "advisor": advisor_name,
        "message": f"Đặt lịch thành công cho tài khoản {student_id} với {advisor_name} vào lúc {datetime_str}."
    }, ensure_ascii=False)

# Router gọi tool thực tế
TOOL_ROUTER = {
    "get_customer_profile": execute_get_customer_profile,
    "academic_query": execute_get_customer_profile,
    "query_recent_transactions": execute_query_recent_transactions,
    "file_investigation_report": execute_file_investigation_report,
    "schedule_appointment": execute_schedule_appointment
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
