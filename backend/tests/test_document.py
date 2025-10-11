import unittest
import json
import os
import uuid
from typing import Dict, Any, Optional
from base_endpoint import TestEndpoint

class TestDocumentAPIEndpoints(TestEndpoint):
    """使用TestEndpoint框架测试文档API接口"""
    
    def setUp(self):
        """在每个测试方法执行前运行，重置文档ID"""
        # 存储当前测试中使用的文档ID
        self.current_doc_id = None
        # 测试文件路径
        self.test_file_path = "data/蓝牙音响客服.txt"
    
    async def run_test(self):
        """实现 TestEndpoint 的抽象方法，运行所有测试"""
        self.setUp()  # setUp 不是异步方法，不需要 await
        try:
            await self._test_upload_document()
            await self._test_list_documents()
            await self._test_get_document_info()
            await self._test_delete_document()
            await self._test_get_nonexistent_document()
            await self._test_delete_nonexistent_document()
        finally:
            await self.async_tearDown()
    
    def _prepare_test_file(self):
        """准备测试文件，如果不存在则创建临时文件"""
        if not os.path.exists(self.test_file_path):
            # 如果文件不存在，创建一个临时文件
            temp_path = "temp_test_file.txt"
            with open(temp_path, "w") as f:
                f.write("这是一个测试文档内容，用于测试文档上传功能。")
            return temp_path, True
        return self.test_file_path, False
    
    async def _test_upload_document(self):
        """测试上传文档接口"""
        print("\n=== 测试上传文档 ===")
        
        file_path, is_temp = self._prepare_test_file()
        
        try:
            # 构建文件上传请求
            with open(file_path, "rb") as file_obj:
                files = {"file": (os.path.basename(file_path), file_obj)}
                response = await self.request(
                    "POST", 
                    "/documents/upload", 
                    files=files
                )
            
            # 打印响应结果
            print(f"上传响应状态码: {response.status_code}")
            print(f"上传响应内容: {response.text}")
            
            # 断言请求成功
            self.assertEqual(response.status_code, 200)
            
            # 解析响应并存储文档ID
            result = response.json()
            
            # 从响应中获取文档ID（从data字段中获取id）
            data = result.get("data", {})
            doc_id = data.get("id")
            if not doc_id:
                # 尝试其他可能的字段名
                doc_id = result.get("document_id") or data.get("doc_id")
            
            self.assertIsNotNone(doc_id, "未能从上传结果中获取文档ID")
            self.current_doc_id = doc_id
            
            print(f"成功上传文档，文档ID: {doc_id}")
        except Exception as e:
            self.fail(f"上传文档测试失败: {str(e)}")
        finally:
            # 清理临时文件
            if is_temp and os.path.exists(file_path):
                os.remove(file_path)
    
    async def _test_list_documents(self):
        """测试获取文档列表接口"""
        print("\n=== 测试获取文档列表 ===")
        
        # 发送请求
        response = await self.request("GET", "/documents/list")
        
        # 断言状态码
        self.assertEqual(response.status_code, 200)
        
        # 解析响应
        result = response.json()
        
        # 断言返回结构
        self.assertIn("code", result)
        self.assertIn("data", result)
        self.assertEqual(result["code"], 0)  # 成功时 code 为 0
        
        # 断言数据结构
        documents = result["data"]
        self.assertIsInstance(documents, list)
        
        # 如果有文档，验证文档结构
        if documents:
            doc = documents[0]
            self.assertIn("id", doc)
            self.assertIn("filename", doc)
        
        print(f"获取到 {len(documents)} 个文档")
    
    async def _test_get_document_info(self):
        """测试获取文档信息接口"""
        # 首先需要上传一个文档获取文档ID
        if not self.current_doc_id:
            await self._test_upload_document()
            
        doc_id = self.current_doc_id
        print(f"\n=== 测试获取文档信息 (ID: {doc_id}) ===")
        
        try:
            response = await self.request("GET", f"/documents/{doc_id}")
            
            print(f"获取信息响应状态码: {response.status_code}")
            print(f"获取信息响应内容: {response.text}")
            
            # 断言请求成功
            self.assertEqual(response.status_code, 200)
            
            # 解析响应
            result = response.json()
            data = result.get("data", {})
            
            # 断言返回的文档信息包含正确的ID和文件名
            self.assertEqual(data.get("id"), doc_id)
            self.assertIn("filename", data)
            
            print(f"成功获取文档信息，文档名称: {data.get('filename')}")
        except Exception as e:
            self.fail(f"获取文档信息测试失败: {str(e)}")
    
    async def _test_delete_document(self):
        """测试删除文档接口"""
        # 首先需要上传一个文档获取文档ID
        if not self.current_doc_id:
            await self._test_upload_document()
            
        doc_id = self.current_doc_id
        print(f"\n=== 测试删除文档 (ID: {doc_id}) ===")
        
        try:
            response = await self.request("DELETE", f"/documents/{doc_id}")
            
            print(f"删除响应状态码: {response.status_code}")
            print(f"删除响应内容: {response.text}")
            
            # 断言请求成功
            self.assertEqual(response.status_code, 200)
            
            # 解析响应
            result = response.json()
            
            print(f"删除响应结果: {result}")
            
            # 如果删除失败，打印错误信息
            if result.get("code") != 0:
                print(f"删除失败，错误码: {result.get('code')}, 错误信息: {result.get('msg')}")
            
            # 断言响应结构
            self.assertEqual(result.get("code"), 0)  # 成功时 code 为 0
            
            data = result.get("data")
            if data:
                # 断言删除成功
                self.assertTrue(data.get("success"), "删除文档失败")
            else:
                # 如果没有 data 字段，检查 code 是否为成功
                self.assertEqual(result.get("code"), 0, "删除文档失败")
            
            print(f"成功删除文档: {doc_id}")
            
            # 验证文档已被删除
            await self._verify_document_deleted(doc_id)
        except Exception as e:
            self.fail(f"删除文档测试失败: {str(e)}")
    
    async def _test_get_nonexistent_document(self):
        """测试获取不存在的文档信息"""
        nonexistent_doc_id = "nonexistent-document-id-12345"
        print(f"\n=== 测试获取不存在的文档信息 (ID: {nonexistent_doc_id}) ===")
        
        try:
            response = await self.request("GET", f"/documents/{nonexistent_doc_id}")
            
            print(f"获取信息响应状态码: {response.status_code}")
            print(f"获取信息响应内容: {response.text}")
            
            # 断言返回404状态码
            self.assertEqual(response.status_code, 404)
            
            # 解析响应
            result = response.json()
            
            # 断言返回错误信息（适应我们的API格式）
            self.assertIn("msg", result)
            self.assertIn("文档不存在", result["msg"])
            
            print(f"文档ID {nonexistent_doc_id} 不存在，符合预期")
        except Exception as e:
            self.fail(f"测试获取不存在的文档信息失败: {str(e)}")
    
    async def _test_delete_nonexistent_document(self):
        """测试删除不存在的文档"""
        nonexistent_doc_id = "nonexistent-document-id-67890"
        print(f"\n=== 测试删除不存在的文档 (ID: {nonexistent_doc_id}) ===")
        
        try:
            response = await self.request("DELETE", f"/documents/{nonexistent_doc_id}")
            
            print(f"删除响应状态码: {response.status_code}")
            print(f"删除响应内容: {response.text}")
            
            # 断言返回404状态码
            self.assertEqual(response.status_code, 404)
            
            # 解析响应
            result = response.json()
            
            # 断言返回错误信息（适应我们的API格式）
            self.assertIn("msg", result)
            self.assertIn("文档不存在", result["msg"])
            
            print(f"文档ID {nonexistent_doc_id} 不存在，删除失败，符合预期")
        except Exception as e:
            self.fail(f"测试删除不存在的文档失败: {str(e)}")
    
    async def _verify_document_deleted(self, doc_id: str):
        """验证文档已被删除"""
        print(f"\n=== 验证文档已被删除 (ID: {doc_id}) ===")
        
        response = await self.request("GET", f"/documents/{doc_id}")
        
        print(f"验证删除响应状态码: {response.status_code}")
        print(f"验证删除响应内容: {response.text}")
        
        # 断言返回404状态码
        self.assertEqual(response.status_code, 404)
        
        # 解析响应
        result = response.json()
        
        # 断言返回错误信息
        self.assertIn("msg", result)
        self.assertIn("文档不存在", result["msg"])
        
        print(f"验证删除成功: 文档 {doc_id} 已不存在")
    
    async def async_tearDown(self):
        """在每个测试方法执行后运行，清理资源"""
        # 如果有文档ID，尝试删除该文档
        if self.current_doc_id:
            try:
                await self.request("DELETE", f"/documents/{self.current_doc_id}")
            except:
                pass  # 忽略删除失败的情况


if __name__ == "__main__":
    print("开始使用unittest框架测试文档API接口...")
    unittest.main()