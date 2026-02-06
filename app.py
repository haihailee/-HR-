"""
汽车行业HR情报监控系统 - 带用户认证的主界面
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import os

# 导入用户认证模块
try:
    from 用户认证 import 用户管理
    用户管理器 = 用户管理()
except:
    用户管理器 = None

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
    .login-box {
        max-width: 400px;
        margin: 100px auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


def 登录页面():
    """显示登录页面"""
    st.markdown('<div class="main-header">🚗 汽车行业HR情报监控系统</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        st.markdown("### 🔐 用户登录")

        with st.form("login_form"):
            用户名 = st.text_input("用户名", placeholder="请输入用户名")
            密码 = st.text_input("密码", type="password", placeholder="请输入密码")
            提交 = st.form_submit_button("登录", use_container_width=True)

            if 提交:
                if not 用户名 or not 密码:
                    st.error("请输入用户名和密码")
                elif not 用户管理器:
                    st.error("用户认证系统未启用")
                else:
                    用户信息 = 用户管理器.验证登录(用户名, 密码)
                    if 用户信息:
                        st.session_state['logged_in'] = True
                        st.session_state['user_info'] = 用户信息
                        st.success(f"欢迎回来，{用户信息['name']}！")
                        st.rerun()
                    else:
                        st.error("用户名或密码错误，或账号已被禁用")

        st.info("💡 默认管理员账号：admin / admin123")


def 管理员后台():
    """管理员后台页面"""
    st.markdown('<div class="main-header">👥 用户管理</div>', unsafe_allow_html=True)

    tabs = st.tabs(["📋 用户列表", "➕ 创建用户", "📊 访问统计"])

    # 用户列表
    with tabs[0]:
        st.markdown("### 所有用户")

        用户列表 = 用户管理器.获取所有用户()

        if 用户列表:
            df = pd.DataFrame(用户列表)
            df['状态'] = df['enabled'].apply(lambda x: '✅ 启用' if x else '❌ 禁用')
            df['角色'] = df['role'].apply(lambda x: '👑 管理员' if x == 'admin' else '👤 用户')

            显示列 = ['username', 'name', '角色', '状态', 'created_at']
            st.dataframe(df[显示列], use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("### 用户操作")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 修改密码")
                with st.form("change_password_form"):
                    用户名 = st.selectbox("选择用户", [u['username'] for u in 用户列表])
                    新密码 = st.text_input("新密码", type="password")
                    if st.form_submit_button("修改密码"):
                        if 用户管理器.修改密码(用户名, 新密码):
                            st.success(f"已修改 {用户名} 的密码")
                        else:
                            st.error("修改失败")

            with col2:
                st.markdown("#### 启用/禁用用户")
                with st.form("toggle_user_form"):
                    用户名 = st.selectbox("选择用户", [u['username'] for u in 用户列表 if u['username'] != 'admin'], key="toggle")
                    操作 = st.radio("操作", ["启用", "禁用"])
                    if st.form_submit_button("执行"):
                        if 用户管理器.启用禁用用户(用户名, 操作 == "启用"):
                            st.success(f"已{操作}用户 {用户名}")
                        else:
                            st.error("操作失败")

    # 创建用户
    with tabs[1]:
        st.markdown("### 创建新用户")

        with st.form("create_user_form"):
            col1, col2 = st.columns(2)

            with col1:
                新用户名 = st.text_input("用户名", placeholder="英文或拼音")
                新姓名 = st.text_input("姓名", placeholder="真实姓名")

            with col2:
                新密码 = st.text_input("密码", type="password", placeholder="至少6位")
                新角色 = st.selectbox("角色", ["user", "admin"])

            if st.form_submit_button("创建用户", use_container_width=True):
                if not 新用户名 or not 新密码 or not 新姓名:
                    st.error("请填写所有字段")
                elif len(新密码) < 6:
                    st.error("密码至少6位")
                elif 用户管理器.创建用户(新用户名, 新密码, 新姓名, 新角色):
                    st.success(f"成功创建用户：{新用户名}")
                else:
                    st.error("用户名已存在")

    # 访问统计
    with tabs[2]:
        st.markdown("### 用户访问统计")

        统计数据 = 用户管理器.获取用户统计()

        if 统计数据:
            统计列表 = []
            for 用户名, 数据 in 统计数据.items():
                统计列表.append({
                    '用户名': 用户名,
                    '登录次数': 数据['login_count'],
                    '浏览次数': 数据['view_count'],
                    '最后活跃': 数据['last_active'][:16] if 数据['last_active'] else '-'
                })

            df = pd.DataFrame(统计列表)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("### 最近访问日志")

            日志 = 用户管理器.获取用户日志(限制数量=20)

            for log in 日志:
                动作 = "🔐 登录" if log['action'] == 'login' else "📰 浏览新闻"
                时间 = log['timestamp'][:16]

                if log['action'] == 'view_news':
                    st.text(f"{时间} | {log['username']} | {动作}: {log.get('news_title', '')}")
                else:
                    st.text(f"{时间} | {log['username']} | {动作}")
        else:
            st.info("暂无访问记录")


@st.cache_data(ttl=600)
def 加载数据():
    """加载新闻数据"""
    try:
        with open('数据/新闻数据.json', 'r', encoding='utf-8') as f:
            数据 = json.load(f)
        return [n for n in 数据 if n.get('is_hr_related', False)]
    except FileNotFoundError:
        return []


def 渲染侧边栏筛选():
    """渲染侧边栏筛选器"""
    新闻列表 = st.session_state.get('新闻列表', [])

    st.sidebar.markdown("## 🔍 筛选条件")

    # 按公司筛选
    所有公司 = ['全部'] + sorted(set(n['company'] for n in 新闻列表))
    选中公司 = st.sidebar.selectbox("按公司筛选", 所有公司)

    # 按HR模块筛选
    所有分类 = ['全部'] + sorted(set(n.get('hr_category', '未分类') for n in 新闻列表))
    选中分类 = st.sidebar.selectbox("按HR模块筛选", 所有分类)

    # 按来源筛选
    所有来源 = ['全部'] + sorted(set(n.get('source', '未知') for n in 新闻列表))
    选中来源 = st.sidebar.selectbox("按新闻来源筛选", 所有来源)

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


def 渲染新闻内容():
    """渲染新闻页面（原有功能）"""
    st.markdown('<div class="main-header">🚗 汽车行业HR情报监控系统</div>', unsafe_allow_html=True)

    # 顶部统计（简化版）
    新闻列表 = st.session_state.get('新闻列表', [])

    if 新闻列表:
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

        st.markdown("---")

        # 获取侧边栏筛选条件
        筛选条件 = 渲染侧边栏筛选()

        # 筛选逻辑
        筛选后新闻 = 新闻列表.copy()

        if 筛选条件['公司'] != '全部':
            筛选后新闻 = [n for n in 筛选后新闻 if n['company'] == 筛选条件['公司']]

        if 筛选条件['分类'] != '全部':
            筛选后新闻 = [n for n in 筛选后新闻 if n.get('hr_category') == 筛选条件['分类']]

        if 筛选条件['来源'] != '全部':
            筛选后新闻 = [n for n in 筛选后新闻 if n.get('source') == 筛选条件['来源']]

        # 时间筛选
        现在 = datetime.now()
        if 筛选条件['时间'] != '全部':
            时间映射 = {
                '最近24小时': 1,
                '最近7天': 7,
                '最近30天': 30
            }
            天数 = 时间映射[筛选条件['时间']]
            截止时间 = 现在 - timedelta(days=天数)
            筛选后新闻 = [n for n in 筛选后新闻
                         if datetime.fromisoformat(n['crawl_time']) > 截止时间]

        if 筛选条件['搜索词']:
            搜索词_lower = 筛选条件['搜索词'].lower()
            筛选后新闻 = [n for n in 筛选后新闻
                         if 搜索词_lower in n['title'].lower()
                         or 搜索词_lower in n.get('summary', '').lower()]

        st.markdown(f"### 📋 新闻列表 ({len(筛选后新闻)} 条)")

        # 提示：这是示例数据
        st.info("💡 当前显示的是示例数据。启用真实爬虫后，将自动从全网50+媒体抓取最新HR新闻。")

        # 显示新闻
        for 新闻 in 筛选后新闻[:20]:
            try:
                发布时间 = datetime.fromisoformat(新闻['crawl_time'])
                时间文本 = 发布时间.strftime('%Y-%m-%d %H:%M')
            except:
                时间文本 = '未知时间'

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
                </div>
                <div style="margin-top: 0.8rem;">
                    <a href="{新闻['url']}" target="_blank" style="color: #057568; text-decoration: none;">
                        📖 阅读原文 →
                    </a>
                </div>
            </div>
            """

            st.markdown(html, unsafe_allow_html=True)

            # 记录浏览
            if 用户管理器 and st.session_state.get('logged_in'):
                用户管理器.记录访问(st.session_state['user_info']['username'], 新闻['title'])
    else:
        st.info("暂无数据")


