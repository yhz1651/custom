import requests
from flask import Flask, request, jsonify, Response
import json
from riskIndicatorDescription import *
app = Flask(__name__)
# 全局配置：JSON序列化时保留中文
app.config['JSON_AS_ASCII'] = False

def json_response(data, status_code=200):
    """自定义JSON响应，确保中文不转义"""
    json_str = json.dumps(data, ensure_ascii=False, indent=2)  # 关键：ensure_ascii=False
    return Response(
        json_str,
        status=status_code,
        mimetype='application/json; charset=utf-8'  # 明确指定UTF-8编码
    )

@app.route('/explain_risk', methods=['POST'])
def explain_risk():
    """多维特征提取接口：输入单维指标，输出多维计算结构+大模型语义描述"""
    # 从请求中获取参数
    data = request.json
    risk_features = data.get('risk_features', {})
    rules = data.get('rules', [])

    # 验证输入
    if not risk_features or not rules:
        return json_response({"error": "缺少必要参数"}, 400)

    try:
        # 生成多维计算结构
        multi_dimensional_structure = generate_risk_indicator(risk_features, rules)
        print(f"多维计算结构: {multi_dimensional_structure}")

        # 获取大模型详细语义描述
        url = "http://100.100.20.144:9997/v1/chat/completions"
        model = "qwen3"
        semantic_description = get_llm_explanation(risk_features, rules, multi_dimensional_structure, url, model)
        print(f"语义描述: {semantic_description}")

        # 构建完整响应
        response_data = {
            "multi_dimensional_structure": multi_dimensional_structure,
            "semantic_description": semantic_description,
            "summary": {
                "risk_indicator": multi_dimensional_structure["final_risk_indicator"],
                "risk_level": "高风险" if multi_dimensional_structure["final_risk_indicator"] == 1 else "低风险",
                "features_count": len(risk_features),
                "calculation_steps": len(multi_dimensional_structure["calculation_steps"])
            }
        }

        return json_response(response_data)
        
    except Exception as e:
        print(f"处理错误: {str(e)}")
        return json_response({"error": str(e)}, 500)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return json_response({"status": "healthy", "message": "多维特征提取服务运行正常"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
