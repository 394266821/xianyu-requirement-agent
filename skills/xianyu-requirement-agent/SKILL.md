---
name: xianyu-requirement-agent
description: "闲鱼需求收集 Agent：分析客户需求，整理结构化工单，推送确认"
version: 1.0.0
author: Hermes Agent
platforms: [linux]
metadata:
  hermes:
    tags: [xianyu, requirement, order-management]
---

# 闲鱼需求收集 Agent

## 功能

接收客户发来的需求（文字/图片/视频/文件），分析提取关键信息，生成结构化工单，推送你确认后自动回复客户。

## 工作流程

### 1. 接收消息

客户通过微信发来消息，支持：
- 文字（需求描述、预算、工期）
- 图片（截图、设计稿、报错界面）
- 视频（演示、参考案例）
- 文件（文档、代码、需求文档）

### 2. 分析需求

提取以下信息：
- `client_name`: 客户称呼
- `budget_min` / `budget_max`: 预算区间
- `deadline`: 期望工期
- `requirement_summary`: 需求一句话摘要
- `requirement_detail`: 详细需求描述
- `attachments`: 附件列表（路径数组）

### 3. 生成工单

输出格式：

```
📋 订单 #{id} 待确认

【客户】{client_name}
【预算】¥{budget_min}-{budget_max}
【工期】{deadline}
【需求摘要】
{requirement_summary}
【详细需求】
{requirement_detail}
【附件】{attachment_count} 个文件

⏰ 收到时间：{created_at}
[接单] [婉拒] [询价]
```

### 4. 推送确认

将工单推送到你的微信（WEIXIN_HOME_CHANNEL: o9cq80_Tw3b1eYWs7BEVJQ7wg9e0@im.wechat），等待你的决策。

### 5. 执行决策

根据你的回复：
- **接单** → 更新订单状态为 confirmed，回复客户"好的，需求已收到，我这边安排开发，请问你方便什么时候开始？"
- **婉拒** → 更新订单状态为 rejected，回复客户"抱歉，目前暂无档期承接新项目，建议您联系其他开发者，感谢理解！"
- **询价** → 回复客户"请提供更多信息：1) 需求详细描述 2) 参考案例 3) 预期交付时间"

## 命令

### 订单管理

- `查看订单` — 列出所有待处理订单
- `订单详情 {id}` — 查看订单详细信息
- `更新状态 {id} {status}` — 更新订单状态

### 状态说明

| status | 说明 |
|--------|------|
| pending | 待确认 |
| confirmed | 已接单 |
| rejected | 已婉拒 |
| in_progress | 进行中 |
| done | 已交付 |
| paid | 已结算 |

## 数据库

- 路径: `/root/project/xianyu-requirement-agent/db/orders.db`
- 表: `orders`, `messages`

## 附件存储

- 路径: `/root/project/xianyu-requirement-agent/data/attachments/{order_id}/`
- 结构: `data/attachments/{order_id}/{message_id}/{filename}`

## 使用示例

### 处理新需求

```
用户: 我需要一个电商小程序，预算3000，两周内完成
Agent:
  1. 分析文字内容，提取关键信息
  2. 创建订单记录
  3. 推送工单给你确认:
     📋 订单 #1 待确认
     【客户】未知
     【预算】¥3000
     【工期】2周
     【需求摘要】电商小程序
     ...
  4. 等待你回复: 接单/婉拒/询价
```

### CLI 管理

```bash
cd /root/project/xianyu-requirement-agent

# 查看所有订单
python scripts/orders_cli.py list

# 查看订单详情
python scripts/orders_cli.py view 1

# 更新状态
python scripts/orders_cli.py update 1 --status in_progress

# 搜索订单
python scripts/orders_cli.py search 小程序
```