def 渲染本周大事记():
    """渲染本周大事记总结"""
    try:
        from AI分析.周报生成 import 生成本周大事记
    except:
        st.error("AI分析模块加载失败")
        return

    新闻列表 = st.session_state.get('新闻列表', [])

    if not 新闻列表:
        st.info("暂无数据")
        return

    # 生成大事记（暂时不使用AI客户端，使用规则生成）
    大事记 = 生成本周大事记(新闻列表, ai客户端=None)

    # 显示总览摘要
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #002D2B 0%, #057568 100%);
                padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h2 style="margin: 0; color: white;">📊 本周HR大事记</h2>
        <p style="font-size: 1.2rem; margin: 1rem 0 0 0; opacity: 0.95;">
            {大事记['summary']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # TOP3 重要事件
    if 大事记.get('top_events'):
        st.markdown("### 🔥 本周TOP事件")

        for i, event in enumerate(大事记['top_events'], 1):
            st.markdown(f"""
            <div class="news-card">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="background: #002D2B; color: white; width: 30px; height: 30px;
                                 border-radius: 50%; display: flex; align-items: center;
                                 justify-content: center; font-weight: bold; margin-right: 1rem;">
                        {i}
                    </span>
                    <span class="news-title" style="margin: 0;">{event['title']}</span>
                </div>
                <div class="news-meta">
                    <span class="tag tag-company">🏢 {event['company']}</span>
                    <span class="tag tag-category">📋 {event['category']}</span>
                </div>
                <div class="news-summary">{event['summary']}</div>
            </div>
            """, unsafe_allow_html=True)

    # 按公司汇总
    if 大事记.get('company_updates'):
        st.markdown("### 🏢 各公司动态")

        cols = st.columns(3)
        for i, (公司, 信息) in enumerate(大事记['company_updates'].items()):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background: #f5f5f5; padding: 1rem; border-radius: 8px;
                            border-left: 3px solid #057568;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #002D2B;">{公司}</h4>
                    <p style="color: #666; font-size: 0.9rem; margin: 0;">
                        本周 {信息['count']} 条动态
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # 趋势分析
    if 大事记.get('trends'):
        st.markdown("### 📈 本周趋势")

        for trend in 大事记['trends']:
            st.markdown(f"- {trend}")

    # 一句话洞察
    if 大事记.get('insight'):
        st.markdown(f"""
        <div style="background: #FAEBD7; padding: 1.5rem; border-radius: 10px;
                    border-left: 4px solid #CEA472; margin-top: 2rem;">
            <h4 style="margin: 0 0 0.5rem 0; color: #002D2B;">💡 HR洞察</h4>
            <p style="font-size: 1.1rem; color: #555; margin: 0;">
                {大事记['insight']}
            </p>
        </div>
        """, unsafe_allow_html=True)


def 渲染行业报告专区():
    """渲染行业报告专区"""
    st.markdown('<div class="main-header">📚 行业报告专区</div>', unsafe_allow_html=True)

    新闻列表 = st.session_state.get('新闻列表', [])

    # 筛选出行业报告
    报告列表 = [n for n in 新闻列表 if n.get('hr_category') == '行业报告']

    if not 报告列表:
        st.info("暂无行业报告数据。启用真实爬虫后，将自动收集各类HR行业报告。")
        st.markdown("""
        ### 📊 即将收录的报告类型

        #### 薪酬福利类
        - 年度薪酬白皮书
        - 行业薪酬调研报告
        - 股权激励趋势报告

        #### 人才市场类
        - 人才供需报告
        - 招聘趋势分析
        - 人才流动报告

        #### 组织管理类
        - 组织效能报告
        - 领导力发展报告
        - 企业文化调研

        #### 培训发展类
        - 学习发展趋势
        - 人才培养白皮书
        - 技能需求报告
        """)
        return

    # 统计信息
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">报告总数</div>
            <div class="stat-number">{len(报告列表)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        来源数 = len(set(n.get('source', '') for n in 报告列表))
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">报告来源</div>
            <div class="stat-number">{来源数}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        本月报告 = sum(1 for n in 报告列表
                      if (datetime.now() - datetime.fromisoformat(n['crawl_time'])).days <= 30)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">本月新增</div>
            <div class="stat-number">{本月报告}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 侧边栏筛选
    st.sidebar.markdown("## 📚 报告筛选")

    所有来源 = ['全部'] + sorted(set(n.get('source', '未知') for n in 报告列表))
    选中来源 = st.sidebar.selectbox("按发布机构", 所有来源)

    时间选项 = st.sidebar.radio("发布时间", ['本月', '近3个月', '近半年', '全部'], index=1)

    搜索词 = st.sidebar.text_input("🔍 搜索报告", placeholder="输入关键词...")

    # 筛选逻辑
    筛选后报告 = 报告列表.copy()

    if 选中来源 != '全部':
        筛选后报告 = [n for n in 筛选后报告 if n.get('source') == 选中来源]

    # 时间筛选
    现在 = datetime.now()
    if 时间选项 != '全部':
        时间映射 = {'本月': 30, '近3个月': 90, '近半年': 180}
        天数 = 时间映射[时间选项]
        截止时间 = 现在 - timedelta(days=天数)
        筛选后报告 = [n for n in 筛选后报告
                     if datetime.fromisoformat(n['crawl_time']) > 截止时间]

    if 搜索词:
        搜索词_lower = 搜索词.lower()
        筛选后报告 = [n for n in 筛选后报告
                     if 搜索词_lower in n['title'].lower()
                     or 搜索词_lower in n.get('summary', '').lower()]

    st.markdown(f"### 📋 报告列表 ({len(筛选后报告)} 份)")

    # 按时间排序
    筛选后报告.sort(key=lambda x: x['crawl_time'], reverse=True)

    # 显示报告
    for 报告 in 筛选后报告:
        try:
            发布时间 = datetime.fromisoformat(报告['crawl_time'])
            时间文本 = 发布时间.strftime('%Y-%m-%d')
        except:
            时间文本 = '未知时间'

        # 提取关键词标签
        关键词标签 = ""
        if 报告.get('keywords'):
            for 关键词 in 报告['keywords'][:4]:
                关键词标签 += f'<span class="tag">🏷️ {关键词}</span>'

        html = f"""
        <div class="news-card" style="border-left-color: #CEA472;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div class="news-title">📊 {报告['title']}</div>
                    <div class="news-meta">
                        <span>🏛️ {报告.get('source', '未知机构')}</span> |
                        <span>📅 {时间文本}</span>
                    </div>
                </div>
            </div>
            <div class="news-summary" style="margin-top: 1rem;">
                {报告.get('summary', '暂无摘要')}
            </div>
            <div style="margin-top: 0.8rem;">
                {关键词标签}
            </div>
            <div style="margin-top: 1rem;">
                <a href="{报告['url']}" target="_blank"
                   style="color: #057568; text-decoration: none; font-weight: 500;">
                    📄 查看完整报告 →
                </a>
            </div>
        </div>
        """

        st.markdown(html, unsafe_allow_html=True)

        # 记录浏览
        if 用户管理器 and st.session_state.get('logged_in'):
            用户管理器.记录访问(st.session_state['user_info']['username'], 报告['title'])


def 主函数():
    """主函数"""
    # 初始化session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if '新闻列表' not in st.session_state:
        st.session_state['新闻列表'] = 加载数据()

    # 如果未登录，显示登录页面
    if not st.session_state['logged_in']:
        登录页面()
        return

    # 已登录，显示主界面
    用户信息 = st.session_state.get('user_info', {})

    # 侧边栏
    with st.sidebar:
        st.markdown(f"### 👤 {用户信息.get('name', '用户')}")
        st.markdown(f"**角色**: {用户信息.get('role', 'user')}")

        st.markdown("---")

        # 导航菜单
        if 用户信息.get('role') == 'admin':
            页面 = st.radio("导航", ['🏠 新闻首页', '📊 本周大事记', '📚 行业报告', '👥 用户管理', '🚪 退出登录'])
        else:
            页面 = st.radio("导航", ['🏠 新闻首页', '📊 本周大事记', '📚 行业报告', '🚪 退出登录'])

    # 处理退出登录
    if 页面 == '🚪 退出登录':
        st.session_state['logged_in'] = False
        st.session_state['user_info'] = None
        st.rerun()

    # 显示对应页面
    if 页面 == '👥 用户管理':
        管理员后台()
    elif 页面 == '📊 本周大事记':
        渲染本周大事记()
    elif 页面 == '📚 行业报告':
        渲染行业报告专区()
    else:
        渲染新闻内容()


if __name__ == "__main__":
    主函数()
