import csv
import random
import time
import json
from datetime import datetime, timedelta

# 分类定义海关相关的属性字段，并分组相关属性
numeric_attribute_groups = {
    "weight_related": ["申报重量", "限重", "净重", "毛重", "集装箱最大载重"],
    "price_related": ["申报价格", "参考价格", "货物价值", "市场均价", "历史成交价", "保险价值"],
    "tax_related": ["关税税率", "增值税率", "消费税率", "反倾销税率", "保障措施税率", "优惠税率"],
    "transport_related": ["运输温度", "运输湿度", "运输距离", "运输时长", "运输成本"],
    "enterprise_related": ["历史违规次数", "企业信用等级", "通关次数", "查验通过率", "违规金额"],
    "quantity_related": ["申报数量", "最小起订量", "最大订购量", "库存数量", "在途数量"],
    "time_related": ["生产日期", "有效期", "申报日期", "到港日期", "清关时限"]
}

categorical_attribute_groups = {
    "goods_related": ["货物类型", "包装类型", "危险品等级", "商品编码", "品牌", "型号", "规格"],
    "location_related": ["原产国", "目的国", "启运港", "目的港", "中转国", "贸易区"],
    "process_related": ["贸易方式", "运输方式", "检疫要求", "许可证要求", "监管条件", "检验检疫类别"],
    "enterprise_info": ["企业类型", "行业类别", "注册资本", "成立年限", "企业规模"],
    "certificate_related": ["原产地证书", "质量证书", "卫生证书", "动植物检疫证书", "安全许可证"]
}

# 所有属性
numeric_attributes = []
for group in numeric_attribute_groups.values():
    numeric_attributes.extend(group)

categorical_attributes = []
for group in categorical_attribute_groups.values():
    categorical_attributes.extend(group)

customs_attributes = numeric_attributes + categorical_attributes

# 定义算子及其所需的参数数量和属性类型
operators_info = {
    "diff_operator": {
        "name": "差值算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],
        "description": "计算两个特征值的差值",
        "compatible_groups": [["weight_related", "weight_related"],
                              ["price_related", "price_related"],
                              ["transport_related", "transport_related"],
                              ["quantity_related", "quantity_related"]]
    },
    "ratio_operator": {
        "name": "比值算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],
        "description": "计算两个特征值的比值",
        "compatible_groups": [["weight_related", "weight_related"],
                              ["price_related", "price_related"],
                              ["quantity_related", "quantity_related"]]
    },
    "comparison_operator": {
        "name": "对比算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],
        "description": "比较两个特征值的大小关系",
        "compatible_groups": [["weight_related", "weight_related"],
                              ["price_related", "price_related"],
                              ["tax_related", "tax_related"],
                              ["transport_related", "transport_related"],
                              ["enterprise_related", "enterprise_related"],
                              ["quantity_related", "quantity_related"],
                              ["time_related", "time_related"]]
    },
    "multiplication_operator": {
        "name": "乘法算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],
        "description": "计算两个特征值的乘积",
        "compatible_groups": [["price_related", "tax_related"],
                              ["weight_related", "price_related"]]
    },
    "subset_judgment_operator": {
        "name": "子集判断算子",
        "param_count": 2,
        "attribute_types": ["categorical", "categorical"],
        "description": "判断一个集合是否为另一个集合的子集",
        "compatible_groups": [["goods_related", "goods_related"],
                              ["location_related", "location_related"],
                              ["process_related", "process_related"],
                              ["certificate_related", "certificate_related"]]
    },
    "mean_operator": {
        "name": "均值算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],
        "description": "计算两个特征值的平均值",
        "compatible_groups": [["price_related", "price_related"],
                              ["weight_related", "weight_related"]]
    },
    "joint_probability_operator": {
        "name": "联合概率算子",
        "param_count": 2,
        "attribute_types": ["categorical", "categorical"],
        "description": "计算多个事件或特征的联合发生概率",
        "compatible_groups": [["goods_related", "location_related"],
                              ["goods_related", "process_related"],
                              ["location_related, process_related"],
                              ["certificate_related", "process_related"]]
    },
    "variance_operator": {
        "name": "方差算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],
        "description": "计算两个特征值的方差",
        "compatible_groups": [["price_related", "price_related"],
                              ["weight_related", "weight_related"]]
    },
    "weighted_combination_operator": {
        "name": "加权组合算子",
        "param_count": 3,
        "attribute_types": ["numeric", "numeric", "numeric"],
        "description": "计算多个特征值的加权综合值",
        "compatible_groups": [["price_related", "tax_related", "weight_related"]]
    }
}

# 规则类型和状态
rule_types = ["重量风险", "价格风险", "品类风险", "产地风险", "企业信用风险", "税收风险", "检疫风险", "数量风险",
              "时间风险"]
