#!/usr/bin/env python3
"""
需求分析脚本：调用 MiniMax API 分析文字/图片/视频/文件
"""

import sys
import json
import os
import base64
import requests
from pathlib import Path

# API 配置
API_BASE = "https://api.minimaxi.com/anthropic/v1"
MODEL = "MiniMax-M2.7"

def get_api_key():
    """从 Claude Code 设置获取 API key"""
    settings_path = os.path.expanduser("~/.claude/settings.json")
    with open(settings_path) as f:
        settings = json.load(f)
    return settings.get("env", {}).get("ANTHROPIC_AUTH_TOKEN", "")

API_KEY = get_api_key()

def call_api(messages, max_tokens=1024):
    """调用 MiniMax Anthropic API"""
    url = f"{API_BASE}/messages"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": messages
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise Exception(f"API Error: {resp.status_code} - {resp.text}")

    data = resp.json()
    if "content" in data:
        for item in data["content"]:
            if item.get("type") == "text":
                return item["text"]
    return str(data)

def parse_json_response(response):
    """从 API 响应中提取 JSON"""
    try:
        # 尝试找 JSON 对象（可能包含换行和缩进）
        import re
        # 匹配 {...} 模式
        match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group())
        # 更宽松的匹配
        json_start = response.find('{')
        json_end = response.rfind('}')
        if json_start != -1 and json_end > json_start:
            return json.loads(response[json_start:json_end+1])
    except Exception:
        pass
    return None

def analyze_text(text: str) -> dict:
    """
    分析文字需求，提取关键信息
    """
    prompt = f"""分析以下需求，提取关键信息。返回 JSON 格式：

需求内容：
{text}

提取以下字段（如果没提到则设为 null）：
- client_name: 客户称呼
- budget_min: 最低预算（数字，单位元）
- budget_max: 最高预算（数字，单位元）
- deadline: 期望工期（文字描述）
- requirement_summary: 一句话需求摘要
- requirement_detail: 详细需求描述

返回格式（只返回 JSON，不要其他内容）：
{{
  "client_name": "...",
  "budget_min": null,
  "budget_max": null,
  "deadline": "...",
  "requirement_summary": "...",
  "requirement_detail": "..."
}}"""

    try:
        response = call_api([{"role": "user", "content": prompt}])
        result = parse_json_response(response)
        if result:
            return {
                "client_name": result.get("client_name"),
                "budget_min": result.get("budget_min"),
                "budget_max": result.get("budget_max"),
                "deadline": result.get("deadline"),
                "requirement_summary": result.get("requirement_summary"),
                "requirement_detail": result.get("requirement_detail")
            }
    except Exception as e:
        print(f"Warning: API call failed: {e}", file=sys.stderr)

    # Fallback: 简单解析
    return {
        "client_name": None,
        "budget_min": None,
        "budget_max": None,
        "deadline": None,
        "requirement_summary": text[:50] + "..." if len(text) > 50 else text,
        "requirement_detail": text
    }

