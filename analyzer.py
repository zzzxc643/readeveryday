# -*- coding: utf-8 -*-
"""
调用 DeepSeek 对评论文章做五段式分析。
"""
import os
import requests

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_URL = 'https://api.deepseek.com/chat/completions'

PROMPT_TEMPLATE = """请阅读下面这篇《人民日报》评论文章，按以下五个部分进行分析：

一、标题分析
用一句话概括：这个标题由哪几个关键词构成，表达了什么核心意思，从中可以提炼出什么拟标题的方法？

二、文章结构分析
梳理出这篇文章的逻辑框架（例如：现象引入→问题分析→原因剖析→对策建议→总结升华），并简要说明各部分是如何衔接推进的。

三、观点提炼
问题1：这篇文章的核心论点是什么？围绕它设置了哪些分论点？
问题2：作者如何看待这个问题？核心主张是什么？与同类话题相比，作者的视角有何独特之处？

四、问题逻辑分析
发现问题：这篇文章回应了什么现实问题或社会现象？问题的实质是什么？
分析问题：作者从哪些角度分析问题？用了什么方法让分析有说服力？
解决问题：作者提出了什么倡导、路径或方案？它们如何与中心论点形成逻辑闭环？

五、表达与素材积累
提炼文中值得学习的金句、规范表达（3—5句），并摘录可用素材（人物、事例、数据等），注明其适用话题。

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
            {'role': 'system', 'content': '你是一位资深的时政评论写作导师，擅长拆解评论文章的谋篇布局与论证逻辑。'},
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
