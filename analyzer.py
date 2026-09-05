# -*- coding: utf-8 -*-
"""
调用 DeepSeek 对评论文章做五段式分析。
"""
import os
import requests

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_URL = 'https://api.deepseek.com/chat/completions'

PROMPT_TEMPLATE = """你是申论阅卷老师兼写作教练。下面是一篇《人民日报》评论，请帮我把它拆成能直接用于申论备考的干货，简明扼要，不要客套和赏析式空话。

【一句话立意】用一句话说清：这篇文章针对什么问题、亮明什么核心观点。

【标题怎么学】拆解标题由哪些关键词构成、用了什么技巧（对仗/设问/化用等），给出1个我能直接套用的拟题公式。

【文章骨架】用提纲形式还原全文框架（提出问题→分析问题→解决问题→升华），每层一句话概括，标出各分论点。这是我要背的谋篇模板。

【论证怎么打】作者从哪几个角度分析问题、用了什么论证方法（举例/引用/对比/因果等）？解决方案与开头的问题如何形成闭环？

【可抄语料】摘3—5句金句或规范表达（原文照抄），再列2—3个可复用素材（人物/事例/数据/政策表述），每条注明"适用话题：xx"。

===== 文章标题 =====
{title}

===== 文章正文 =====
{body}
"""


def analyze(article, model='deepseek-chat', timeout=180):
    """对单篇文章调用 DeepSeek，返回分析文本。"""
    if not DEEPSEEK_API_KEY:
        raise RuntimeError('未设置 DEEPSEEK_API_KEY 环境变量')

    prompt = PROMPT_TEMPLATE.format(title=article['title'], body=article['body'])
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': '你是申论阅卷老师兼写作教练，擅长把范文拆成可背诵的框架和可套用的语料，回答简明、直指采分点，不说赏析式空话。'},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.6,
        'stream': False,
    }
    r = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data['choices'][0]['message']['content']


if __name__ == '__main__':
    demo = {
        'title': '测试标题',
        'body': '这是一段用于测试 DeepSeek 接口是否连通的示例正文。' * 20,
    }
    print(analyze(demo)[:500])
