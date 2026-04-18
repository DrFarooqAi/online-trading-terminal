import feedparser
import streamlit as st
from config import RSS_FEEDS, NEWS_MAX_PER_FEED


@st.cache_data(ttl=300)
def get_news_headlines() -> list:
    items = []
    for feed_cfg in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_cfg["url"])
            for entry in feed.entries[:NEWS_MAX_PER_FEED]:
                title = entry.get("title", "").strip()
                if not title:
                    continue
                items.append({
                    "title"    : title,
                    "source"   : feed_cfg["name"],
                    "url"      : entry.get("link", ""),
                    "published": entry.get("published", entry.get("updated", "")),
                    "tag"      : "NEUTRAL",   # overwritten by gemini_tagger
                })
        except Exception:
            pass
    return items
