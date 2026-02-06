"""
快速启动脚本
一键完成数据抓取、AI分析和启动Web界面
"""

import subprocess
import sys
import os


def 检查依赖():
    """检查是否安装了必要的依赖包"""
    print("🔍 检查依赖包...")
    try:
        import streamlit
        import requests
        import yaml
        print("✅ 依赖包检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e.name}")
        print("请运行: pip install -r requirements.txt")
        return False


def 检查配置():
    """检查配置文件是否存在"""
    print("\n🔍 检查配置文件...")
    if not os.path.exists('配置文件.yaml'):
        print("❌ 配置文件不存在")
        return False

    import yaml
    with open('配置文件.yaml', 'r', encoding='utf-8') as f:
        配置 = yaml.safe_load(f)

    api_key = 配置.get('ai_service', {}).get('zhipu', {}).get('api_key', '')
    if 'your_' in api_key or not api_key:
        print("❌ 请在配置文件.yaml中填入智谱AI的API Key")
        print("获取地址: https://open.bigmodel.cn/")
        return False

    print("✅ 配置文件检查通过")
    return True


def 运行爬虫():
    """运行新闻爬虫"""
    print("\n📰 开始抓取新闻...")
    try:
        result = subprocess.run(
            [sys.executable, '数据抓取/新闻爬虫.py'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ 爬虫运行出错: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ 运行爬虫失败: {e}")
        return False


def 运行ai分析():
    """运行AI分析"""
    print("\n🤖 开始AI分析...")
    try:
        result = subprocess.run(
            [sys.executable, 'AI分析/内容分类.py'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ AI分析出错: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ 运行AI分析失败: {e}")
        return False


def 启动web界面():
    """启动Streamlit Web界面"""
    print("\n🌐 启动Web界面...")
    print("提示: 按 Ctrl+C 可以停止服务")
    try:
        subprocess.run([
            sys.executable,
            '-m', 'streamlit',
            'run',
            '主应用.py',
            '--server.headless=true'
        ])
    except KeyboardInterrupt:
        print("\n\n👋 已停止服务")


def 主菜单():
    """显示主菜单"""
    print("\n" + "="*50)
    print("🚗 汽车行业HR情报监控系统")
    print("="*50)
    print("\n请选择操作:")
    print("1. 完整运行（抓取 → 分析 → 启动界面）")
    print("2. 仅抓取新闻")
    print("3. 仅AI分析")
    print("4. 仅启动Web界面")
    print("5. 退出")
    print()

    选择 = input("请输入选项 (1-5): ").strip()
    return 选择


def 主程序():
    """主程序入口"""
    # 基础检查
    if not 检查依赖():
        return

    if not 检查配置():
        return

    while True:
        选择 = 主菜单()

        if 选择 == '1':
            # 完整运行
            if 运行爬虫():
                if 运行ai分析():
                    启动web界面()
                    break

        elif 选择 == '2':
            # 仅抓取
            运行爬虫()

        elif 选择 == '3':
            # 仅分析
            运行ai分析()

        elif 选择 == '4':
            # 仅启动界面
            启动web界面()
            break

        elif 选择 == '5':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效选项，请重新选择")


if __name__ == "__main__":
    try:
        主程序()
    except KeyboardInterrupt:
        print("\n\n👋 已退出")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()
