#!/usr/bin/env python3
"""
需求分析脚本：分析文字/图片/视频/文件，提取结构化信息
"""

import sys
import json
import os
from pathlib import Path

# MiniMax API 配置
API_BASE = "https://api.minimax.chat/v1"
API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MODEL = "MiniMax-M2.7"

def analyze_text(text: str) -> dict:
    """
    分析文字需求，提取关键信息
    """
    prompt = f"""分析以下需求，提取关键信息，返回 JSON 格式：

需求内容：
{text}

提取以下字段：
- client_name: 客户称呼（如果提到）
- budget_min: 最低预算（数字，单位元）
- budget_max: 最高预算（数字，单位元）
- deadline: 期望工期（文字描述）
- requirement_summary: 一句话需求摘要
- requirement_detail: 详细需求描述

如果没有提到某项，设为 null。

返回格式：
{{
  "client_name": "...",
  "budget_min": null,
  "budget_max": null,
  "deadline": "...",
  "requirement_summary": "...",
  "requirement_detail": "..."
}}
"""
    # TODO: 实现 MiniMax API 调用
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
    """
    # TODO: 实现 MiniMax 视觉 API 调用
    return {
        "description": "图片内容描述（待实现）",
        "type": "screenshot"  # screenshot/design/error/other
    }

def analyze_video(video_path: str) -> dict:
    """
    分析视频内容
    """
    # TODO: 实现 MiniMax 视频分析 API 调用
    return {
        "description": "视频内容描述（待实现）",
        "duration": None,
        "key_frames": []
    }

def analyze_file(file_path: str) -> dict:
    """
    分析文件内容
    """
    ext = Path(file_path).suffix.lower()

    if ext in ['.txt', '.md', '.pdf', '.doc', '.docx']:
        # 文本类文件，读取内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "description": content[:500] + "..." if len(content) > 500 else content,
                "type": "document"
            }
        except:
            return {
                "description": "文件内容无法读取",
                "type": "unknown"
            }
    else:
        return {
            "description": f"文件类型: {ext}",
            "type": "binary"
        }

def main():
    if len(sys.argv) < 3:
        print("用法: python analyze.py <type> <path>")
        print("  type: text/image/video/file")
        print("  path: 文件路径或文本内容")
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