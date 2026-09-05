# -*- coding: utf-8 -*-
"""
人民日报评论爬虫
遍历当天所有版面，找到版名含“评论”的版面，抓取其前 N 篇正文文章。
当天没有评论版时返回空列表（上层据此暂停推送）。
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


def get_page_list(year, month, day):
    """
    获取当天所有版面，返回 [(版名, 版面url), ...]。
    版名如 '09版：评论'；顺序即报纸版序。
    """
    url = f'{BASE}{year}{month}/{day}/node_01.html'
    bs = bs4.BeautifulSoup(fetch(url), 'html.parser')

    pages = []
    # 新版结构：swiper-container 内每个 swiper-slide 是一个版面
    cont = bs.find('div', attrs={'class': 'swiper-container'})
    if cont:
        slides = cont.find_all('div', attrs={'class': 'swiper-slide'})
        for s in slides:
            a = s.find('a')
            if not a:
                continue
            name = a.get_text(strip=True)
            href = a.get('href', '')
            if href:
                pages.append((name, urljoin(url, href)))
    else:
        # 旧版结构兜底
        temp = bs.find('div', attrs={'id': 'pageList'})
        if temp:
            for div in temp.ul.find_all('div', attrs={'class': 'right_title-name'}):
                a = div.find('a')
                if a:
                    pages.append((a.get_text(strip=True), urljoin(url, a.get('href', ''))))
    return pages


def get_title_links(page_url):
    """获取某版面的文章链接列表（保序去重）。"""
    bs = bs4.BeautifulSoup(fetch(page_url), 'html.parser')

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
                full = urljoin(page_url, href)
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


def find_comment_pages(pages):
    """从版面列表里挑出版名含“评论”的版面。"""
    return [(name, url) for name, url in pages if '评论' in name]


def crawl_comments(year, month, day, top_n=2):
    """
    抓取当天评论版前 top_n 篇文章。
    返回 (articles, page_name)：
      - 有评论版：articles 为文章列表，page_name 为版名
      - 无评论版：([], None)
    """
    pages = get_page_list(year, month, day)
    if not pages:
        return [], None

    comment_pages = find_comment_pages(pages)
    if not comment_pages:
        return [], None

    articles = []
    used_name = None
    for name, page_url in comment_pages:
        links = get_title_links(page_url)
        for url in links:
            art = get_article(url)
            # 过滤正文过短的条目（图片报道、责编署名等）
            if len(art['body']) < 200:
                continue
            art['page'] = name
            articles.append(art)
            used_name = used_name or name
            if len(articles) >= top_n:
                return articles, used_name
    return articles, used_name


if __name__ == '__main__':
    import datetime
    d = datetime.date.today()
    arts, page = crawl_comments(f'{d.year}', f'{d.month:02d}', f'{d.day:02d}', top_n=2)
    if not arts:
        print('今日无评论版，跳过。')
    else:
        print(f'评论版：{page}，共取 {len(arts)} 篇')
        for i, a in enumerate(arts, 1):
            print(f'--- {i}. {a["title"]} ({len(a["body"])}字) ---')
            print(a['body'][:120], '...\n')
