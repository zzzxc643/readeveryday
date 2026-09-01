# -*- coding: utf-8 -*-
"""
主入口：抓取当天人民日报评论版前 2 篇 → DeepSeek 分析 → 存 JSON → 生成静态网站。

用法：
    python main.py            # 抓今天
    python main.py 20260901   # 抓指定日期(YYYYMMDD)
"""
import os
import sys
import json
import datetime

import crawler
import analyzer
import site_builder

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data')


def run(date_str=None, top_n=2, skip_ai=False):
    if date_str:
        d = datetime.datetime.strptime(date_str, '%Y%m%d').date()
    else:
        d = datetime.date.today()
    y, m, dd = f'{d.year}', f'{d.month:02d}', f'{d.day:02d}'
    day = f'{y}{m}{dd}'

    print(f'[1/3] 抓取 {y}-{m}-{dd} 评论版前 {top_n} 篇...')
    articles = crawler.crawl_comments(y, m, dd, top_n=top_n)
    if not articles:
        print('  未抓到任何文章（当天可能未发布或版面结构变化）。')
        return
    for a in articles:
        print(f'  - {a["title"]} ({len(a["body"])}字)')

    print('[2/3] DeepSeek 分析...')
    for i, art in enumerate(articles, 1):
        if skip_ai:
            art['analysis'] = '(本次跳过 AI 分析)'
            continue
        print(f'  分析第 {i} 篇：{art["title"]} ...')
        try:
            art['analysis'] = analyzer.analyze(art)
            print(f'    完成，{len(art["analysis"])} 字。')
        except Exception as e:
            art['analysis'] = f'(分析失败：{e})'
            print(f'    失败：{e}')

    # 存 JSON（累积历史）
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, f'{day}.json'), 'w', encoding='utf-8') as f:
        json.dump({'articles': articles}, f, ensure_ascii=False, indent=2)

    print('[3/3] 生成静态网站...')
    site_builder.build_all()
    print('全部完成。')


if __name__ == '__main__':
    arg = None
    skip = False
    for a in sys.argv[1:]:
        if a == '--skip-ai':
            skip = True
        else:
            arg = a
    run(arg, skip_ai=skip)
