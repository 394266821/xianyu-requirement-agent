#!/usr/bin/env python3
"""AI工具素材收集脚本 - 无需认证版本"""
import json
import urllib.request
import urllib.error
from datetime import datetime

today = datetime.now().strftime("%m月%d日")
print(f"🤖 AI工具情报 — {today}")
print("=" * 40)

tools = []

# 方法1: 抓取 AIHub 导航站
try:
    req = urllib.request.Request(
        "https://www.aihub.cn/",
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8')
        # 简单解析标题
        import re
        names = re.findall(r'data-v-\w+="([^"]+)">([^<]{2,20})</a>', content)
        for name in names[:10]:
            tools.append({
                'name': name[1],
                'desc': 'AI工具',
                'url': '#',
                'votes': 0,
                'source': 'AIHub'
            })
except Exception as e:
    print(f"AIHub: {e}")

# 方法2: Product Hunt 抓取（网页版）
try:
    req = urllib.request.Request(
        "https://www.producthunt.com/",
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8')
        import re
        # 匹配产品卡片
        items = re.findall(r'href="/products/([^"]+)"[^>]*>([^<]{2,50})</[^>]+>', content)
        for item in items[:8]:
            name = item[1].strip()
            if name and len(name) > 2:
                tools.append({
                    'name': name,
                    'desc': 'Product Hunt 热门',
                    'url': f'https://producthunt.com/products/{item[0]}',
                    'votes': 0,
                    'source': 'Product Hunt'
                })
except Exception as e:
    print(f"Product Hunt: {e}")

# 方法3: AlternativeMe AI排行榜
try:
    req = urllib.request.Request(
        "https://alternativeme.com/ai-tools/",
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8')
        import re
        items = re.findall(r'<h3[^>]*>([^<]+)</h3>', content)
        for item in items[:8]:
            name = item.strip()
            if name and len(name) > 2:
                tools.append({
                    'name': name,
                    'desc': 'AI工具',
                    'url': '#',
                    'votes': 0,
                    'source': 'AlternativeMe'
                })
except Exception as e:
    print(f"AlternativeMe: {e}")

# 方法4: 读取本地缓存或使用备用数据
if not tools:
    print("使用备用数据...")
    tools = [
        {'name': 'ChatGPT', 'desc': 'OpenAI 大语言模型，用于对话、写作、编程', 'url': 'https://chat.openai.com', 'votes': 99999, 'source': 'OpenAI'},
        {'name': 'Midjourney', 'desc': 'AI绘图工具，通过文字描述生成精美图片', 'url': 'https://midjourney.com', 'votes': 88888, 'source': 'Midjourney'},
        {'name': 'Claude', 'desc': 'Anthropic AI 助手，擅长长文本分析和代码', 'url': 'https://claude.ai', 'votes': 77777, 'source': 'Anthropic'},
        {'name': 'Stable Diffusion', 'desc': '开源AI绘图模型，本地部署免费使用', 'url': 'https://stability.ai', 'votes': 66666, 'source': 'Stability AI'},
        {'name': 'Cursor', 'desc': 'AI编程工具，集成GPT-4辅助写代码', 'url': 'https://cursor.sh', 'votes': 55555, 'source': 'Cursor'},
    ]

# 去重
seen = set()
unique_tools = []
for t in tools:
    if t['name'] not in seen:
        seen.add(t['name'])
        unique_tools.append(t)

tools = unique_tools[:8]

print(f"\n今天给你准备了 {len(tools)} 个新鲜AI工具")
print("可以做成小红书图文/抖音口播素材：\n")

for i, t in enumerate(tools[:5], 1):
    print(f"{i}. 【{t['name']}】")
    desc = t.get('desc', 'AI工具')
    print(f"   {desc}")
    url = t.get('url', '#')
    if url and url != '#':
        print(f"   🔗 {url}")
    votes = t.get('votes', 0)
    source = t.get('source', '')
    if votes > 0:
        print(f"   ❤️ {votes} (🔥{source})")
    print()

print("-" * 40)
print("\n📌 制作建议：")
print("• 封面标题：「这个AI工具也太牛了吧」")
print("• 内容结构：工具介绍 → 能解决什么问题 → 怎么用")
print("• 评论区互动：「你用过这个吗？」")
print("\n💡 回复「素材」获取更多")