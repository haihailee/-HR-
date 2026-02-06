"""
汽车行业HR情报监控系统 - Streamlit主界面
提供现代化的Web界面展示和筛选功能
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import yaml


# 页面配置
st.set_page_config(
    page_title="汽车行业HR情报监控系统",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 理想汽车品牌色
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #002D2B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #002D2B 0%, #057568 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .news-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #002D2B;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        border-left-color: #057568;
    }
    .news-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #002D2B;
        margin-bottom: 0.5rem;
    }
    .news-meta {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .news-summary {
        font-size: 0.95rem;
        color: #555;
        line-height: 1.6;
        margin: 0.5rem 0;
    }
    .tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        margin: 0.2rem;
        border-radius: 15px;
        font-size: 0.8rem;
        background: #f0f0f0;
        color: #666;
    }
    .tag-company {
        background: #E8F5F3;
        color: #057568;
        font-weight: 500;
    }
    .tag-category {
        background: #FAEBD7;
        color: #CEA472;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=600)  # 缓存10分钟
def 加载数据():
    """加载新闻数据"""
    try:
        with open('数据/新闻数据.json', 'r', encoding='utf-8') as f:
            数据 = json.load(f)
        return [n for n in 数据 if n.get('is_hr_related', False)]
    except FileNotFoundError:
        return []


@st.cache_data
def 加载配置():
    """加载配置文件"""
    try:
        with open('配置文件.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}


def 渲染顶部统计():
    """渲染顶部统计卡片"""
    新闻列表 = st.session_state.get('新闻列表', [])

    if not 新闻列表:
        st.warning("暂无数据，请先运行数据抓取脚本")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">总新闻数</div>
            <div class="stat-number">{len(新闻列表)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        最近7天 = sum(1 for n in 新闻列表
                     if (datetime.now() - datetime.fromisoformat(n['crawl_time'])).days <= 7)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">近7天新增</div>
            <div class="stat-number">{最近7天}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        公司数 = len(set(n['company'] for n in 新闻列表))
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">监控公司</div>
            <div class="stat-number">{公司数}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        分类数 = len(set(n.get('hr_category', '未分类') for n in 新闻列表))
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">HR分类</div>
            <div class="stat-number">{分类数}</div>
        </div>
        """, unsafe_allow_html=True)


def 渲染侧边栏():
    """渲染侧边栏筛选器"""
    st.sidebar.markdown("## 🔍 筛选条件")

    新闻列表 = st.session_state.get('新闻列表', [])

    # 按公司筛选
    所有公司 = ['全部'] + sorted(set(n['company'] for n in 新闻列表))
    选中公司 = st.sidebar.selectbox("按公司筛选", 所有公司, key='公司筛选')

    # 按HR模块筛选
    所有分类 = ['全部'] + sorted(set(n.get('hr_category', '未分类') for n in 新闻列表))
    选中分类 = st.sidebar.selectbox("按HR模块筛选", 所有分类, key='分类筛选')

    # 按来源筛选
    所有来源 = ['全部'] + sorted(set(n.get('source', '未知') for n in 新闻列表))
    选中来源 = st.sidebar.selectbox("按新闻来源筛选", 所有来源, key='来源筛选')

    # 时间范围筛选
    st.sidebar.markdown("### 📅 时间范围")
    时间选项 = st.sidebar.radio(
        "选择时间",
        ['最近24小时', '最近7天', '最近30天', '全部'],
        index=1
    )

    # 搜索框
    st.sidebar.markdown("### 🔎 关键词搜索")
    搜索词 = st.sidebar.text_input("输入关键词", placeholder="搜索标题或摘要...")

    return {
        '公司': 选中公司,
        '分类': 选中分类,
        '来源': 选中来源,
        '时间': 时间选项,
        '搜索词': 搜索词
    }


def 筛选新闻(新闻列表, 筛选条件):
    """根据筛选条件过滤新闻"""
    结果 = 新闻列表.copy()

    # 按公司筛选
    if 筛选条件['公司'] != '全部':
        结果 = [n for n in 结果 if n['company'] == 筛选条件['公司']]

    # 按分类筛选
    if 筛选条件['分类'] != '全部':
        结果 = [n for n in 结果 if n.get('hr_category') == 筛选条件['分类']]

    # 按来源筛选
    if 筛选条件['来源'] != '全部':
        结果 = [n for n in 结果 if n.get('source') == 筛选条件['来源']]

    # 按时间筛选
    现在 = datetime.now()
    if 筛选条件['时间'] != '全部':
        时间映射 = {
            '最近24小时': 1,
            '最近7天': 7,
            '最近30天': 30
        }
        天数 = 时间映射[筛选条件['时间']]
        截止时间 = 现在 - timedelta(days=天数)
        结果 = [n for n in 结果
                if datetime.fromisoformat(n['crawl_time']) > 截止时间]

    # 按关键词搜索
    if 筛选条件['搜索词']:
        搜索词 = 筛选条件['搜索词'].lower()
        结果 = [n for n in 结果
                if 搜索词 in n['title'].lower()
                or 搜索词 in n.get('summary', '').lower()]

    return 结果


