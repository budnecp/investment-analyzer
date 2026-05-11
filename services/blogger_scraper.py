"""
博主/分析师观点爬取服务
从 gold-eagle.com 等来源爬取黄金分析文章
"""
import pandas as pd
import streamlit as st
from config import BLOGGER_SOURCES, POSITIVE_KEYWORDS, NEGATIVE_KEYWORDS

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_SCRAPING = True
except ImportError:
    HAS_SCRAPING = False


def _simple_sentiment(text: str) -> str:
    """基于关键词的简单情感分析"""
    text_lower = text.lower()
    pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw.lower() in text_lower)
    neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw.lower() in text_lower)

    if pos_count > neg_count:
        return "看多"
    elif neg_count > pos_count:
        return "看空"
    else:
        return "中性"


def _scrape_gold_eagle() -> list:
    """爬取 gold-eagle.com 的黄金分析文章"""
    if not HAS_SCRAPING:
        return []

    articles = []
    urls = [
        "https://www.gold-eagle.com/article/gold",
        "https://www.gold-eagle.com/article/silver",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    for url in urls:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            # 尝试多种选择器
            items = soup.select("div.views-row") or soup.select("article") or soup.select("div.node")

            for item in items[:10]:
                try:
                    # 标题
                    title_el = item.select_one("h2 a, h3 a, .field-name-title a, .title a")
                    title = title_el.get_text(strip=True) if title_el else ""

                    # 链接
                    link = ""
                    if title_el and title_el.get("href"):
                        href = title_el.get("href", "")
                        if href.startswith("/"):
                            link = "https://www.gold-eagle.com" + href
                        else:
                            link = href

                    # 摘要
                    summary_el = item.select_one(".field-name-body, .field-type-text-with-summary, .summary, p")
                    summary = summary_el.get_text(strip=True)[:200] if summary_el else title

                    # 作者
                    author_el = item.select_one(".field-name-field-article-author a, .username, .author a, .field-name-uid a")
                    author = author_el.get_text(strip=True) if author_el else "Gold-Eagle Analyst"

                    # 日期
                    date_el = item.select_one(".field-name-post-date, .date-display-single, time, .post-date")
                    date_str = date_el.get_text(strip=True) if date_el else ""

                    if not title:
                        continue

                    sentiment = _simple_sentiment(title + " " + summary)

                    articles.append({
                        "博主": author,
                        "平台": "Gold-Eagle",
                        "观点": summary if summary else title,
                        "标题": title,
                        "链接": link,
                        "时间": date_str,
                        "方向": sentiment,
                    })
                except Exception:
                    continue

        except Exception as e:
            continue

    return articles


def _scrape_investing_com() -> list:
    """爬取 investing.com 的黄金分析文章"""
    if not HAS_SCRAPING:
        return []

    articles = []
    url = "https://www.investing.com/news/commodities-news/gold"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        items = soup.select("article.articleItem") or soup.select("div.largeTitle article")

        for item in items[:8]:
            try:
                title_el = item.select_one("a.title, .articleTitle a")
                title = title_el.get_text(strip=True) if title_el else ""
                link = title_el.get("href", "") if title_el else ""
                if link and not link.startswith("http"):
                    link = "https://www.investing.com" + link

                # 作者
                author_el = item.select_one(".articleDetails span, .authorName")
                author = author_el.get_text(strip=True).replace("By ", "") if author_el else "Investing.com"

                # 日期
                date_el = item.select_one(".articleDetails span:nth-child(2), .date")
                date_str = date_el.get_text(strip=True) if date_el else ""

                if not title:
                    continue

                sentiment = _simple_sentiment(title)

                articles.append({
                    "博主": author,
                    "平台": "Investing.com",
                    "观点": title,
                    "标题": title,
                    "链接": link,
                    "时间": date_str,
                    "方向": sentiment,
                })
            except Exception:
                continue

    except Exception:
        pass

    return articles


@st.cache_data(ttl=600, show_spinner="正在爬取博主/分析师观点...")
def get_all_blogger_views() -> pd.DataFrame:
    """
    获取所有博主的最新观点
    """
    all_views = []

    # 爬取 Gold-Eagle
    try:
        gold_eagle_views = _scrape_gold_eagle()
        all_views.extend(gold_eagle_views)
    except Exception:
        pass

    # 爬取 Investing.com
    try:
        investing_views = _scrape_investing_com()
        all_views.extend(investing_views)
    except Exception:
        pass

    if not all_views:
        # 返回友好提示
        placeholder = []
        for name, info in BLOGGER_SOURCES.items():
            placeholder.append({
                "博主": name,
                "平台": info["platform"],
                "观点": "暂时无法获取数据，请稍后重试",
                "标题": "-",
                "链接": info.get("url", ""),
                "时间": "-",
                "方向": "待定",
            })
        return pd.DataFrame(placeholder)

    return pd.DataFrame(all_views)


def calculate_blogger_score(views_df: pd.DataFrame) -> dict:
    """
    综合博主观点评分
    """
    if views_df.empty:
        return {"score": 50, "direction": "中性", "confidence": "低"}

    directions = views_df["方向"].tolist()
    bullish = sum(1 for d in directions if d == "看多")
    bearish = sum(1 for d in directions if d == "看空")
    neutral = sum(1 for d in directions if d == "中性")
    total = len(directions)

    if total == 0:
        return {"score": 50, "direction": "中性", "confidence": "低"}

    score = 50 + (bullish / total - bearish / total) * 50
    score = max(0, min(100, score))

    if score >= 60:
        direction = "偏多"
    elif score <= 40:
        direction = "偏空"
    else:
        direction = "中性"

    confidence = "高" if total >= 5 else "中" if total >= 3 else "低"

    return {
        "score": round(score, 1),
        "direction": direction,
        "confidence": confidence,
        "bullish_count": bullish,
        "bearish_count": bearish,
        "neutral_count": neutral,
    }
