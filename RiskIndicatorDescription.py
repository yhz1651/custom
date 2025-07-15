# 假设之前的算子代码已经保存为 operators.py
from operators import *
from api import *

def generate_risk_indicator(risk_features, rules):
    """
    根据风险特征和规则生成风险指标
    :param risk_features: 风险特征字典，键为特征名称，值为特征值
    :param rules: 风险规则列表，每个规则是一个元组，格式为 (算子名称, 特征名称列表, 阈值)
    :return: 包含多维计算结构的字典
    """
    intermediate_results = []
    calculation_steps = []
    
    # 第一步：计算属性算子结果
    for i, rule in enumerate(rules[:-1]):  # 排除最后一个规则（逻辑算子规则）
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
        
        # 记录计算步骤
        step_info = {
            "step": i + 1,
            "operator": operator_name,
            "input_features": {name: risk_features[name] for name in feature_names},
            "threshold": threshold,
            "result": result,
            "description": get_operator_description(operator_name, feature_names, threshold, result)
        }
        calculation_steps.append(step_info)

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

    # 记录最终步骤
    final_step = {
        "step": len(calculation_steps) + 1,
        "operator": operator_name,
        "input_results": intermediate_results,
        "result": final_result,
        "description": get_logical_operator_description(operator_name, intermediate_results, final_result)
    }
    calculation_steps.append(final_step)

    # 构建多维计算结构
    multi_dimensional_structure = {
        "original_features": risk_features,
        "calculation_steps": calculation_steps,
        "intermediate_results": intermediate_results,
        "final_risk_indicator": final_result,
        "rules_applied": rules
    }

    return multi_dimensional_structure

def get_operator_description(operator_name, feature_names, threshold, result):
    """生成算子计算描述"""
    operator_descriptions = {
        "diff_operator": f"计算{feature_names[0]}与{feature_names[1]}的差值，判断是否大于等于阈值{threshold}",
        "ratio_operator": f"计算{feature_names[0]}与{feature_names[1]}的比值，判断是否大于等于阈值{threshold}",
        "cmp_operator": f"比较{feature_names[0]}与{feature_names[1]}的大小",
        "avg_operator": f"计算{feature_names[0]}与{feature_names[1]}的平均值，判断是否大于等于阈值{threshold}",
        "weighted_avg_operator": f"计算加权平均值，判断是否大于等于阈值{threshold}",
        "subset_operator": f"判断{feature_names[0]}是否为{feature_names[1]}的子集"
    }
    
    base_desc = operator_descriptions.get(operator_name, f"应用{operator_name}算子")
    result_desc = "满足条件" if result == 1 else "不满足条件"
    return f"{base_desc}，结果：{result_desc}"

def get_logical_operator_description(operator_name, input_results, final_result):
    """生成逻辑算子描述"""
    logical_descriptions = {
        "and_operator": f"逻辑与运算：所有条件({input_results})均需满足",
        "or_operator": f"逻辑或运算：任一条件({input_results})满足即可",
        "and3_operator": f"三元逻辑与运算：所有三个条件({input_results})均需满足",
        "or3_operator": f"三元逻辑或运算：任一条件({input_results})满足即可"
    }
    
    base_desc = logical_descriptions.get(operator_name, f"应用{operator_name}逻辑运算")
    result_desc = "触发风险" if final_result == 1 else "未触发风险"
    return f"{base_desc}，最终判定：{result_desc}"

def get_llm_explanation(risk_features, rules, multi_dimensional_structure, url, model):
    """调用大模型解释风险指标计算逻辑，生成详细的语义描述"""
    
    # 构建详细的计算过程描述
    calculation_process = ""
    for step in multi_dimensional_structure["calculation_steps"]:
        calculation_process += f"步骤{step['step']}: {step['description']}\n"
    
    prompt = f"""
    基于以下多维风险特征分析，请生成详细的风险语义描述：
    
    【原始风险特征】
    {risk_features}
    
    【计算过程】
    {calculation_process}
    
    【最终风险指标】
    {multi_dimensional_structure['final_risk_indicator']}
    
    请按照以下要求生成语义描述：
    1. 识别风险类型（如：伪瞒报高危风险、运输违规风险、申报异常风险等）
    2. 分析具体的风险表现（基于计算过程中触发的条件）
    3. 评估潜在威胁和影响（对运输安全、环境安全、贸易安全等的威胁）
    4. 提出应对建议（如：立即触发人工查验、许可证溯源、路径核查等）
    
    示例格式：当[具体条件]时，判定为'[风险类型]'。此类风险可能导致[威胁分析]，需[应对建议]。
    """

    messages = [
        {'role': 'system', 'content': "你是专业的风险分析专家，擅长基于多维特征进行风险识别和语义描述。"},
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
    multi_dimensional_structure = generate_risk_indicator(risk_features, rules)
    risk_indicator = multi_dimensional_structure['final_risk_indicator']
    print(f"风险指标: {risk_indicator}\n")

    url = "http://100.100.20.144:9997/v1/chat/completions"
    model = "qwen3"
    print(get_llm_explanation(risk_features, rules, multi_dimensional_structure, url, model))

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