def analyze_image(image_path: str) -> dict:
    """
    分析图片内容
    支持 URL 或本地文件路径
    使用 MiniMax Token Plan VLM API
    """
    import base64
    import requests

    # 获取 API key
    with open(os.path.expanduser('~/.claude/settings.json')) as f:
        settings = json.load(f)
    token = settings.get("env", {}).get("ANTHROPIC_AUTH_TOKEN", "")
    api_host = "https://api.minimaxi.com"

    # 下载图片并转为 base64 data URL
    if image_path.startswith("http://") or image_path.startswith("https://"):
        try:
            resp = requests.get(image_path, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            img_data = resp.content
            ct = resp.headers.get('content-type', 'image/jpeg').lower()
            fmt = 'jpeg' if 'jpeg' in ct else 'png' if 'png' in ct else 'webp' if 'webp' in ct else 'jpeg'
        except Exception as e:
            return {
                "description": f"图片下载失败: {e}",
                "type": "error",
                "ui_elements": "",
                "requirement_related": ""
            }
    else:
        # 本地文件
        try:
            with open(image_path, "rb") as f:
                img_data = f.read()
            ext = Path(image_path).suffix.lower()
            fmt = 'jpeg' if ext in ['.jpg', '.jpeg'] else 'png' if ext == '.png' else 'webp' if ext == '.webp' else 'jpeg'
        except Exception as e:
            return {
                "description": f"无法读取图片文件: {e}",
                "type": "error",
                "ui_elements": "",
                "requirement_related": ""
            }

    # 转为 data URL
    img_b64 = base64.b64encode(img_data).decode()
    data_url = f"data:image/{fmt};base64,{img_b64}"

    # 调用 MiniMax Token Plan VLM API
    url = f"{api_host}/v1/coding_plan/vlm"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": "请描述这张图片的内容：1) 图片类型（截图/设计稿/照片等）2) 主要内容 3) 如果是UI设计，描述布局和功能元素。回答简洁。",
        "image_url": data_url
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        data = resp.json()
        content = data.get("content", "")
        if content:
            return {
                "description": content,
                "type": "image",
                "ui_elements": "",
                "requirement_related": ""
            }
        else:
            base_resp = data.get("base_resp", {})
            status_code = base_resp.get("status_code", 0)
            if status_code == 1026:
                return {
                    "description": "图片内容涉及敏感信息，无法分析",
                    "type": "sensitive",
                    "ui_elements": "",
                    "requirement_related": ""
                }
            return {
                "description": f"API 返回异常: {base_resp.get('status_msg', 'unknown')}",
                "type": "error",
                "ui_elements": "",
                "requirement_related": str(data)
            }
    except Exception as e:
        return {
            "description": f"图片分析失败: {e}",
            "type": "error",
            "ui_elements": "",
            "requirement_related": ""
        }

def analyze_video(video_path: str) -> dict:
    """
    分析视频内容
    """
    if video_path.startswith("http://") or video_path.startswith("https://"):
        return {
            "description": "在线视频暂不支持分析",
            "duration": None,
            "key_frames": [],
            "note": "请下载视频后分析，或提供视频截图"
        }

    # 本地视频
    return {
        "description": f"视频文件: {Path(video_path).name}",
        "duration": None,
        "key_frames": [],
        "note": "视频分析需要提取关键帧，请用 analyze_image 分析截图"
    }

def analyze_file(file_path: str) -> dict:
    """
    分析文件内容
    """
    ext = Path(file_path).suffix.lower()

    if ext in ['.txt', '.md']:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "description": content[:500] + "..." if len(content) > 500 else content,
            "type": "text"
        }
    elif ext in ['.pdf', '.doc', '.docx']:
        return {
            "description": f"文档文件 ({ext})，需要文档解析工具提取内容",
            "type": "document"
        }
    elif ext in ['.py', '.js', '.html', '.css', '.json', '.yaml', '.yml', '.sh']:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return analyze_code(content, ext)
        except Exception as e:
            return {
                "description": f"文件读取失败: {e}",
                "type": "error"
            }
    else:
        return {
            "description": f"文件类型: {ext}",
            "type": "binary"
        }

def analyze_code(code: str, ext: str) -> dict:
    """分析代码内容"""
    prompt = f"""分析以下代码，简要描述：
1. 代码语言和功能
2. 主要模块和功能点
3. 技术栈

代码：
```{ext}
{code[:2000]}
```"""

    try:
        response = call_api([{"role": "user", "content": prompt}])
        return {
            "description": response[:500],
            "type": "code"
        }
    except Exception as e:
        return {
            "description": f"代码分析失败: {e}",
            "type": "code"
        }

def main():
    if len(sys.argv) < 3:
        print("用法: python analyze.py <type> <path>")
        print("  type: text/image/video/file")
        print("  path: 文件路径或 URL 或文本内容")
        sys.exit(1)

    type_ = sys.argv[1]
    path = sys.argv[2]

    if type_ == "text":
        result = analyze_text(path)
    elif type_ == "image":
        result = analyze_image(path)
    elif type_ == "video":
        result = analyze_video(path)
    elif type_ == "file":
        result = analyze_file(path)
    else:
        print(f"未知类型: {type_}")
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()