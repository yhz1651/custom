import requests
from flask import Flask, request, jsonify, Response
from RiskIndicatorDescription import *
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
    """获取风险指标解释接口"""
    # 从请求中获取参数
    data = request.json
    risk_features = data.get('risk_features', {})
    rules = data.get('rules', [])

    # 验证输入
    if not risk_features or not rules:
        return jsonify({"error": "缺少必要参数"}), 400

    try:
        # 计算风险指标
        risk_indicator = generate_risk_indicator(risk_features, rules)
        print(f"风险指标: {risk_indicator}")

        # 获取大模型解释
        url = "http://100.100.20.144:9997/v1/chat/completions"
        model = "qwen3"
        explain = get_llm_explanation(risk_features, rules, risk_indicator, url, model)
        print(f"大模型解释: {explain}")

        # return jsonify({
        #     "risk_indicator": risk_indicator,
        #     "explain": explain
        # })
        # 使用自定义响应函数
        return json_response({
            "risk_indicator": risk_indicator,
            "explain": explain
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)