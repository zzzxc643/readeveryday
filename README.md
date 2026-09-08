# 人民日报评论 → DeepSeek 分析 → 手机网页

每天自动抓取《人民日报》评论版（第09版）前 2 篇，用 DeepSeek 做五段式写作分析，
生成手机友好的静态网页，通过 GitHub Pages 发布。iPhone 加到主屏幕即可像 app 一样看。

## 流程

```
GitHub Actions(每日 07:00 北京时间)
  → 爬人民日报评论版前 2 篇
  → 每篇交给 DeepSeek 分析（五段式）
  → 生成静态网页(docs/)
  → 部署到 GitHub Pages
  → iPhone Safari 打开 → 添加到主屏幕
```

## 文件说明
- `crawler.py`      抓取评论版文章（已用 urljoin 修正 URL、过滤图片/署名条目）
- `analyzer.py`     调用 DeepSeek（五段式分析提示词内置）
- `site_builder.py` 渲染手机版静态网站
- `main.py`         串起全流程：抓取 → 分析 → 存 JSON → 建站
- `data/*.json`     每日数据，累积成历史
- `docs/`           网站（GitHub Pages 根目录）
- `.github/workflows/daily.yml`  每日定时 + 自动部署

## 本地运行

```bash
pip install -r requirements.txt

# 设置 DeepSeek 密钥后运行
export DEEPSEEK_API_KEY=sk-xxxx
python main.py            # 抓今天
python main.py 20260901   # 抓指定日期
python main.py --skip-ai  # 跳过 AI（只抓取+建站，用于快速预览）

# 本地预览网站
python -m http.server 8757 --directory docs
# 浏览器打开 http://localhost:8757
```

## 上云部署（每天自动跑）

1. **建仓库**：在 GitHub 新建一个仓库（可设为 Public，Pages 免费）。
2. **推代码**：把本目录内容推到该仓库的 `main` 分支。
3. **填密钥**：仓库 → Settings → Secrets and variables → Actions →
   New repository secret，添加 `DEEPSEEK_API_KEY`。
4. **开 Pages**：仓库 → Settings → Pages → Source 选 **GitHub Actions**。
5. **触发一次**：Actions 页面 → 选 workflow → Run workflow（手动测试）。
   之后每天北京时间 07:00 自动运行。
6. **访问**：部署成功后网址为 `https://<用户名>.github.io/<仓库名>/`。
   iPhone Safari 打开 → 分享 → 添加到主屏幕。

## 备注
- DeepSeek 分析每篇约 2000–3500 字，两篇合计每天约几分钱成本。
- 若某天人民日报未发布或版面结构变化，脚本会打印提示并跳过，不影响历史页面。
