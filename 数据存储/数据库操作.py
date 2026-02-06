"""
数据库操作模块
提供JSON和SQLite两种存储方式
"""

import json
import sqlite3
from typing import List, Dict
from datetime import datetime


class 数据存储:
    def __init__(self, 存储类型: str = "json", 文件路径: str = "数据/新闻数据.json"):
        self.存储类型 = 存储类型
        self.文件路径 = 文件路径

        if 存储类型 == "sqlite":
            self._初始化数据库()

    def _初始化数据库(self):
        """初始化SQLite数据库表结构"""
        conn = sqlite3.connect(self.文件路径)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS 新闻表 (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT,
                source TEXT,
                company TEXT,
                publish_time TEXT,
                abstract TEXT,
                crawl_time TEXT,
                is_hr_related INTEGER,
                hr_category TEXT,
                summary TEXT,
                keywords TEXT
            )
        """)

        conn.commit()
        conn.close()

    def 保存新闻(self, 新闻列表: List[Dict]):
        """保存新闻数据"""
        if self.存储类型 == "json":
            self._保存到json(新闻列表)
        elif self.存储类型 == "sqlite":
            self._保存到sqlite(新闻列表)

    def 加载新闻(self) -> List[Dict]:
        """加载新闻数据"""
        if self.存储类型 == "json":
            return self._从json加载()
        elif self.存储类型 == "sqlite":
            return self._从sqlite加载()

    def _保存到json(self, 新闻列表: List[Dict]):
        """保存到JSON文件"""
        现有数据 = self._从json加载()

        # 合并去重
        现有id = {n['id'] for n in 现有数据}
        for 新闻 in 新闻列表:
            if 新闻['id'] not in 现有id:
                现有数据.append(新闻)

        # 排序
        现有数据.sort(key=lambda x: x.get('crawl_time', ''), reverse=True)

        with open(self.文件路径, 'w', encoding='utf-8') as f:
            json.dump(现有数据, f, ensure_ascii=False, indent=2)

    def _从json加载(self) -> List[Dict]:
        """从JSON文件加载"""
        try:
            with open(self.文件路径, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _保存到sqlite(self, 新闻列表: List[Dict]):
        """保存到SQLite数据库"""
        conn = sqlite3.connect(self.文件路径)
        cursor = conn.cursor()

        for 新闻 in 新闻列表:
            keywords_str = ','.join(新闻.get('keywords', []))

            cursor.execute("""
                INSERT OR REPLACE INTO 新闻表
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                新闻['id'],
                新闻['title'],
                新闻.get('url', ''),
                新闻.get('source', ''),
                新闻.get('company', ''),
                新闻.get('publish_time', ''),
                新闻.get('abstract', ''),
                新闻.get('crawl_time', ''),
                1 if 新闻.get('is_hr_related') else 0,
                新闻.get('hr_category', ''),
                新闻.get('summary', ''),
                keywords_str
            ))

        conn.commit()
        conn.close()

    def _从sqlite加载(self) -> List[Dict]:
        """从SQLite数据库加载"""
        conn = sqlite3.connect(self.文件路径)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM 新闻表 ORDER BY crawl_time DESC")
        rows = cursor.fetchall()

        新闻列表 = []
        for row in rows:
            新闻 = {
                'id': row[0],
                'title': row[1],
                'url': row[2],
                'source': row[3],
                'company': row[4],
                'publish_time': row[5],
                'abstract': row[6],
                'crawl_time': row[7],
                'is_hr_related': bool(row[8]),
                'hr_category': row[9],
                'summary': row[10],
                'keywords': row[11].split(',') if row[11] else []
            }
            新闻列表.append(新闻)

        conn.close()
        return 新闻列表
