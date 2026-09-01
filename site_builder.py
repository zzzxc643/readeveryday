# -*- coding: utf-8 -*-
"""
把每日数据渲染成手机友好的静态网站，输出到 docs/（GitHub Pages 根目录）。

数据存储：data/YYYYMMDD.json（每天一个文件，累积成历史）
产出：
  docs/index.html         首页，按日期倒序列出
  docs/YYYYMMDD.html      当天详情（两篇：原文 + DeepSeek 分析）
  docs/manifest.json      PWA 清单（添加到主屏幕）
"""
import os
import re
import json
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data')
DOCS_DIR = os.path.join(ROOT, 'docs')

STYLE = """
:root{--bg:#f7f7f8;--card:#fff;--ink:#1a1a1a;--sub:#6b6b6b;--line:#ecec ec;--accent:#c0392b}
*{box-sizing:border-box;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.75 -apple-system,BlinkMacSystemFont,'PingFang SC','Segoe UI',sans-serif}
header{position:sticky;top:0;background:var(--accent);color:#fff;padding:14px 16px;
  font-size:18px;font-weight:600;box-shadow:0 1px 6px rgba(0,0,0,.15);z-index:9}
.wrap{max-width:760px;margin:0 auto;padding:16px}
a{color:var(--accent);text-decoration:none}
.card{background:var(--card);border-radius:14px;padding:16px 18px;margin:12px 0;
  box-shadow:0 1px 3px rgba(0,0,0,.06)}
.card h2{margin:.1em 0 .3em;font-size:18px}
.date{font-size:13px;color:var(--sub)}
.count{font-size:13px;color:var(--sub);margin-top:4px}
.back{display:inline-block;margin-bottom:8px}
.sub{color:var(--sub);font-size:14px;margin:-.3em 0 1em}
h1.title{font-size:22px;line-height:1.4;margin:.2em 0}
.section{background:var(--card);border-radius:14px;padding:18px;margin:16px 0;
  box-shadow:0 1px 3px rgba(0,0,0,.06)}
.tag{display:inline-block;background:var(--accent);color:#fff;border-radius:6px;
  padding:2px 10px;font-size:13px;margin-bottom:10px}
.tag.ai{background:#2c3e50}
.body p{margin:.7em 0;text-indent:2em}
.ai-body p{margin:.6em 0}
.ai-body{white-space:normal}
.src{font-size:13px;color:var(--sub);margin-top:14px;word-break:break-all}
footer{text-align:center;color:var(--sub);font-size:12px;padding:24px}
""".replace("ec ec", "ececec")

HEAD = """<!doctype html><html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#c0392b">
<link rel="manifest" href="manifest.json">
<title>{title}</title>
<style>{style}</style>
</head><body>"""


def _esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _paras(text):
    out = ''
    for line in (text or '').split('\n'):
        line = line.strip()
        if line:
            out += '<p>' + _esc(line) + '</p>\n'
    return out


def _fmt_date(d):
    # d = 'YYYYMMDD'
    return f'{d[0:4]}-{d[4:6]}-{d[6:8]}'


def build_day(day, record):
    """渲染单日页面。record = {'date','articles':[{title,subtitle,body,url,analysis}]}"""
    title = f'人民日报评论 {_fmt_date(day)}'
    html = HEAD.format(title=title, style=STYLE)
    html += f'<header>📰 人民日报评论分析</header><div class="wrap">'
    html += '<a class="back" href="index.html">← 返回目录</a>'
    html += f'<div class="date">{_fmt_date(day)} · 第09版评论</div>'

    for art in record['articles']:
        html += '<article>'
        html += f'<h1 class="title">{_esc(art["title"])}</h1>'
        if art.get('subtitle'):
            html += f'<div class="sub">{_esc(art["subtitle"])}</div>'

        html += '<div class="section"><span class="tag">原文</span>'
        html += f'<div class="body">{_paras(art["body"])}</div>'
        if art.get('url'):
            html += f'<div class="src">原文链接：<a href="{_esc(art["url"])}">{_esc(art["url"])}</a></div>'
        html += '</div>'

        html += '<div class="section"><span class="tag ai">DeepSeek 分析</span>'
        html += f'<div class="ai-body">{_paras(art.get("analysis",""))}</div>'
        html += '</div>'
        html += '</article>'

    html += '</div><footer>由 GitHub Actions 每日自动生成</footer></body></html>'
    return html


def build_index(records):
    """records = [{'date','articles'}...] 已按日期倒序。"""
    html = HEAD.format(title='人民日报评论分析', style=STYLE)
    html += '<header>📰 人民日报评论分析</header><div class="wrap">'
    if not records:
        html += '<div class="card">暂无内容，等待每日自动更新。</div>'
    for rec in records:
        day = rec['date']
        titles = ' / '.join(a['title'] for a in rec['articles'])
        html += f'<a href="{day}.html"><div class="card">'
        html += f'<div class="date">{_fmt_date(day)}</div>'
        html += f'<h2>{_esc(titles)}</h2>'
        html += f'<div class="count">共 {len(rec["articles"])} 篇 · 含 DeepSeek 分析</div>'
        html += '</div></a>'
    html += '</div><footer>由 GitHub Actions 每日自动生成</footer></body></html>'
    return html


MANIFEST = {
    "name": "人民日报评论分析",
    "short_name": "评论分析",
    "start_url": "index.html",
    "display": "standalone",
    "background_color": "#f7f7f8",
    "theme_color": "#c0392b",
    "icons": []
}


def build_all():
    os.makedirs(DOCS_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*.json')), reverse=True)
    records = []
    for fp in files:
        with open(fp, encoding='utf-8') as f:
            rec = json.load(f)
        day = re.sub(r'\D', '', os.path.basename(fp))[:8]
        rec['date'] = day
        records.append(rec)
        with open(os.path.join(DOCS_DIR, f'{day}.html'), 'w', encoding='utf-8') as f:
            f.write(build_day(day, rec))

    with open(os.path.join(DOCS_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(build_index(records))
    with open(os.path.join(DOCS_DIR, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(MANIFEST, f, ensure_ascii=False, indent=2)

    print(f'已生成 {len(records)} 天，输出目录：{DOCS_DIR}')
    return len(records)


if __name__ == '__main__':
    build_all()
