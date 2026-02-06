"""
用户认证和管理模块
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import os


class 用户管理:
    def __init__(self, 用户文件路径: str = "数据/用户数据.json", 日志文件路径: str = "数据/访问日志.json"):
        self.用户文件 = 用户文件路径
        self.日志文件 = 日志文件路径
        self._确保文件存在()

    def _确保文件存在(self):
        """确保数据文件存在"""
        os.makedirs(os.path.dirname(self.用户文件), exist_ok=True)

        # 初始化用户文件
        if not os.path.exists(self.用户文件):
            初始用户 = {
                "admin": {
                    "password": self._加密密码("admin123"),
                    "role": "admin",
                    "name": "系统管理员",
                    "created_at": datetime.now().isoformat(),
                    "enabled": True
                }
            }
            with open(self.用户文件, 'w', encoding='utf-8') as f:
                json.dump(初始用户, f, ensure_ascii=False, indent=2)

        # 初始化日志文件
        if not os.path.exists(self.日志文件):
            with open(self.日志文件, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _加密密码(self, 密码: str) -> str:
        """使用SHA256加密密码"""
        return hashlib.sha256(密码.encode('utf-8')).hexdigest()

    def 验证登录(self, 用户名: str, 密码: str) -> Optional[Dict]:
        """验证用户登录"""
        用户数据 = self._加载用户数据()

        if 用户名 not in 用户数据:
            return None

        用户 = 用户数据[用户名]

        # 检查用户是否被禁用
        if not 用户.get('enabled', True):
            return None

        # 验证密码
        if 用户['password'] == self._加密密码(密码):
            # 记录登录日志
            self.记录登录(用户名)
            return {
                'username': 用户名,
                'role': 用户['role'],
                'name': 用户['name']
            }

        return None

    def 创建用户(self, 用户名: str, 密码: str, 姓名: str, 角色: str = "user") -> bool:
        """创建新用户"""
        用户数据 = self._加载用户数据()

        if 用户名 in 用户数据:
            return False

        用户数据[用户名] = {
            "password": self._加密密码(密码),
            "role": 角色,
            "name": 姓名,
            "created_at": datetime.now().isoformat(),
            "enabled": True
        }

        self._保存用户数据(用户数据)
        return True

    def 删除用户(self, 用户名: str) -> bool:
        """删除用户"""
        if 用户名 == "admin":  # 不能删除管理员
            return False

        用户数据 = self._加载用户数据()

        if 用户名 in 用户数据:
            del 用户数据[用户名]
            self._保存用户数据(用户数据)
            return True

        return False

    def 修改密码(self, 用户名: str, 新密码: str) -> bool:
        """修改用户密码"""
        用户数据 = self._加载用户数据()

        if 用户名 in 用户数据:
            用户数据[用户名]['password'] = self._加密密码(新密码)
            self._保存用户数据(用户数据)
            return True

        return False

    def 启用禁用用户(self, 用户名: str, 启用: bool) -> bool:
        """启用或禁用用户"""
        if 用户名 == "admin":  # 不能禁用管理员
            return False

        用户数据 = self._加载用户数据()

        if 用户名 in 用户数据:
            用户数据[用户名]['enabled'] = 启用
            self._保存用户数据(用户数据)
            return True

        return False

    def 获取所有用户(self) -> List[Dict]:
        """获取所有用户列表"""
        用户数据 = self._加载用户数据()

        用户列表 = []
        for 用户名, 信息 in 用户数据.items():
            用户列表.append({
                'username': 用户名,
                'name': 信息['name'],
                'role': 信息['role'],
                'created_at': 信息['created_at'],
                'enabled': 信息.get('enabled', True)
            })

        return 用户列表

    def 记录登录(self, 用户名: str):
        """记录用户登录"""
        日志 = self._加载日志数据()

        日志.append({
            'username': 用户名,
            'action': 'login',
            'timestamp': datetime.now().isoformat()
        })

        # 只保留最近1000条记录
        if len(日志) > 1000:
            日志 = 日志[-1000:]

        self._保存日志数据(日志)

    def 记录访问(self, 用户名: str, 新闻标题: str):
        """记录用户访问新闻"""
        日志 = self._加载日志数据()

        日志.append({
            'username': 用户名,
            'action': 'view_news',
            'news_title': 新闻标题,
            'timestamp': datetime.now().isoformat()
        })

        # 只保留最近1000条记录
        if len(日志) > 1000:
            日志 = 日志[-1000:]

        self._保存日志数据(日志)

    def 获取用户日志(self, 用户名: str = None, 限制数量: int = 50) -> List[Dict]:
        """获取用户访问日志"""
        日志 = self._加载日志数据()

        # 按时间倒序
        日志.reverse()

        # 筛选特定用户
        if 用户名:
            日志 = [log for log in 日志 if log['username'] == 用户名]

        return 日志[:限制数量]

    def 获取用户统计(self) -> Dict:
        """获取用户访问统计"""
        日志 = self._加载日志数据()

        统计 = {}
        for log in 日志:
            用户名 = log['username']
            if 用户名 not in 统计:
                统计[用户名] = {
                    'login_count': 0,
                    'view_count': 0,
                    'last_active': None
                }

            if log['action'] == 'login':
                统计[用户名]['login_count'] += 1
            elif log['action'] == 'view_news':
                统计[用户名]['view_count'] += 1

            统计[用户名]['last_active'] = log['timestamp']

        return 统计

    def _加载用户数据(self) -> Dict:
        """加载用户数据"""
        try:
            with open(self.用户文件, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _保存用户数据(self, 数据: Dict):
        """保存用户数据"""
        with open(self.用户文件, 'w', encoding='utf-8') as f:
            json.dump(数据, f, ensure_ascii=False, indent=2)

    def _加载日志数据(self) -> List:
        """加载日志数据"""
        try:
            with open(self.日志文件, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _保存日志数据(self, 日志: List):
        """保存日志数据"""
        with open(self.日志文件, 'w', encoding='utf-8') as f:
            json.dump(日志, f, ensure_ascii=False, indent=2)
