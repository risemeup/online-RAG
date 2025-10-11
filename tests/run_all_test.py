#!/usr/bin/env python3
"""
运行所有测试用例的入口文件
使用方法: python tests/run_all_test.py
"""
import os
import sys
import unittest

# 将项目根目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))


def run_all_tests():
    """运行tests目录下所有的测试用例"""
    test_suite = unittest.TestSuite()
    test_loader = unittest.TestLoader()
    
    # 发现所有以test_开头的Python文件
    test_suite.addTest(
        test_loader.discover(
            os.path.dirname(os.path.realpath(__file__)),
            pattern="test_*.py",
        )
    )

    # 运行测试
    print("=" * 70)
    print("开始运行所有测试用例...")
    print("=" * 70)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 输出测试结果统计
    print("\n" + "=" * 70)
    print("测试结果统计:")
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print("=" * 70)
    
    if result.wasSuccessful():
        print("🎉 所有测试都通过了!")
        sys.exit(0)
    else:
        print("❌ 有测试失败，请检查上面的错误信息")
        sys.exit(1)


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n运行测试时发生错误: {e}")
        sys.exit(1)
