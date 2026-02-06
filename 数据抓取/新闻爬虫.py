"""
新闻爬虫模块
负责从各大媒体网站抓取汽车行业HR相关新闻
"""

import requests
from bs4 import BeautifulSoup
import time
import yaml
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re


class 新闻爬虫:
    def __init__(self, 配置文件路径: str = "配置文件.yaml"):
        """初始化爬虫"""
        with open(配置文件路径, 'r', encoding='utf-8') as f:
            self.配置 = yaml.safe_load(f)

        self.爬虫配置 = self.配置['crawler']
        self.公司列表 = [c for c in self.配置['companies'] if c['enabled']]
        self.请求头 = {
            'User-Agent': self.爬虫配置['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

    def 抓取新闻(self) -> List[Dict]:
        """主函数：抓取所有公司的新闻"""
        所有新闻 = []

        print(f"开始抓取新闻... 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        for 公司 in self.公司列表:
            print(f"\n正在抓取 {公司['name']} 相关新闻...")
            关键词 = 公司['keywords'][0]  # 使用第一个关键词

            # 从各个数据源抓取
            新闻列表 = self._从36氪抓取(关键词, 公司['name'])
            新闻列表.extend(self._从虎嗅抓取(关键词, 公司['name']))
            新闻列表.extend(self._从通用搜索抓取(关键词, 公司['name']))

            所有新闻.extend(新闻列表)
            print(f"{公司['name']} 抓取到 {len(新闻列表)} 条新闻")

            # 延迟，避免被封
            time.sleep(self.爬虫配置['request_delay'])

        print(f"\n总计抓取 {len(所有新闻)} 条新闻")
        return self._去重(所有新闻)

    def _从36氪抓取(self, 关键词: str, 公司名: str) -> List[Dict]:
        """从36氪抓取新闻"""
        新闻列表 = []
        try:
            # 36氪搜索API（这是示例，实际需要根据网站结构调整）
            url = f"https://www.36kr.com/search/articles/{关键词}"

            响应 = requests.get(url, headers=self.请求头, timeout=self.爬虫配置['timeout'])

            if 响应.status_code == 200:
                soup = BeautifulSoup(响应.text, 'lxml')

                # 解析新闻列表（需要根据实际网页结构调整选择器）
                文章列表 = soup.find_all('div', class_='article-item', limit=self.爬虫配置['max_news_per_source'])

                for 文章 in 文章列表:
                    try:
                        标题元素 = 文章.find('a', class_='title')
                        if not 标题元素:
                            continue

                        新闻 = {
                            'id': self._生成id(标题元素.text.strip()),
                            'title': 标题元素.text.strip(),
                            'url': 'https://www.36kr.com' + 标题元素.get('href', ''),
                            'source': '36氪',
                            'company': 公司名,
                            'publish_time': self._提取时间(文章),
                            'abstract': self._提取摘要(文章),
                            'crawl_time': datetime.now().isoformat(),
                            'keywords': [关键词, 公司名],
                        }

                        # 只保留最近N天的新闻
                        if self._是否在时间范围内(新闻['publish_time']):
                            新闻列表.append(新闻)
                    except Exception as e:
                        print(f"解析单条新闻出错: {e}")
                        continue

        except Exception as e:
            print(f"从36氪抓取出错: {e}")

        return 新闻列表

    def _从虎嗅抓取(self, 关键词: str, 公司名: str) -> List[Dict]:
        """从虎嗅网抓取新闻"""
        新闻列表 = []
        try:
            url = f"https://www.huxiu.com/search?s={关键词}"

            响应 = requests.get(url, headers=self.请求头, timeout=self.爬虫配置['timeout'])

            if 响应.status_code == 200:
                soup = BeautifulSoup(响应.text, 'lxml')

                # 这里需要根据虎嗅的实际网页结构调整
                文章列表 = soup.find_all('div', class_='search-item', limit=self.爬虫配置['max_news_per_source'])

                for 文章 in 文章列表:
                    try:
                        标题元素 = 文章.find('a', class_='search-item-title')
                        if not 标题元素:
                            continue

                        新闻 = {
                            'id': self._生成id(标题元素.text.strip()),
                            'title': 标题元素.text.strip(),
                            'url': 标题元素.get('href', ''),
                            'source': '虎嗅网',
                            'company': 公司名,
                            'publish_time': self._提取时间(文章),
                            'abstract': self._提取摘要(文章),
                            'crawl_time': datetime.now().isoformat(),
                            'keywords': [关键词, 公司名],
                        }

                        if self._是否在时间范围内(新闻['publish_time']):
                            新闻列表.append(新闻)
                    except Exception as e:
                        print(f"解析单条新闻出错: {e}")
                        continue

        except Exception as e:
            print(f"从虎嗅抓取出错: {e}")

        return 新闻列表

    def _从通用搜索抓取(self, 关键词: str, 公司名: str) -> List[Dict]:
        """从通用搜索引擎抓取（备用方案）"""
        # 这里可以使用今日头条、搜狗搜索等其他渠道
        # 为了演示，这里返回空列表
        return []

    def _提取时间(self, 文章元素) -> str:
        """提取发布时间"""
        try:
            时间元素 = 文章元素.find('time')
            if 时间元素:
                return 时间元素.get('datetime', '')

            # 尝试其他常见的时间选择器
            时间文本 = 文章元素.find('span', class_='time')
            if 时间文本:
                return self._解析相对时间(时间文本.text)

        except Exception:
            pass

        return datetime.now().isoformat()

    def _提取摘要(self, 文章元素) -> str:
        """提取文章摘要"""
        try:
            摘要元素 = 文章元素.find('p', class_='abstract')
            if 摘要元素:
                return 摘要元素.text.strip()

            # 尝试其他选择器
            摘要元素 = 文章元素.find('div', class_='summary')
            if 摘要元素:
                return 摘要元素.text.strip()

        except Exception:
            pass

        return ""

    def _解析相对时间(self, 时间文本: str) -> str:
        """解析"3小时前"这类相对时间"""
        现在 = datetime.now()

        if '分钟前' in 时间文本:
            分钟数 = int(re.search(r'\d+', 时间文本).group())
            时间 = 现在 - timedelta(minutes=分钟数)
        elif '小时前' in 时间文本:
            小时数 = int(re.search(r'\d+', 时间文本).group())
            时间 = 现在 - timedelta(hours=小时数)
        elif '天前' in 时间文本:
            天数 = int(re.search(r'\d+', 时间文本).group())
            时间 = 现在 - timedelta(days=天数)
        else:
            时间 = 现在

        return 时间.isoformat()

    def _是否在时间范围内(self, 发布时间: str) -> bool:
        """检查新闻是否在指定时间范围内"""
        try:
            发布日期 = datetime.fromisoformat(发布时间.replace('Z', '+00:00'))
            天数限制 = self.爬虫配置['days_to_fetch']
            截止日期 = datetime.now() - timedelta(days=天数限制)
            return 发布日期 > 截止日期
        except Exception:
            return True  # 如果无法解析时间，则保留

    def _生成id(self, 标题: str) -> str:
        """根据标题生成唯一ID"""
        import hashlib
        return hashlib.md5(标题.encode('utf-8')).hexdigest()[:16]

    def _去重(self, 新闻列表: List[Dict]) -> List[Dict]:
        """根据ID去重"""
        已见id = set()
        去重后列表 = []

        for 新闻 in 新闻列表:
            if 新闻['id'] not in 已见id:
                已见id.add(新闻['id'])
                去重后列表.append(新闻)

        print(f"去重前: {len(新闻列表)} 条, 去重后: {len(去重后列表)} 条")
        return 去重后列表

    def 保存到文件(self, 新闻列表: List[Dict], 文件路径: str = None):
        """保存到JSON文件"""
        if not 文件路径:
            文件路径 = self.配置['storage']['json_path']

        # 加载现有数据
        现有数据 = []
        try:
            with open(文件路径, 'r', encoding='utf-8') as f:
                现有数据 = json.load(f)
        except FileNotFoundError:
            pass

        # 合并并去重
        所有id = {新闻['id'] for 新闻 in 现有数据}
        新增数量 = 0

        for 新闻 in 新闻列表:
            if 新闻['id'] not in 所有id:
                现有数据.append(新闻)
                新增数量 += 1

        # 按时间倒序排序
        现有数据.sort(key=lambda x: x['crawl_time'], reverse=True)

        # 保存
        with open(文件路径, 'w', encoding='utf-8') as f:
            json.dump(现有数据, f, ensure_ascii=False, indent=2)

        print(f"\n数据已保存到 {文件路径}")
        print(f"新增 {新增数量} 条新闻，总计 {len(现有数据)} 条")


def 主程序():
    """命令行运行入口"""
    爬虫 = 新闻爬虫()
    新闻列表 = 爬虫.抓取新闻()
    爬虫.保存到文件(新闻列表)

    print("\n✅ 新闻抓取完成！")


if __name__ == "__main__":
    主程序()
