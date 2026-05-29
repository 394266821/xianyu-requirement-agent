#!/usr/bin/env python3
"""
微信通知模块
"""

import os
import json
from datetime import datetime

# 从 Hermes 配置读取微信信息
WEIXIN_HOME_CHANNEL = os.environ.get("WEIXIN_HOME_CHANNEL", "o9cq80_Tw3b1eYWs7BEVJQ7wg9e0@im.wechat")

def format_order_message(order: dict) -> str:
    """格式化工单消息"""
    budget = f"¥{order['budget_min']}-{order['budget_max']}" if order.get('budget_min') and order.get('budget_max') else "待定"
    deadline = order.get('deadline') or "待定"
    client = order.get('client_name') or "未知"

    attachments = json.loads(order.get('attachments', '[]'))
    attachment_info = f"{len(attachments)} 个附件" if attachments else "无"

    created = order.get('created_at', '')
    if created:
        try:
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            created = dt.strftime("%m-%d %H:%M")
        except:
            pass

    return f"""📋 订单 #{order['id']} 待确认

【客户】{client}
【预算】{budget}
【工期】{deadline}
【需求摘要】
{order.get('requirement_summary', '无')}

【详细需求】
{order.get('requirement_detail', '无')}

【附件】{attachment_info}

⏰ 收到时间：{created}
"""

def notify_new_order(order: dict) -> bool:
    """
    推送新订单给你确认
    使用 Hermes send_message 工具发送
    """
    message = format_order_message(order)
    message += "\n回复：接单 / 婉拒 / 询价"

    # 这里通过环境变量或配置文件获取推送目标
    # 实际推送由 Agent 调用 send_message 工具完成
    print(f"[通知] 准备推送工单 #{order['id']} 到 {WEIXIN_HOME_CHANNEL}")
    print(message)
    return True

def notify_order_confirmed(order: dict, customer_response: str) -> bool:
    """通知客户已接单"""
    response_messages = {
        "confirmed": "好的，需求已收到，我这边安排开发，请问你方便什么时候开始？",
        "rejected": "抱歉，目前暂无档期承接新项目，建议您联系其他开发者，感谢理解！",
        "inquiry": "请提供更多信息：1) 需求详细描述 2) 参考案例 3) 预期交付时间"
    }

    return response_messages.get(customer_response, "收到，我会尽快处理")

if __name__ == "__main__":
    # 测试
    test_order = {
        "id": 1,
        "client_name": "张三",
        "budget_min": 2000,
        "budget_max": 3000,
        "deadline": "2周",
        "requirement_summary": "需要一个电商小程序",
        "requirement_detail": "包含商品展示、购物车、微信支付功能",
        "attachments": "[]",
        "created_at": datetime.now().isoformat()
    }
    notify_new_order(test_order)