import asyncio
import unittest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from app.main import app

# API 前缀
API_PREFIX = "/api"

def get_test_login_header():
    return {"x-wx-openid": "test_wx_openid"}


class TestEndpoint(unittest.TestCase):
    async def run_test(self):
        raise NotImplementedError("子类必须实现此方法")

    async def request(self, method, url, headers=None, **kwargs):
        url = f"{API_PREFIX}{url}"
        if headers is None:
            headers = self.login_header
        return await self.client.request(method, url, headers=headers, **kwargs)

    async def func_test_endpoint(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                transport=ASGITransport(app=manager.app), base_url="http://testserver"
            ) as client:
                self.client = client
                self.login_header = get_test_login_header()
                await self.run_test()

    def test_endpoint(self):
        # 如果是基类，跳过测试
        if self.__class__ == TestEndpoint:
            self.skipTest("")
        asyncio.run(self.func_test_endpoint())
