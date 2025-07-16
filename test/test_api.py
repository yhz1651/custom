import requests
import json

def test_multi_dimensional_feature_extraction():
    """测试多维特征提取接口"""
    
    # 测试数据
    test_data = {
        "risk_features": {
            "申报重量": 55,
            "限重": 50,
            "申报价格": 100,
            "参考价格": 80,
            "运输许可证状态": "过期",
            "申报名称": "化学试剂",
            "实际货物": "危险化学品"
        },
        "rules": [
            ("diff_operator", ["申报重量", "限重"], 0),  # 申报重量 - 限重 > 0？
            ("ratio_operator", ["申报价格", "参考价格"], 1.2),  # 申报价格/参考价格 > 1.2？
            ("and_operator", [], None)  # 所有条件满足则风险指标为1
        ]
    }
    
    # 发送请求
    url = "http://localhost:8000/explain_risk"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(test_data), headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("=== 多维特征提取结果 ===")
            print(f"风险指标: {result['summary']['risk_indicator']}")
            print(f"风险等级: {result['summary']['risk_level']}")
            print(f"特征数量: {result['summary']['features_count']}")
            print(f"计算步骤: {result['summary']['calculation_steps']}")
            
            print("\n=== 多维计算结构 ===")
            structure = result['multi_dimensional_structure']
            print(f"原始特征: {structure['original_features']}")
            
            print("\n计算步骤详情:")
            for step in structure['calculation_steps']:
                print(f"  步骤 {step['step']}: {step['description']}")
            
            print(f"\n中间结果: {structure['intermediate_results']}")
            print(f"最终风险指标: {structure['final_risk_indicator']}")
            
            print("\n=== 语义描述 ===")
            print(result['semantic_description'])
            
        else:
            print(f"请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("连接失败，请确保服务正在运行在 localhost:8000")
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

def test_health_check():
    """测试健康检查接口"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            result = response.json()
            print(f"健康检查: {result['status']} - {result['message']}")
        else:
            print(f"健康检查失败: {response.status_code}")
    except:
        print("健康检查连接失败")

if __name__ == "__main__":
    print("开始测试多维特征提取接口...")
    test_health_check()
    print("\n" + "="*50)
    test_multi_dimensional_feature_extraction()
