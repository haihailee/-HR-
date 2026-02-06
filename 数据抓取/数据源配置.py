"""
数据源配置
定义各个新闻网站的URL和解析规则
"""

# 新闻数据源配置
数据源列表 = {
    "36氪": {
        "search_url": "https://www.36kr.com/search/articles/{keyword}",
        "selectors": {
            "article_list": "div.article-item",
            "title": "a.title",
            "url": "a.title",
            "abstract": "p.abstract",
            "time": "time"
        },
        "enabled": True
    },

    "虎嗅网": {
        "search_url": "https://www.huxiu.com/search?s={keyword}",
        "selectors": {
            "article_list": "div.search-item",
            "title": "a.search-item-title",
            "url": "a.search-item-title",
            "abstract": "div.search-item-summary",
            "time": "span.time"
        },
        "enabled": True
    },

    "钛媒体": {
        "search_url": "https://www.tmtpost.com/search?q={keyword}",
        "selectors": {
            "article_list": "div.article-item",
            "title": "h3.title a",
            "url": "h3.title a",
            "abstract": "div.content",
            "time": "span.time"
        },
        "enabled": True
    }
}

# 备用数据源（如主数据源失效）
备用数据源 = {
    "今日头条": {
        "search_url": "https://so.toutiao.com/search?keyword={keyword}",
        "enabled": False
    },

    "搜狐科技": {
        "search_url": "https://search.sohu.com/?keyword={keyword}",
        "enabled": False
    }
}
