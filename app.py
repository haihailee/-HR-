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


def 渲染新闻内容():
    """渲染新闻页面（原有功能）"""
    st.markdown('<div class="main-header">🚗 汽车行业HR情报监控系统</div>', unsafe_allow_html=True)

    # 顶部统计（简化版）
    新闻列表 = st.session_state.get('新闻列表', [])

    if 新闻列表:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">总新闻数</div>
                <div class="stat-number">{len(新闻列表)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            公司数 = len(set(n['company'] for n in 新闻列表))
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">监控公司</div>
                <div class="stat-number">{公司数}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            分类数 = len(set(n.get('hr_category', '未分类') for n in 新闻列表))
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">HR分类</div>
                <div class="stat-number">{分类数}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # 筛选功能
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            所有公司 = ['全部'] + sorted(set(n['company'] for n in 新闻列表))
            选中公司 = st.selectbox("按公司筛选", 所有公司)

        with col2:
            所有分类 = ['全部'] + sorted(set(n.get('hr_category', '未分类') for n in 新闻列表))
            选中分类 = st.selectbox("按HR模块筛选", 所有分类)

        with col3:
            时间选项 = st.selectbox("时间范围", ['最近7天', '最近30天', '全部'])

        with col4:
            搜索词 = st.text_input("🔍 关键词搜索", placeholder="搜索标题或摘要")

        # 筛选逻辑
        筛选后新闻 = 新闻列表.copy()

        if 选中公司 != '全部':
            筛选后新闻 = [n for n in 筛选后新闻 if n['company'] == 选中公司]

        if 选中分类 != '全部':
            筛选后新闻 = [n for n in 筛选后新闻 if n.get('hr_category') == 选中分类]

        if 搜索词:
            搜索词_lower = 搜索词.lower()
            筛选后新闻 = [n for n in 筛选后新闻
                         if 搜索词_lower in n['title'].lower()
                         or 搜索词_lower in n.get('summary', '').lower()]

        st.markdown(f"### 📋 新闻列表 ({len(筛选后新闻)} 条)")

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
            页面 = st.radio("导航", ['🏠 新闻首页', '👥 用户管理', '🚪 退出登录'])
        else:
            页面 = st.radio("导航", ['🏠 新闻首页', '🚪 退出登录'])

    # 处理退出登录
    if 页面 == '🚪 退出登录':
        st.session_state['logged_in'] = False
        st.session_state['user_info'] = None
        st.rerun()

    # 显示对应页面
    if 页面 == '👥 用户管理':
        管理员后台()
    else:
        渲染新闻内容()


if __name__ == "__main__":
    主函数()
