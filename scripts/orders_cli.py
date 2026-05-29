#!/usr/bin/env python3
"""
订单管理 CLI

用法:
  python orders_cli.py list [status]
  python orders_cli.py view <order_id>
  python orders_cli.py update <order_id> --status <status>
  python orders_cli.py messages <order_id>
  python orders_cli.py search <keyword>
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.db import get_order, list_orders, update_order_status, get_messages

STATUS_COLORS = {
    "pending": "🟡",
    "confirmed": "🟢",
    "rejected": "🔴",
    "in_progress": "🔵",
    "done": "✅",
    "paid": "💰"
}

STATUS_NAMES = {
    "pending": "待确认",
    "confirmed": "已接单",
    "rejected": "已婉拒",
    "in_progress": "进行中",
    "done": "已交付",
    "paid": "已结算"
}

def format_order(order: dict, brief: bool = True) -> str:
    """格式化订单显示"""
    status = order.get('status', 'pending')
    status_icon = STATUS_COLORS.get(status, '⚪')
    status_name = STATUS_NAMES.get(status, status)

    budget = ""
    if order.get('budget_min') and order.get('budget_max'):
        budget = f"¥{order['budget_min']}-{order['budget_max']}"
    elif order.get('budget_min'):
        budget = f"¥{order['budget_min']}+"
    elif order.get('budget_max'):
        budget = f"~¥{order['budget_max']}"
    else:
        budget = "待定"

    created = order.get('created_at', '')[:16] if order.get('created_at') else ''

    if brief:
        summary = order.get('requirement_summary', '无')[:40]
        return f"{status_icon} #{order['id']:3d} | {status_name:4s} | {budget:12s} | {summary}"
    else:
        attachments = json.loads(order.get('attachments', '[]'))
        attachment_info = f"{len(attachments)} 个附件" if attachments else "无"

        return f"""📋 订单 #{order['id']}

【客户】{order.get('client_name', '未知')}
【预算】{budget}
【工期】{order.get('deadline', '待定')}
【状态】{status_icon} {status_name}
【附件】{attachment_info}
【时间】{created}

【需求摘要】
{order.get('requirement_summary', '无')}

【详细需求】
{order.get('requirement_detail', '无')}
"""

def cmd_list(args):
    """列出订单"""
    status = args[0] if args else None
    orders = list_orders(status)

    if not orders:
        print("暂无订单")
        return

    print(f"{'状态':8s} | {'ID':4s} | {'预算':12s} | {'需求摘要'}")
    print("-" * 80)

    for order in orders:
        status = order.get('status', 'pending')
        status_icon = STATUS_COLORS.get(status, '⚪')
        status_name = STATUS_NAMES.get(status, status)

        budget = ""
        if order.get('budget_min') and order.get('budget_max'):
            budget = f"¥{order['budget_min']}-{order['budget_max']}"
        elif order.get('budget_min'):
            budget = f"¥{order['budget_min']}+"
        elif order.get('budget_max'):
            budget = f"~¥{order['budget_max']}"
        else:
            budget = "待定"

        summary = order.get('requirement_summary', '无')[:40]
        created = order.get('created_at', '')[:16] if order.get('created_at') else ''

        print(f"{status_icon}{status_name:6s} | #{order['id']:3d} | {budget:12s} | {summary} ({created})")

def cmd_view(args):
    """查看订单详情"""
    if not args:
        print("用法: orders_cli.py view <order_id>")
        sys.exit(1)

    order_id = int(args[0])
    order = get_order(order_id)

    if not order:
        print(f"订单 #{order_id} 不存在")
        sys.exit(1)

    print(format_order(order, brief=False))

def cmd_update(args):
    """更新订单状态"""
    if len(args) < 2:
        print("用法: orders_cli.py update <order_id> --status <status>")
        sys.exit(1)

    order_id = int(args[0])

    # 解析 --status 参数
    status = None
    for i, arg in enumerate(args):
        if arg == "--status" and i + 1 < len(args):
            status = args[i + 1]
            break

    if not status:
        print("缺少 --status 参数")
        sys.exit(1)

    if status not in STATUS_NAMES:
        print(f"无效状态: {status}")
        print(f"可选: {', '.join(STATUS_NAMES.keys())}")
        sys.exit(1)

    if update_order_status(order_id, status):
        print(f"订单 #{order_id} 状态已更新为: {STATUS_COLORS[status]} {STATUS_NAMES[status]}")
    else:
        print(f"更新失败，订单 #{order_id} 不存在")
        sys.exit(1)

def cmd_messages(args):
    """查看订单消息"""
    if not args:
        print("用法: orders_cli.py messages <order_id>")
        sys.exit(1)

    order_id = int(args[0])
    messages = get_messages(order_id)

    if not messages:
        print("暂无消息记录")
        return

    for msg in messages:
        sender_icon = "👤" if msg['sender'] == 'client' else "🤖"
        sender_name = "客户" if msg['sender'] == 'client' else "Agent"
        content = msg.get('content', '')
        created = msg.get('created_at', '')[:16]

        print(f"\n{sender_icon} {sender_name} ({created})")
        print(content)

def cmd_search(args):
    """搜索订单"""
    if not args:
        print("用法: orders_cli.py search <keyword>")
        sys.exit(1)

    keyword = args[0].lower()
    orders = list_orders()

    matched = []
    for order in orders:
        text = json.dumps(order, ensure_ascii=False).lower()
        if keyword in text:
            matched.append(order)

    if not matched:
        print(f"没有找到包含 '{keyword}' 的订单")
        return

    print(f"找到 {len(matched)} 个匹配的订单:\n")
    for order in matched:
        print(format_order(order))

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "list":
        cmd_list(args)
    elif cmd == "view":
        cmd_view(args)
    elif cmd == "update":
        cmd_update(args)
    elif cmd == "messages":
        cmd_messages(args)
    elif cmd == "search":
        cmd_search(args)
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()