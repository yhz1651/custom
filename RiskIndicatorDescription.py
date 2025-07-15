# 假设之前的算子代码已经保存为 operators.py
from operators import *
from api import *

def generate_risk_indicator(risk_features, rules):
    """
    根据风险特征和规则生成风险指标
    :param risk_features: 风险特征字典，键为特征名称，值为特征值
    :param rules: 风险规则列表，每个规则是一个元组，格式为 (算子名称, 特征名称列表, 阈值)
    :return: 风险指标，0或1
    """
    intermediate_results = []
    # 第一步：计算属性算子结果
    for rule in rules[:-1]:  # 排除最后一个规则（逻辑算子规则）
        operator_name, feature_names, threshold = rule
        operator = globals().get(operator_name)
        if operator is None:
            raise ValueError(f"未找到算子 {operator_name}")
        features = [risk_features[feature_name] for feature_name in feature_names]
        if operator_name in ['subset_operator']:
            result = operator(*features)
        elif operator_name in ['weighted_avg_operator']:
            # 假设第一个特征是权重列表，其余是值列表
            weights = features[0]
            values = features[1:]
            result = operator(weights, values, threshold)
        elif operator_name in ['euclidean_distance_2d', 'euclidean_distance_3d', 'cosine_similarity_3d']:
            result = operator(*features, threshold)
        else:
            result = operator(*features, threshold)
        intermediate_results.append(result)

    # 第二步：根据二元或三元异常指标算子组合中间结果
    last_rule = rules[-1]
    operator_name = last_rule[0]
    operator = globals().get(operator_name)
    if operator is None:
        raise ValueError(f"未找到算子 {operator_name}")

    if len(intermediate_results) == 2:
        # 二元异常指标算子
        final_result = operator(*intermediate_results)
    elif len(intermediate_results) == 3:
        # 三元异常指标算子
        final_result = operator(*intermediate_results)
    else:
        raise ValueError("不支持的规则数量，仅支持二元或三元组合")

    return final_result


def get_llm_explanation(risk_features, rules, risk_indicator, url, model):
    """调用大模型解释风险指标计算逻辑"""
    prompt = f"""
    - 风险特征：{risk_features}
    - 判定规则：{rules}
    - 最终风险指标：{risk_indicator}

    请说明为什么最终风险指标是{risk_indicator}, 给出语义描述。
    """

    messages = [
        {'role': 'system', 'content': "你是逻辑分析助手，擅长解释规则判定过程。"},
        {'role': 'user', 'content': prompt.strip()}
    ]
    content = chat_with_requests(url, model, messages)
    return content


if __name__ == "__main__":
    # 1. 定义风险特征、规则
    risk_features = {
        "申报重量": 55,
        "限重": 50,
        "申报价格": 100,
        "参考价格": 80
    }

    rules = [
        ("diff_operator", ["申报重量", "限重"], 0),  # 申报重量 - 限重 > 0？
        ("ratio_operator", ["申报价格", "参考价格"], 1.2),  # 申报价格/参考价格 > 1.2？
        ("and_operator", [], None)  # 所有条件满足则风险指标为1
    ]

    # 2. 计算风险指标
    risk_indicator = generate_risk_indicator(risk_features, rules)
    print(f"风险指标: {risk_indicator}\n")

    url = "http://100.100.20.144:9997/v1/chat/completions"
    model = "qwen3"
    print(get_llm_explanation(risk_features, rules, risk_indicator, url, model))

    # # 3. 构建整合prompt
    # prompt = f"""
    # - 风险特征：{risk_features}
    # - 判定规则：
    #   1. {rules[0][0]}：比较{rules[0][1][0]}与{rules[0][1][1]}，阈值{rules[0][2]}
    #   2. {rules[1][0]}：比较{rules[1][1][0]}与{rules[1][1][1]}，阈值{rules[1][2]}
    #   3. {rules[2][0]}：需满足以上所有规则
    # - 最终风险指标：{risk_indicator}
    #
    # 请说明为什么最终风险指标是{risk_indicator}, 结合风险特征和判定规则的定义， 给出简洁一点的解释。
    # """
    #
    # # 4. 调用大模型
    # url = "http://100.100.20.144:9997/v1/chat/completions"
    # model = "qwen3"
    # messages = [
    #     {'role': 'system', 'content': "你是逻辑分析助手，擅长解释规则判定过程。"},
    #     {'role': 'user', 'content': prompt.strip()}
    # ]
    # content = chat_with_requests(url, model, messages)
    # print("大模型解释：\n", content)