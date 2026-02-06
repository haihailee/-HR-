"""
AI内容分类和总结模块
使用智谱AI进行内容的智能分析
"""

import yaml
import json
from typing import Dict, List
from zhipuai import ZhipuAI


class AI分析器:
    def __init__(self, 配置文件路径: str = "配置文件.yaml"):
        """初始化AI分析器"""
        with open(配置文件路径, 'r', encoding='utf-8') as f:
            self.配置 = yaml.safe_load(f)

        # 初始化智谱AI客户端
        ai配置 = self.配置['ai_service']['zhipu']
        self.客户端 = ZhipuAI(api_key=ai配置['api_key'])
        self.模型 = ai配置['model']

        self.hr分类 = self.配置['hr_categories']

    def 分析新闻(self, 新闻: Dict) -> Dict:
        """分析单条新闻，返回分类和摘要"""
        print(f"正在分析: {新闻['title'][:30]}...")

        # 1. 判断是否为HR相关
        是否hr相关 = self._判断是否hr相关(新闻)

        if not 是否hr相关:
            return {
                'is_hr_related': False,
                'hr_category': None,
                'summary': None,
                'keywords': [],
            }

        # 2. 分类到具体HR模块
        hr分类 = self._分类hr模块(新闻)

        # 3. 生成摘要
        摘要 = self._生成摘要(新闻)

        # 4. 提取关键词
        关键词 = self._提取关键词(新闻, 摘要)

        return {
            'is_hr_related': True,
            'hr_category': hr分类,
            'summary': 摘要,
            'keywords': 关键词,
        }

    def _判断是否hr相关(self, 新闻: Dict) -> bool:
        """判断新闻是否与HR相关"""
        提示词 = f"""
请判断以下新闻是否与人力资源管理相关。

新闻标题：{新闻['title']}
新闻摘要：{新闻.get('abstract', '')}

人力资源相关包括：招聘、薪酬福利、培训发展、组织架构调整、企业文化、员工关系、劳动法规等。

请只回答"是"或"否"，不要其他解释。
"""

        try:
            响应 = self.客户端.chat.completions.create(
                model=self.模型,
                messages=[{"role": "user", "content": 提示词}],
                temperature=0.1,
            )

            回答 = 响应.choices[0].message.content.strip()
            return "是" in 回答

        except Exception as e:
            print(f"AI判断出错: {e}")
            # 出错时使用关键词匹配作为后备方案
            return self._关键词匹配判断(新闻)

    def _关键词匹配判断(self, 新闻: Dict) -> bool:
        """使用关键词匹配判断（后备方案）"""
        文本 = 新闻['title'] + " " + 新闻.get('abstract', '')

        for 分类 in self.hr分类:
            for 关键词 in 分类['keywords']:
                if 关键词 in 文本:
                    return True

        return False

    def _分类hr模块(self, 新闻: Dict) -> str:
        """将新闻分类到具体的HR模块"""
        分类列表 = "\n".join([f"{i+1}. {cat['name']}" for i, cat in enumerate(self.hr分类)])

        提示词 = f"""
请将以下新闻分类到最合适的人力资源模块中。

新闻标题：{新闻['title']}
新闻摘要：{新闻.get('abstract', '')}

可选分类：
{分类列表}

请只回答分类名称，不要其他解释。如果涉及多个分类，请选择最主要的一个。
"""

        try:
            响应 = self.客户端.chat.completions.create(
                model=self.模型,
                messages=[{"role": "user", "content": 提示词}],
                temperature=0.1,
            )

            分类结果 = 响应.choices[0].message.content.strip()

            # 验证分类是否有效
            有效分类 = [cat['name'] for cat in self.hr分类]
            if 分类结果 in 有效分类:
                return 分类结果

            # 如果AI返回的不在列表中，尝试模糊匹配
            for 分类名 in 有效分类:
                if 分类名 in 分类结果:
                    return 分类名

        except Exception as e:
            print(f"AI分类出错: {e}")

        # 后备方案：使用关键词匹配
        return self._关键词匹配分类(新闻)

    def _关键词匹配分类(self, 新闻: Dict) -> str:
        """使用关键词匹配分类（后备方案）"""
        文本 = 新闻['title'] + " " + 新闻.get('abstract', '')

        匹配得分 = {}
        for 分类 in self.hr分类:
            得分 = 0
            for 关键词 in 分类['keywords']:
                得分 += 文本.count(关键词)
            if 得分 > 0:
                匹配得分[分类['name']] = 得分

        if 匹配得分:
            return max(匹配得分, key=匹配得分.get)

        return "其他"

    def _生成摘要(self, 新闻: Dict) -> str:
        """生成新闻摘要"""
        # 如果已有摘要且较短，直接使用
        原摘要 = 新闻.get('abstract', '')
        if 原摘要 and len(原摘要) < 150:
            return 原摘要

        提示词 = f"""
请为以下汽车行业HR新闻生成一个简洁的摘要（50字以内），重点突出：
1. 涉及哪家公司
2. 发生了什么HR相关的事情
3. 对行业的影响或意义

新闻标题：{新闻['title']}
原始摘要：{原摘要}

请直接输出摘要，不要前缀说明。
"""

        try:
            响应 = self.客户端.chat.completions.create(
                model=self.模型,
                messages=[{"role": "user", "content": 提示词}],
                temperature=0.7,
            )

            return 响应.choices[0].message.content.strip()

        except Exception as e:
            print(f"生成摘要出错: {e}")
            return 原摘要 if 原摘要 else "暂无摘要"

    def _提取关键词(self, 新闻: Dict, 摘要: str) -> List[str]:
        """提取关键词"""
        提示词 = f"""
请从以下新闻中提取3-5个关键词。

标题：{新闻['title']}
摘要：{摘要}

请只输出关键词，用逗号分隔，不要其他解释。
例如：招聘,高薪,人才竞争
"""

        try:
            响应 = self.客户端.chat.completions.create(
                model=self.模型,
                messages=[{"role": "user", "content": 提示词}],
                temperature=0.5,
            )

            关键词文本 = 响应.choices[0].message.content.strip()
            return [k.strip() for k in 关键词文本.split(',')]

        except Exception as e:
            print(f"提取关键词出错: {e}")
            return 新闻.get('keywords', [])

    def 批量分析(self, 新闻列表: List[Dict]) -> List[Dict]:
        """批量分析新闻列表"""
        结果列表 = []

        for i, 新闻 in enumerate(新闻列表, 1):
            print(f"\n进度: {i}/{len(新闻列表)}")

            分析结果 = self.分析新闻(新闻)

            # 合并分析结果到新闻数据中
            新闻.update(分析结果)
            结果列表.append(新闻)

        # 统计
        hr相关数量 = sum(1 for n in 结果列表 if n['is_hr_related'])
        print(f"\n✅ 分析完成！")
        print(f"总计: {len(结果列表)} 条")
        print(f"HR相关: {hr相关数量} 条")
        print(f"不相关: {len(结果列表) - hr相关数量} 条")

        return 结果列表


def 主程序():
    """命令行运行入口"""
    # 加载未分析的新闻数据
    with open('数据/新闻数据.json', 'r', encoding='utf-8') as f:
        新闻列表 = json.load(f)

    # 筛选未分析的
    未分析列表 = [n for n in 新闻列表 if 'is_hr_related' not in n]

    if not 未分析列表:
        print("没有需要分析的新闻")
        return

    print(f"发现 {len(未分析列表)} 条未分析的新闻")

    # 进行分析
    分析器 = AI分析器()
    分析结果 = 分析器.批量分析(未分析列表)

    # 更新原数据
    新闻字典 = {n['id']: n for n in 新闻列表}
    for 新闻 in 分析结果:
        新闻字典[新闻['id']] = 新闻

    # 保存
    所有新闻 = list(新闻字典.values())
    with open('数据/新闻数据.json', 'w', encoding='utf-8') as f:
        json.dump(所有新闻, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 分析结果已保存！")


if __name__ == "__main__":
    主程序()