rule_statuses = ["启用", "禁用", "测试"]
operators = ["管理员", "系统", "审核员", "专家"]


# 根据算子类型和规则类型选择兼容的属性，确保不重复
def select_compatible_attributes(operator_key, rule_type, used_attributes):
    op_info = operators_info[operator_key]
    compatible_groups = op_info.get("compatible_groups", [])

    if not compatible_groups:
        # 如果没有定义兼容组，则回退到随机选择
        return select_attributes_by_type(op_info["attribute_types"], used_attributes)

    # 根据规则类型选择最相关的属性组
    if rule_type == "重量风险":
        preferred_groups = [g for g in compatible_groups if "weight_related" in g]
    elif rule_type == "价格风险":
        preferred_groups = [g for g in compatible_groups if "price_related" in g]
    elif rule_type == "品类风险":
        preferred_groups = [g for g in compatible_groups if "goods_related" in g]
    elif rule_type == "产地风险":
        preferred_groups = [g for g in compatible_groups if "location_related" in g]
    elif rule_type == "企业信用风险":
        preferred_groups = [g for g in compatible_groups if "enterprise_related" in g]
    elif rule_type == "税收风险":
        preferred_groups = [g for g in compatible_groups if "tax_related" in g]
    elif rule_type == "数量风险":
        preferred_groups = [g for g in compatible_groups if "quantity_related" in g]
    elif rule_type == "时间风险":
        preferred_groups = [g for g in compatible_groups if "time_related" in g]
    else:  # 检疫风险
        preferred_groups = [g for g in compatible_groups if "process_related" in g]

    # 如果没有找到首选组，使用所有兼容组
    if not preferred_groups:
        preferred_groups = compatible_groups

    # 尝试多次找到不重复的属性组合
    max_attempts = 10
    for attempt in range(max_attempts):
        # 随机选择一个兼容组
        selected_group_pair = random.choice(preferred_groups)

        # 从每个组中选择一个属性
        selected_attributes = []
        for group_key in selected_group_pair:
            group_attributes = []
            if group_key in numeric_attribute_groups:
                group_attributes = numeric_attribute_groups[group_key]
            elif group_key in categorical_attribute_groups:
                group_attributes = categorical_attribute_groups[group_key]

            # 过滤掉已使用的属性
            available_attributes = [attr for attr in group_attributes if attr not in used_attributes]

            if available_attributes:
                selected_attributes.append(random.choice(available_attributes))
            elif group_attributes:
                # 如果没有可用属性，从整个组中选择
                selected_attributes.append(random.choice(group_attributes))

        # 检查是否有重复属性
        if len(selected_attributes) == len(set(selected_attributes)):
            return selected_attributes

    # 如果多次尝试后仍然找不到不重复的属性，返回空列表
    return []


# 根据属性类型选择属性（回退方法），确保不重复
def select_attributes_by_type(attribute_types, used_attributes):
    selected_attributes = []
    for attr_type in attribute_types:
        if attr_type == "numeric":
            available_attrs = [attr for attr in numeric_attributes if attr not in used_attributes]
            if available_attrs:
                selected_attributes.append(random.choice(available_attrs))
            else:
                selected_attributes.append(random.choice(numeric_attributes))
        elif attr_type == "categorical":
            available_attrs = [attr for attr in categorical_attributes if attr not in used_attributes]
            if available_attrs:
                selected_attributes.append(random.choice(available_attrs))
            else:
                selected_attributes.append(random.choice(categorical_attributes))

    # 检查是否有重复属性
    if len(selected_attributes) != len(set(selected_attributes)):
        # 如果有重复，重新选择
        return select_attributes_by_type(attribute_types, used_attributes)

    return selected_attributes


