import unittest
import requests
import json
import os
import uuid
from typing import Dict, Any, Optional

class TestDocumentAPIEndpoints(unittest.TestCase):
    """使用unittest框架测试文档API接口"""
    
    @classmethod
    def setUpClass(cls):
        """在所有测试方法执行前运行一次，设置基础环境"""
        # 基础URL
        cls.BASE_URL = "http://localhost:8000/api/documents"
        
        # 生成唯一的会话ID用于测试
        cls.session_id = str(uuid.uuid4())
        cls.headers = {"X-Session-ID": cls.session_id}
        
        # 测试文件路径
        cls.test_file_path = "data/蓝牙音响客服.txt"
        
        print(f"使用会话ID进行测试: {cls.session_id}")
    
    def setUp(self):
        """在每个测试方法执行前运行，重置文档ID"""
        # 存储当前测试中使用的文档ID
        self.current_doc_id = None
    
    def _prepare_test_file(self):
        """准备测试文件，如果不存在则创建临时文件"""
        if not os.path.exists(self.test_file_path):
            # 如果文件不存在，创建一个临时文件
            temp_path = "temp_test_file.txt"
            with open(temp_path, "w") as f:
                f.write("这是一个测试文档内容，用于测试文档上传功能。")
            return temp_path, True
        return self.test_file_path, False
    
    def test_upload_document(self):
        """测试上传文档接口"""
        print("\n=== 测试上传文档 ===")
        
        file_path, is_temp = self._prepare_test_file()
        
        try:
            # 构建文件上传请求
            with open(file_path, "rb") as file_obj:
                files = {"file": (os.path.basename(file_path), file_obj)}
                response = requests.post(
                    f"{self.BASE_URL}/upload", 
                    headers=self.headers, 
                    files=files
                )
            
            # 打印响应结果
            print(f"上传响应状态码: {response.status_code}")
            print(f"上传响应内容: {response.text}")
            
            # 断言请求成功
            self.assertEqual(response.status_code, 200)
            
            # 解析响应并存储文档ID
            result = response.json()
            
            # 从响应中获取文档ID（使用document_id而不是doc_id）
            doc_id = result.get("document_id")
            if not doc_id:
                # 尝试从metadata中获取doc_id
                metadata = result.get("metadata", {})
                doc_id = metadata.get("doc_id")
            
            self.assertIsNotNone(doc_id, "未能从上传结果中获取文档ID")
            self.current_doc_id = doc_id
            
            print(f"成功上传文档，文档ID: {doc_id}")
        except Exception as e:
            self.fail(f"上传文档测试失败: {str(e)}")
        finally:
            # 清理临时文件
            if is_temp and os.path.exists(file_path):
                os.remove(file_path)
    
    def test_list_documents(self):
        """测试列出文档接口"""
        print("\n=== 测试列出文档 ===")
        
        try:
            response = requests.get(f"{self.BASE_URL}/list", headers=self.headers)
            
            print(f"列出响应状态码: {response.status_code}")
            print(f"列出响应内容: {response.text}")
            
            # 断言请求成功
            self.assertEqual(response.status_code, 200)
            
            # 解析响应
            result = response.json()
            
            # 断言返回的是字典类型
            self.assertIsInstance(result, dict)
            
            print(f"共列出 {len(result)} 个文档")
        except Exception as e:
            self.fail(f"列出文档测试失败: {str(e)}")
    
    def test_get_document_info(self):
        """测试获取文档信息接口"""
        # 首先需要上传一个文档获取文档ID
        if not self.current_doc_id:
            self.test_upload_document()
            
        doc_id = self.current_doc_id
        print(f"\n=== 测试获取文档信息 (ID: {doc_id}) ===")
        
        try:
            response = requests.get(f"{self.BASE_URL}/{doc_id}", headers=self.headers)
            
            print(f"获取信息响应状态码: {response.status_code}")
            print(f"获取信息响应内容: {response.text}")
            
            # 断言请求成功
            self.assertEqual(response.status_code, 200)
            
            # 解析响应
            result = response.json()
            
            # 断言返回的文档信息包含正确的ID和文件名
            self.assertEqual(result.get("doc_id"), doc_id)
            self.assertIn("filename", result)
            
            print(f"成功获取文档信息，文档名称: {result.get('filename')}")
        except Exception as e:
            self.fail(f"获取文档信息测试失败: {str(e)}")
    
    def test_delete_document(self):
        """测试删除文档接口"""
        # 首先需要上传一个文档获取文档ID
        if not self.current_doc_id:
            self.test_upload_document()
            
        doc_id = self.current_doc_id
        print(f"\n=== 测试删除文档 (ID: {doc_id}) ===")
        
        try:
            response = requests.delete(f"{self.BASE_URL}/{doc_id}", headers=self.headers)
            
            print(f"删除响应状态码: {response.status_code}")
            print(f"删除响应内容: {response.text}")
            
            # 断言请求成功
            self.assertEqual(response.status_code, 200)
            
            # 解析响应
            result = response.json()
            
            # 断言删除成功
            self.assertTrue(result.get("success"), "删除文档失败")
            
            print(f"成功删除文档: {doc_id}")
            
            # 验证文档已被删除
            self._verify_document_deleted(doc_id)
        except Exception as e:
            self.fail(f"删除文档测试失败: {str(e)}")
    
    def test_get_nonexistent_document(self):
        """测试获取不存在的文档信息"""
        nonexistent_doc_id = "nonexistent-document-id-12345"
        print(f"\n=== 测试获取不存在的文档信息 (ID: {nonexistent_doc_id}) ===")
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/{nonexistent_doc_id}", 
                headers=self.headers
            )
            
            print(f"获取信息响应状态码: {response.status_code}")
            print(f"获取信息响应内容: {response.text}")
            
            # 断言返回404状态码
            self.assertEqual(response.status_code, 404)
            
            # 解析响应
            result = response.json()
            
            # 断言返回错误信息
            self.assertIn("detail", result)
            self.assertEqual(result["detail"], "文档不存在")
            
            print(f"文档ID {nonexistent_doc_id} 不存在，符合预期")
        except Exception as e:
            self.fail(f"测试获取不存在的文档信息失败: {str(e)}")
    
    def test_delete_nonexistent_document(self):
        """测试删除不存在的文档"""
        nonexistent_doc_id = "nonexistent-document-id-67890"
        print(f"\n=== 测试删除不存在的文档 (ID: {nonexistent_doc_id}) ===")
        
        try:
            response = requests.delete(
                f"{self.BASE_URL}/{nonexistent_doc_id}", 
                headers=self.headers
            )
            
            print(f"删除响应状态码: {response.status_code}")
            print(f"删除响应内容: {response.text}")
            
            # 断言返回404状态码
            self.assertEqual(response.status_code, 404)
            
            # 解析响应
            result = response.json()
            
            # 断言返回错误信息
            self.assertIn("detail", result)
            self.assertEqual(result["detail"], "文档不存在")
            
            print(f"文档ID {nonexistent_doc_id} 不存在，删除失败，符合预期")
        except Exception as e:
            self.fail(f"测试删除不存在的文档失败: {str(e)}")
    
    def _verify_document_deleted(self, doc_id: str):
        """验证文档已被删除"""
        print(f"\n=== 验证文档已被删除 (ID: {doc_id}) ===")
        
        response = requests.get(f"{self.BASE_URL}/{doc_id}", headers=self.headers)
        
        print(f"验证删除响应状态码: {response.status_code}")
        print(f"验证删除响应内容: {response.text}")
        
        # 断言返回404状态码
        self.assertEqual(response.status_code, 404)
        
        # 解析响应
        result = response.json()
        
        # 断言返回错误信息
        self.assertIn("detail", result)
        self.assertEqual(result["detail"], "文档不存在")
        
        print(f"验证删除成功: 文档 {doc_id} 已不存在")
    
    def tearDown(self):
        """在每个测试方法执行后运行，清理资源"""
        # 如果有文档ID，尝试删除该文档
        if self.current_doc_id:
            try:
                requests.delete(f"{self.BASE_URL}/{self.current_doc_id}", headers=self.headers)
            except:
                pass  # 忽略删除失败的情况


if __name__ == "__main__":
    print("开始使用unittest框架测试文档API接口...")
    unittest.main()