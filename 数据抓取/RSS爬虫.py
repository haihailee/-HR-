"""
RSS新闻抓取模块
从各大媒体的RSS源抓取汽车行业HR相关新闻
"""

import feedparser
import requests
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re


class RSS爬虫:
    """RSS爬虫类"""

    def __init__(self):
        """初始化RSS爬虫"""
        self.请求头 = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.RSS源列表 = self._获取RSS源列表()

        # 监控的公司关键词
        self.公司关键词 = {
            '特斯拉': ['特斯拉', 'Tesla', '马斯克'],
            '小米汽车': ['小米汽车', '小米SU7', '雷军造车', '小米新车'],
            '问界': ['问界', 'AITO', '华为汽车', '余承东'],
            '小鹏汽车': ['小鹏', 'XPENG', '何小鹏'],
            '蔚来汽车': ['蔚来', 'NIO', '李斌'],
            '理想汽车': ['理想', '理想汽车', '李想'],
            '比亚迪': ['比亚迪', 'BYD', '王传福']
        }

        # HR相关关键词
        self.HR关键词 = [
            '招聘', '人才', 'offer', '校招', '社招', '猎聘', '内推', '入职',
            '薪资', '工资', '涨薪', '年终奖', '股票', '期权', '股权激励', '持股', '分红',
            '培训', '晋升', '发展', '学习', '企业大学', '成长',
            '组织架构', '裁员', '优化', '调整', '重组', '人事变动', '人员流动',
            '企业文化', '价值观', '团建', '离职', '员工',
            '职位', '岗位', '人力资源', 'HR', '人事', '团队', '管理者',
            '薪酬', '福利', '待遇', '奖金', '激励',
            '首席人才官', 'CHO', '高管', '管理人员', 'CEO', 'CTO', 'COO'
        ]

    def _获取RSS源列表(self) -> List[Dict]:
        """获取RSS源列表"""
        return [
            {
                'name': '36氪',
                'url': 'https://36kr.com/feed',
                'enabled': True,
                'category': '科技'
            },
            {
                'name': '虎嗅网',
                'url': 'https://www.huxiu.com/rss/0.xml',
                'enabled': True,
                'category': '科技'
            },
            {
                'name': '钛媒体',
                'url': 'https://www.tmtpost.com/rss.xml',
                'enabled': True,
                'category': '科技'
            },
            {
                'name': 'InfoQ',
                'url': 'https://www.infoq.cn/feed',
                'enabled': True,
                'category': '技术'
            },
            {
                'name': '第一财经',
                'url': 'https://www.yicai.com/feed',
                'enabled': True,
                'category': '财经'
            },
            {
                'name': '新浪科技',
                'url': 'https://tech.sina.com.cn/rss/digi.xml',
                'enabled': True,
                'category': '科技'
            },
            {
                'name': '腾讯科技',
                'url': 'https://tech.qq.com/rss/tech.xml',
                'enabled': True,
                'category': '科技'
            },
            {
                'name': '第一电动网',
                'url': 'https://www.d1ev.com/feed.xml',
                'enabled': True,
                'category': '汽车'
            },
            {
                'name': '盖世汽车',
                'url': 'https://auto.gasgoo.com/rss.xml',
                'enabled': True,
                'category': '汽车'
            }
        ]

    def 抓取所有RSS(self, 最大文章数: int = 100) -> List[Dict]:
        """从所有RSS源抓取新闻"""
        所有文章 = []

        print(f"开始从RSS源抓取新闻... 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        for RSS源 in self.RSS源列表:
            if not RSS源.get('enabled', True):
                continue

            print(f"\n抓取 {RSS源['name']} ({RSS源['url']})...")
            文章列表 = self._抓取单个RSS(RSS源, 最大文章数)
            所有文章.extend(文章列表)
            print(f"{RSS源['name']} 抓取到 {len(文章列表)} 条新闻")

            # 延迟避免请求过快
            time.sleep(1)

        print(f"\n总计从RSS抓取 {len(所有文章)} 条新闻")
        return 所有文章

    def _抓取单个RSS(self, RSS源: Dict, 最大文章数: int) -> List[Dict]:
        """抓取单个RSS源"""
        文章列表 = []

        try:
            # 设置超时时间
            feedparser.USER_AGENT = self.请求头['User-Agent']

            # 解析RSS
            feed = feedparser.parse(RSS源['url'])

            if feed.bozo:
                # RSS解析出错，尝试用requests获取内容后解析
                响应 = requests.get(RSS源['url'], headers=self.请求头, timeout=10)
                if 响应.status_code == 200:
                    feed = feedparser.parse(响应.content)
                else:
                    print(f"  ❌ 无法获取RSS: HTTP {响应.status_code}")
                    return 文章列表

            if not feed.entries:
                print(f"  ⚠️ RSS源无内容或格式错误")
                return 文章列表

            # 解析文章
            for entry in feed.entries[:最大文章数]:
                文章 = self._解析RSS条目(entry, RSS源['name'])
                if 文章:
                    文章列表.append(文章)

            print(f"  ✅ 成功解析 {len(文章列表)} 条文章")

        except requests.exceptions.Timeout:
            print(f"  ⏱️  请求超时")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ 请求失败: {e}")
        except Exception as e:
            print(f"  ❌ 解析失败: {e}")

        return 文章列表

    def _解析RSS条目(self, entry: Dict, 来源: str) -> Dict:
        """解析RSS条目"""
        try:
            # 提取标题
            标题 = entry.get('title', '').strip()
            if not 标题:
                return None

            # 提取链接
            链接 = entry.get('link', '')
            if isinstance(链接, list):
                链接 = 链接[0] if 链接 else ''

            # 提取摘要
            摘要 = entry.get('description', '') or entry.get('summary', '')
            # 清理HTML标签
            摘要 = re.sub('<[^<]+?>', '', 摘要).strip()

            # 提取发布时间
            发布时间 = self._解析时间(entry)

            # 生成ID
            文章ID = self._生成ID(链接 or 标题)

            return {
                'id': 文章ID,
                'title': 标题,
                'url': 链接,
                'source': 来源,
                'company': '待分类',  # 后续会分类
                'publish_time': 发布时间,
                'abstract': 摘要[:200] if 摘要 else '',
                'crawl_time': datetime.now().isoformat(),
                'is_hr_related': False,  # 后续会判断
                'hr_category': None,
                'summary': 摘要[:300] if 摘要 else '',
                'keywords': []
            }
        except Exception as e:
            print(f"  ⚠️ 解析条目失败: {e}")
            return None

    def _解析时间(self, entry: Dict) -> str:
        """解析发布时间"""
        时间字段 = [
            'published_parsed',
            'updated_parsed',
            'created_parsed'
        ]

        for 字段名 in 时间字段:
            if 字段名 in entry:
                try:
                    time_struct = entry[字段名]
                    return datetime(*time_struct[:6]).isoformat()
                except:
                    continue

        # 最后返回当前时间
        return datetime.now().isoformat()

    def _生成ID(self, 内容: str) -> str:
        """生成唯一ID"""
        import hashlib
        return hashlib.md5(内容.encode('utf-8')).hexdigest()

    def 识别公司(self, 新闻: Dict) -> str:
        """识别新闻所属公司"""
        标题 = 新闻['title'].lower()
        摘要 = 新闻.get('summary', '').lower()
        内容 = 标题 + 摘要

        for 公司名, 关键词列表 in self.公司关键词.items():
            for 关键词 in 关键词列表:
                if 关键词.lower() in 内容:
                    return 公司名

        # 检查是否有汽车行业关键词
        汽车行业关键词 = ['汽车', '车企', '新能源车', '电动车', '智能驾驶', '自动驾驶']
        for 关键词 in 汽车行业关键词:
            if 关键词.lower() in 内容:
                return '汽车行业'

        return '其他'

    def 判断HR相关(self, 新闻: Dict) -> tuple:
        """判断新闻是否与HR相关，并返回分类"""
        标题 = 新闻['title'].lower()
        摘要 = 新闻.get('summary', '').lower()
        内容 = 标题 + 摘要

        # 检查是否包含HR关键词
        相关性得分 = 0
        匹配的关键词 = []

        for 关键词 in self.HR关键词:
            if 关键词.lower() in 标题:
                相关性得分 += 3  # 标题中出现，权重高
                匹配的关键词.append(关键词)
            elif 关键词.lower() in 摘要:
                相关性得分 += 1  # 摘要中出现，权重低
                匹配的关键词.append(关键词)

        # 判断是否相关（至少命中2个关键词或标题中有1个）
        是否相关 = 相关性得分 >= 2 or any(k.lower() in 标题 for k in self.HR关键词)

        # 检查是否是纯AI/技术报道而非HR相关
        # 如果标题包含"AI"、"技术"、"算法"等，但没有明确的HR关键词，则不相关
        高频技术词 = ['ai', '算法', '模型', '大模型', '技术', '架构', '系统', '开发', '代码', '编程']
        技术词匹配 = sum(1 for 词 in 高频技术词 if 词 in 标题.lower())
        if 技术词匹配 >= 2 and 相关性得分 < 3:
            是否相关 = False

        # 分类
        分类 = self._确定HR分类(内容, 匹配的关键词)

        # 更新新闻信息
        新闻['is_hr_related'] = 是否相关
        新闻['hr_category'] = 分类 if 是否相关 else None
        新闻['keywords'] = 匹配的关键词[:5]  # 最多5个关键词

        return 是否相关, 分类

    def _确定HR分类(self, 内容: str, 匹配关键词: List[str]) -> str:
        """确定HR分类"""
        分类规则 = {
            '招聘与人才': ['招聘', '人才', 'offer', '校招', '社招', '猎聘', 'offer'],
            '薪酬福利': ['薪资', '工资', '涨薪', '年终奖', '股票', '期权', '股权激励', '持股'],
            '培训发展': ['培训', '晋升', '发展', '学习', '企业大学', '成长'],
            '组织变革': ['组织架构', '裁员', '优化', '调整', '重组', '人事变动'],
            '企业文化': ['企业文化', '价值观', '团建'],
            '行业报告': ['报告', '研究', '数据', '趋势', '白皮书', '指数'],
            '高管动态': ['CEO', 'CTO', 'CHO', '首席', '高管', '任命', '离职']
        }

        # 按关键词匹配分类
        for 分类名, 关键词列表 in 分类规则.items():
            for 关键词 in 匹配关键词:
                if 关键词 in 关键词列表:
                    return 分类名

        return '其他'

    def 处理所有新闻(self, 新闻列表: List[Dict]) -> List[Dict]:
        """处理所有新闻：识别公司、判断HR相关性"""
        print("\n开始分析新闻内容...")

        HR相关新闻 = []

        for 新闻 in 新闻列表:
            # 识别公司
            新闻['company'] = self.识别公司(新闻)

            # 判断HR相关性
            是否相关, 分类 = self.判断HR相关(新闻)

            if 是否相关:
                HR相关新闻.append(新闻)

        print(f"✅ 分析完成！共 {len(新闻列表)} 条新闻，{len(HR相关新闻)} 条HR相关")

        return HR相关新闻

    def 去重(self, 新闻列表: List[Dict]) -> List[Dict]:
        """根据标题去重"""
        已见标题 = set()
        去重后列表 = []

        for 新闻 in 新闻列表:
            # 标题归一化（去除空格、特殊字符）
            标题归一 = re.sub(r'\s+', '', 新闻['title'].lower())
            标题归一 = re.sub(r'[^\w\u4e00-\u9fff]', '', 标题归一)

            if 标题归一 not in 已见标题:
                已见标题.add(标题归一)
                去重后列表.append(新闻)

        去重数量 = len(新闻列表) - len(去重后列表)
        if 去重数量 > 0:
            print(f"✅ 去重：移除 {去重数量} 条重复新闻")

        return 去重后列表

    def 保存到文件(self, 新闻列表: List[Dict], 文件路径: str = "数据/新闻数据.json"):
        """保存到JSON文件"""
        import os

        # 确保目录存在
        os.makedirs(os.path.dirname(文件路径), exist_ok=True)

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
                所有id.add(新闻['id'])
                新增数量 += 1

        # 按抓取时间倒序排序，只保留最近500条
        现有数据.sort(key=lambda x: x['crawl_time'], reverse=True)
        if len(现有数据) > 500:
            现有数据 = 现有数据[:500]

        # 保存
        with open(文件路径, 'w', encoding='utf-8') as f:
            json.dump(现有数据, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 数据已保存到 {文件路径}")
        print(f"   新增 {新增数量} 条新闻，总计 {len(现有数据)} 条")

        return 新增数量


def 主程序():
    """命令行运行入口"""
    爬虫 = RSS爬虫()

    # 1. 从RSS源抓取
    原始新闻 = 爬虫.抓取所有RSS(最大文章数=20)

    # 2. 去重
    去重后新闻 = 爬虫.去重(原始新闻)

    # 3. 分析内容（识别公司、判断HR相关性）
    HR新闻 = 爬虫.处理所有新闻(去重后新闻)

    # 4. 保存
    新增数量 = 爬虫.保存到文件(HR新闻)

    # 5. 输出统计
    print(f"\n{'='*60}")
    print(f"抓取完成统计：")
    print(f"  - 原始新闻: {len(原始新闻)} 条")
    print(f"  - 去重后: {len(去重后新闻)} 条")
    print(f"  - HR相关: {len(HR新闻)} 条")
    print(f"  - 新增保存: {新增数量} 条")
    print(f"{'='*60}")

    # 6. 按公司分类统计
    if HR新闻:
        print(f"\n按公司分类：")
        from collections import Counter
        公司统计 = Counter(n['company'] for n in HR新闻)
        for 公司, 数量 in 公司统计.most_common():
            print(f"  {公司}: {数量} 条")

    print("\n✅ 全部完成！")


if __name__ == "__main__":
    主程序()
