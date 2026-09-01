# -*- coding: utf-8 -*-
"""
人民日报评论版爬虫
抓取指定日期第 09 版（评论）的文章列表，返回前 N 篇的标题与正文。
"""
import requests
import bs4
from urllib.parse import urljoin

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}

BASE = 'http://paper.people.com.cn/rmrb/pc/layout/'


def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text


def get_title_links(year, month, day, node='09'):
    """获取某版面的文章链接列表（保序去重）。"""
    url = f'{BASE}{year}{month}/{day}/node_{node}.html'
    bs = bs4.BeautifulSoup(fetch(url), 'html.parser')

    temp = bs.find('div', attrs={'id': 'titleList'})
    if temp:
        lis = temp.ul.find_all('li')
    else:
        ul = bs.find('ul', attrs={'class': 'news-list'})
        lis = ul.find_all('li') if ul else []

    links, seen = [], set()
    for li in lis:
        for a in li.find_all('a'):
            href = a.get('href', '')
            if 'content' in href:
                full = urljoin(url, href)
                if full not in seen:
                    seen.add(full)
                    links.append(full)
    return links


def get_article(url):
    """解析一篇文章，返回 dict(title, subtitle, body, url)。"""
    bs = bs4.BeautifulSoup(fetch(url), 'html.parser')

    def txt(tag):
        el = getattr(bs, tag, None)
        return el.get_text(strip=True) if el else ''

    h3, h1, h2 = txt('h3'), txt('h1'), txt('h2')
    title = h1 or h3 or h2 or '(无标题)'
    subtitle = '　'.join(p for p in [h3, h2] if p)

    body = ''
    oz = bs.find('div', attrs={'id': 'ozoom'})
    if oz:
        for p in oz.find_all('p'):
            t = p.get_text().strip()
            if t:
                body += t + '\n\n'

    return {'title': title, 'subtitle': subtitle, 'body': body.strip(), 'url': url}


def crawl_comments(year, month, day, top_n=2, node='09'):
    """抓取评论版前 top_n 篇文章。"""
    links = get_title_links(year, month, day, node=node)
    articles = []
    for url in links:
        art = get_article(url)
        # 过滤掉正文过短的条目（图片报道、责编署名等）
        if len(art['body']) < 200:
            continue
        articles.append(art)
        if len(articles) >= top_n:
            break
    return articles


if __name__ == '__main__':
    import datetime
    d = datetime.date.today()
    arts = crawl_comments(f'{d.year}', f'{d.month:02d}', f'{d.day:02d}', top_n=2)
    for i, a in enumerate(arts, 1):
        print(f'--- {i}. {a["title"]} ({len(a["body"])}字) ---')
        print(a['body'][:120], '...\n')