# 生成分层规则结构
def generate_rule_structure(rule_type):
    # 根据规则类型确定基础算子
    if rule_type == "重量风险":
        base_operators = ["diff_operator", "comparison_operator", "ratio_operator"]
    elif rule_type == "价格风险":
        base_operators = ["ratio_operator", "comparison_operator", "multiplication_operator", "mean_operator"]
    elif rule_type == "品类风险":
        base_operators = ["subset_judgment_operator", "joint_probability_operator"]
    elif rule_type == "产地风险":
        base_operators = ["subset_judgment_operator", "joint_probability_operator"]
    elif rule_type == "企业信用风险":
        base_operators = ["comparison_operator", "variance_operator"]
    elif rule_type == "税收风险":
        base_operators = ["ratio_operator", "comparison_operator", "multiplication_operator"]
    elif rule_type == "数量风险":
        base_operators = ["diff_operator", "comparison_operator", "ratio_operator"]
    elif rule_type == "时间风险":
        base_operators = ["comparison_operator", "diff_operator"]
    else:  # 检疫风险
        base_operators = ["subset_judgment_operator", "joint_probability_operator"]

    # 确定规则复杂度 (1-3个基础算子)
    num_base_operators = random.randint(1, min(3, len(base_operators)))

    # 选择基础算子
    selected_operators = random.sample(base_operators, num_base_operators)

    # 构建规则结构
    rule_structure = []
    used_attributes = set()  # 跟踪已使用的属性

    # 添加基础算子
    for op in selected_operators:
        op_info = operators_info[op]
        param_count = op_info["param_count"]

        # 选择兼容的属性，确保不重复
        attributes = select_compatible_attributes(op, rule_type, used_attributes)

        if not attributes:
            # 如果找不到合适的属性，跳过这个算子
            continue

        # 更新已使用的属性
        used_attributes.update(attributes)

        # 设置阈值
        if "diff" in op or "comparison" in op:
            threshold = round(random.uniform(-100, 100), 2)
        elif "ratio" in op:
            threshold = round(random.uniform(0.5, 2.0), 2)
        elif "subset" in op or "joint" in op:
            threshold = random.choice([0, 1])
        else:
            threshold = round(random.uniform(0, 10), 2)

        rule_structure.append([op, attributes, threshold])

    return rule_structure


# 生成规则数据
def generate_rules_data(num_records, output_file):
    # CSV文件头
    fieldnames = [
        "rule_id", "rule_name", "rule_description", "rule_type", "rule_status",
        "rule_structure", "calculation_method",
        "created_time", "updated_time", "operator"
    ]

    # 打开CSV文件准备写入
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # 基础时间戳（一年前）
        base_time = int(time.time()) - 365 * 24 * 60 * 60

        # 生成每条规则
        for i in range(num_records):
            # 规则ID
            rule_id = f"CUS_RULE_{i + 1:07d}"

            # 规则类型和名称
            rule_type = random.choice(rule_types)
            rule_name = f"{rule_type}检测规则_{i + 1}"

            # 规则描述
            rule_descriptions = {
                "重量风险": "检测货物的申报重量与限重关系，防止超重申报或低报重量",
                "价格风险": "检测货物的申报价格与市场参考价格偏差，防止低报或高报价格",
                "品类风险": "检测货物品类与申报是否一致，防止伪报品名或瞒报品类",
                "产地风险": "检测货物原产国与申报是否一致，防止伪报产地逃避关税",
                "企业信用风险": "检测货物申报企业的信用等级和历史违规情况，评估企业风险",
                "税收风险": "检测货物的关税、增值税和消费税申报准确性，防止偷逃税款",
                "检疫风险": "检测货物是否符合检疫要求和许可证要求，防止疫情传播",
                "数量风险": "检测货物申报数量与实际数量的一致性，防止瞒报或少报",
                "时间风险": "检测货物生产日期、有效期和清关时限，防止过期或违规"
            }
            rule_description = rule_descriptions.get(rule_type, "海关风险检测规则")

            # 规则状态
            rule_status = random.choice(rule_statuses)

            # 生成规则结构
            rule_structure = generate_rule_structure(rule_type)

            # 如果规则结构为空，重新生成
            if not rule_structure:
                rule_structure = generate_rule_structure(rule_type)

            # 如果仍然为空，使用默认结构
            if not rule_structure:
                rule_structure = [["comparison_operator", ["申报重量", "限重"], 0]]

            # 计算方法描述
            calculation_method = f"使用分层规则结构进行{rule_type.lower()}检测，"
            calculation_method += f"包含{len(rule_structure)}个计算步骤。"

            # 时间戳
            created_time = base_time + random.randint(0, 365 * 24 * 60 * 60)
            updated_time = created_time + random.randint(0, 30 * 24 * 60 * 60)

            # 操作人
            operator = random.choice(operators)

            # 写入一行数据
            writer.writerow({
                "rule_id": rule_id,
                "rule_name": rule_name,
                "rule_description": rule_description,
                "rule_type": rule_type,
                "rule_status": rule_status,
                "rule_structure": json.dumps(rule_structure, ensure_ascii=False),
                "calculation_method": calculation_method,
                "created_time": created_time,
                "updated_time": updated_time,
                "operator": operator
            })

            # 每生成10000条输出进度
            if (i + 1) % 10000 == 0:
                print(f"已生成 {i + 1} 条规则")

    print(f"数据生成完成，已保存到 {output_file}")


# 主程序
if __name__ == "__main__":
    num_records = 1000000  # 100万条记录
    output_file = "data/rules.csv"

    print("开始生成海关风险预警规则数据...")
    start_time = time.time()

    generate_rules_data(num_records, output_file)

    end_time = time.time()
    print(f"总耗时: {end_time - start_time:.2f} 秒")

    # 显示文件大小
    import os

    file_size = os.path.getsize(output_file)
    print(f"生成文件大小: {file_size / 1024 / 1024:.2f} MB")