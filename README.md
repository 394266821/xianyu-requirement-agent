# 闲鱼需求收集 Agent

微信收到客户需求 → 自动整理结构化工单 → 推送给你确认 → 自动回复客户

## 功能

- [ ] 接收文字消息，提取：工期、预算、需求描述
- [ ] 接收图片，分析内容（截图/设计稿）
- [ ] 接收视频，分析内容
- [ ] 接收文件，描述文件内容
- [ ] 形成结构化工单
- [ ] 微信推送确认
- [ ] 自动回复客户

## 目录结构

```
.
├── db/             # SQLite 数据库
├── data/           # 附件存储
├── scripts/        # Python 脚本
├── skills/         # Hermes Skill
└── README.md
```

## 使用

```bash
# 查看订单列表
python scripts/orders_cli.py list

# 查看订单详情
python scripts/orders_cli.py view <order_id>

# 更新订单状态
python scripts/orders_cli.py update <order_id> --status doing
```

## 工作流程

```
客户微信发需求
    ↓
Hermes 接收 + 分析（文字/图片/视频/文件）
    ↓
结构化工单 + 存储 SQLite
    ↓
微信推送给你（格式化工单）
    ↓
你回复：接单/婉拒/询价
    ↓
自动发消息给客户 + 更新订单状态
```