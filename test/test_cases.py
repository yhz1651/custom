import requests
import json

def test_case_1():
    """案例1: 申报重量和价格双重异常 - 原始案例"""
    print("=" * 60)
    print("测试案例1: 申报重量超限且价格异常")
    print("=" * 60)
    
    url = "http://localhost:8000/explain_risk"
    data = {
        "risk_features": {
            "申报重量": 55,
            "限重": 50,
            "申报价格": 100,
            "参考价格": 80
        },
        "rules": [
            ["diff_operator", ["申报重量", "限重"], 0],
            ["ratio_operator", ["申报价格", "参考价格"], 1.2],
            ["and_operator", [], None]
        ]
    }
    
    try:
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"风险指标: {result['summary']['risk_indicator']}")
            print(f"风险等级: {result['summary']['risk_level']}")
            print(f"语义描述: {result['semantic_description']}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n")

def test_case_2():
    """案例2: 三维特征异常检测 - 货物申报异常"""
    print("=" * 60)
    print("测试案例2: 货物申报三维异常检测")
    print("=" * 60)
    
    url = "http://localhost:8000/explain_risk"
    data = {
        "risk_features": {
            "申报数量": 1000,
            "历史平均数量": 500,
            "申报体积": 2.5,
            "标准体积": 1.8,
            "申报频次": 15,
            "正常频次": 8
        },
        "rules": [
            ["ratio_operator", ["申报数量", "历史平均数量"], 1.5],
            ["ratio_operator", ["申报体积", "标准体积"], 1.3],
            ["ratio_operator", ["申报频次", "正常频次"], 1.5],
            ["and3_operator", [], None]
        ]
    }
    
    try:
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"风险指标: {result['summary']['risk_indicator']}")
            print(f"风险等级: {result['summary']['risk_level']}")
            print(f"语义描述: {result['semantic_description']}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n")

def test_case_3():
    """案例3: 温度异常监控 - 冷链运输风险"""
    print("=" * 60)
    print("测试案例3: 冷链运输温度异常监控")
    print("=" * 60)
    
    url = "http://localhost:8000/explain_risk"
    data = {
        "risk_features": {
            "当前温度": -15.5,
            "标准温度": -18.0,
            "温度变化率": 0.8,
            "安全变化率": 0.5,
            "湿度偏差": 12.0,
            "湿度阈值": 10.0
        },
        "rules": [
            ["diff_operator", ["当前温度", "标准温度"], 2.0],
            ["cmp_operator", ["温度变化率", "安全变化率"], None],
            ["cmp_operator", ["湿度偏差", "湿度阈值"], None],
            ["or3_operator", [], None]
        ]
    }
    
    try:
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"风险指标: {result['summary']['risk_indicator']}")
            print(f"风险等级: {result['summary']['risk_level']}")
            print(f"语义描述: {result['semantic_description']}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n")

def run_all_tests():
    """运行所有测试案例"""
    print("开始运行所有风险检测测试案例...")
    print()
    
    test_case_1()
    test_case_2()
    test_case_3()
    
    print("所有测试案例执行完成！")

if __name__ == "__main__":
    run_all_tests()
