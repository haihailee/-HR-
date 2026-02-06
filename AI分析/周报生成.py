"""
AI周报生成模块
使用智谱AI生成本周HR大事记总结
"""

from datetime import datetime, timedelta
from typing import List, Dict
import json


class 周报生成器:
    def __init__(self, ai客户端=None):
        """初始化周报生成器"""
        self.ai客户端 = ai客户端

    def 生成本周大事记(self, 新闻列表: List[Dict]) -> Dict:
        """生成本周大事记总结"""
        # 筛选本周新闻
        本周新闻 = self._筛选本周新闻(新闻列表)

        if not 本周新闻:
            return {
                'summary': '本周暂无重要HR动态',
                'top_events': [],
                'company_updates': {},
                'trends': [],
                'insight': '数据收集中，敬请期待下周精彩内容。'
            }

        # 如果有AI客户端，使用AI生成
        if self.ai客户端:
            return self._ai生成总结(本周新闻)
        else:
            # 否则使用规则生成
            return self._规则生成总结(本周新闻)

    def _筛选本周新闻(self, 新闻列表: List[Dict]) -> List[Dict]:
        """筛选本周的新闻"""
        现在 = datetime.now()
        本周开始 = 现在 - timedelta(days=现在.weekday())  # 本周一
        本周开始 = 本周开始.replace(hour=0, minute=0, second=0, microsecond=0)

        本周新闻 = []
        for 新闻 in 新闻列表:
            try:
                发布时间 = datetime.fromisoformat(新闻['crawl_time'])
                if 发布时间 >= 本周开始:
                    本周新闻.append(新闻)
            except:
                pass

        return 本周新闻

    def _规则生成总结(self, 本周新闻: List[Dict]) -> Dict:
        """使用规则生成总结（无AI时的备用方案）"""
        from collections import Counter

        # 统计各公司新闻数
        公司统计 = Counter(n['company'] for n in 本周新闻)

        # 统计HR分类
        分类统计 = Counter(n.get('hr_category', '其他') for n in 本周新闻)

        # TOP3事件（按时间排序，取最新的）
        本周新闻_sorted = sorted(本周新闻, key=lambda x: x['crawl_time'], reverse=True)
        top_events = []
        for 新闻 in 本周新闻_sorted[:3]:
            top_events.append({
                'title': 新闻['title'],
                'company': 新闻['company'],
                'category': 新闻.get('hr_category', '未分类'),
                'summary': 新闻.get('summary', '暂无摘要')
            })

        # 按公司汇总
        company_updates = {}
        for 公司, 数量 in 公司统计.most_common(5):
            公司新闻 = [n for n in 本周新闻 if n['company'] == 公司]
            company_updates[公司] = {
                'count': 数量,
                'latest': 公司新闻[0]['title'] if 公司新闻 else ''
            }

        # 趋势分析
        trends = []
        最热分类 = 分类统计.most_common(1)[0] if 分类统计 else ('', 0)
        if 最热分类[0]:
            trends.append(f"{最热分类[0]}成为本周热点，共{最热分类[1]}条相关新闻")

        最活跃公司 = 公司统计.most_common(1)[0] if 公司统计 else ('', 0)
        if 最活跃公司[0]:
            trends.append(f"{最活跃公司[0]}动作频繁，本周发布{最活跃公司[1]}条HR相关信息")

        # 洞察
        insight = f"本周共监测到{len(本周新闻)}条HR动态，{len(公司统计)}家公司有新动作。"

        return {
            'summary': f"本周汽车行业HR动态活跃，共{len(本周新闻)}条重要信息",
            'top_events': top_events,
            'company_updates': company_updates,
            'trends': trends,
            'insight': insight
        }

    def _ai生成总结(self, 本周新闻: List[Dict]) -> Dict:
        """使用AI生成总结"""
        # 准备新闻内容
        新闻文本 = ""
        for i, 新闻 in enumerate(本周新闻[:20], 1):  # 最多分析20条
            新闻文本 += f"{i}. 【{新闻['company']}】{新闻['title']}\n"
            新闻文本 += f"   {新闻.get('summary', '')}\n\n"

        提示词 = f"""
请分析以下本周汽车行业HR新闻，生成一份简洁的大事记总结。

本周新闻：
{新闻文本}

请按以下格式输出JSON：
{{
  "summary": "一句话总结本周整体情况（30字以内）",
  "top_events": [
    {{"title": "事件标题", "company": "公司", "impact": "影响分析"}}
  ],
  "trends": ["趋势1", "趋势2", "趋势3"],
  "insight": "一句话洞察（50字以内，给HR从业者的启示）"
}}

要求：
1. top_events选择3个最重要的事件
2. trends总结3个关键趋势
3. 语言专业、简洁
4. 只输出JSON，不要其他内容
"""

        try:
            响应 = self.ai客户端.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": 提示词}],
                temperature=0.7,
            )

            结果文本 = 响应.choices[0].message.content.strip()

            # 尝试解析JSON
            # 清理可能的markdown代码块标记
            if '```json' in 结果文本:
                结果文本 = 结果文本.split('```json')[1].split('```')[0]
            elif '```' in 结果文本:
                结果文本 = 结果文本.split('```')[1].split('```')[0]

            结果 = json.loads(结果文本)
            return 结果

        except Exception as e:
            print(f"AI生成失败，使用规则生成: {e}")
            return self._规则生成总结(本周新闻)


def 生成本周大事记(新闻列表: List[Dict], ai客户端=None) -> Dict:
    """快捷函数：生成本周大事记"""
    生成器 = 周报生成器(ai客户端)
    return 生成器.生成本周大事记(新闻列表)