def 渲染新闻卡片(新闻):
    """渲染单个新闻卡片"""
    # 格式化时间
    try:
        发布时间 = datetime.fromisoformat(新闻['crawl_time'])
        时间文本 = 发布时间.strftime('%Y-%m-%d %H:%M')
    except:
        时间文本 = '未知时间'

    # 构建HTML
    html = f"""
    <div class="news-card">
        <div class="news-title">{新闻['title']}</div>
        <div class="news-meta">
            <span>📰 {新闻.get('source', '未知来源')}</span> |
            <span>🕐 {时间文本}</span>
        </div>
        <div class="news-summary">{新闻.get('summary', '暂无摘要')}</div>
        <div>
            <span class="tag tag-company">🏢 {新闻['company']}</span>
            <span class="tag tag-category">📋 {新闻.get('hr_category', '未分类')}</span>
    """

    # 添加关键词标签
    if 新闻.get('keywords'):
        for 关键词 in 新闻['keywords'][:3]:
            html += f'<span class="tag">🏷️ {关键词}</span>'

    html += f"""
        </div>
        <div style="margin-top: 0.8rem;">
            <a href="{新闻['url']}" target="_blank" style="color: #1890ff; text-decoration: none;">
                📖 阅读原文 →
            </a>
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def 渲染概览页面():
    """渲染首页概览"""
    st.markdown('<div class="main-header">🚗 汽车行业HR情报监控系统</div>', unsafe_allow_html=True)

    # 顶部统计
    渲染顶部统计()

    st.markdown("---")

    # 侧边栏筛选
    筛选条件 = 渲染侧边栏()

    # 获取筛选后的数据
    新闻列表 = st.session_state.get('新闻列表', [])
    筛选后新闻 = 筛选新闻(新闻列表, 筛选条件)

    # 排序选项
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 📋 新闻列表 ({len(筛选后新闻)} 条)")
    with col2:
        排序方式 = st.selectbox("排序", ['最新优先', '按公司', '按分类'], label_visibility="collapsed")

    # 排序
    if 排序方式 == '最新优先':
        筛选后新闻.sort(key=lambda x: x['crawl_time'], reverse=True)
    elif 排序方式 == '按公司':
        筛选后新闻.sort(key=lambda x: (x['company'], x['crawl_time']), reverse=True)
    else:
        筛选后新闻.sort(key=lambda x: (x.get('hr_category', ''), x['crawl_time']), reverse=True)

    # 分页
    每页数量 = 10
    总页数 = (len(筛选后新闻) - 1) // 每页数量 + 1 if 筛选后新闻 else 0

    if 总页数 > 0:
        当前页 = st.number_input("页码", min_value=1, max_value=总页数, value=1, step=1)
        开始索引 = (当前页 - 1) * 每页数量
        结束索引 = 开始索引 + 每页数量

        # 显示新闻
        for 新闻 in 筛选后新闻[开始索引:结束索引]:
            渲染新闻卡片(新闻)
    else:
        st.info("暂无符合条件的新闻")


def 渲染统计分析页面():
    """渲染统计分析页面"""
    st.markdown('<div class="main-header">📊 数据统计分析</div>', unsafe_allow_html=True)

    新闻列表 = st.session_state.get('新闻列表', [])

    if not 新闻列表:
        st.warning("暂无数据")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 各公司新闻数量")
        公司统计 = Counter(n['company'] for n in 新闻列表)
        df_公司 = pd.DataFrame(list(公司统计.items()), columns=['公司', '数量'])
        df_公司 = df_公司.sort_values('数量', ascending=False)
        st.bar_chart(df_公司.set_index('公司'))

    with col2:
        st.markdown("### 📋 HR模块分布")
        分类统计 = Counter(n.get('hr_category', '未分类') for n in 新闻列表)
        df_分类 = pd.DataFrame(list(分类统计.items()), columns=['分类', '数量'])
        df_分类 = df_分类.sort_values('数量', ascending=False)
        st.bar_chart(df_分类.set_index('分类'))

    # 趋势分析
    st.markdown("### 📅 时间趋势")
    日期统计 = Counter()
    for 新闻 in 新闻列表:
        try:
            日期 = datetime.fromisoformat(新闻['crawl_time']).date()
            日期统计[日期] += 1
        except:
            pass

    if 日期统计:
        df_趋势 = pd.DataFrame(list(日期统计.items()), columns=['日期', '数量'])
        df_趋势 = df_趋势.sort_values('日期')
        st.line_chart(df_趋势.set_index('日期'))


def 主函数():
    """主函数"""
    # 加载数据
    if '新闻列表' not in st.session_state:
        st.session_state['新闻列表'] = 加载数据()

    # 侧边栏导航
    页面 = st.sidebar.radio(
        "导航",
        ['🏠 首页概览', '📊 统计分析', '⚙️ 系统设置'],
        label_visibility="collapsed"
    )

    # 刷新按钮
    if st.sidebar.button("🔄 刷新数据"):
        st.cache_data.clear()
        st.session_state['新闻列表'] = 加载数据()
        st.rerun()

    # 显示最后更新时间
    if st.session_state['新闻列表']:
        最新时间 = max(n['crawl_time'] for n in st.session_state['新闻列表'])
        st.sidebar.markdown(f"**最后更新:** {最新时间[:16]}")

    # 路由到不同页面
    if 页面 == '🏠 首页概览':
        渲染概览页面()
    elif 页面 == '📊 统计分析':
        渲染统计分析页面()
    elif 页面 == '⚙️ 系统设置':
        st.markdown('<div class="main-header">⚙️ 系统设置</div>', unsafe_allow_html=True)
        st.info("设置页面开发中...")
        st.markdown("""
        ### 功能规划
        - [ ] 自定义监控公司
        - [ ] 调整HR分类
        - [ ] 配置数据源
        - [ ] 设置定时任务
        - [ ] 飞书通知配置
        """)


if __name__ == "__main__":
    主函数()
