import csv
import random
import time
import json
from datetime import datetime, timedelta

# 分类定义海关相关的属性字段
numeric_attributes = [
    "申报重量", "限重", "申报价格", "参考价格",
    "关税税率", "增值税率", "消费税率", "货物价值",
    "运输温度", "历史违规次数", "企业信用等级"
]

categorical_attributes = [
    "货物类型", "原产国", "目的国", "贸易方式", "运输方式",
    "检疫要求", "许可证要求", "包装类型", "危险品等级"
]

# 所有属性
customs_attributes = numeric_attributes + categorical_attributes

# 定义算子及其所需的参数数量和属性类型
operators_info = {
    "diff_operator": {
        "name": "差值算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],  # 需要两个数值属性
        "description": "计算两个特征值的差值"
    },
    "ratio_operator": {
        "name": "比值算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],  # 需要两个数值属性
        "description": "计算两个特征值的比值"
    },
    "comparison_operator": {
        "name": "对比算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],  # 需要两个数值属性
        "description": "比较两个特征值的大小关系"
    },
    "multiplication_operator": {
        "name": "乘法算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],  # 需要两个数值属性
        "description": "计算两个特征值的乘积"
    },
    "differential_ratio_operator": {
        "name": "差分比率算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],  # 需要两个数值属性
        "description": "计算差分值相对于基准值的比率"
    },
    "subset_judgment_operator": {
        "name": "子集判断算子",
        "param_count": 2,
        "attribute_types": ["categorical", "categorical"],  # 需要两个分类属性
        "description": "判断一个集合是否为另一个集合的子集"
    },
    "mean_operator": {
        "name": "均值算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],  # 需要两个数值属性
        "description": "计算两个特征值的平均值"
    },
    "variance_operator": {
        "name": "方差算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],  # 需要两个数值属性
        "description": "计算两个特征值的方差"
    },
    "euclidean_distance_operator": {
        "name": "欧几里得距离算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],  # 需要两个数值属性
        "description": "计算两点间的欧几里得距离"
    },
    "weighted_combination_operator": {
        "name": "加权组合算子",
        "param_count": 3,
        "attribute_types": ["numeric", "numeric", "numeric"],  # 需要三个数值属性
        "description": "计算多个特征值的加权综合值"
    },
    "cross_deviation_operator": {
        "name": "交叉偏差算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],  # 需要两个数值属性
        "description": "计算多个特征值的交叉偏差"
    },
    "multivariate_variance_operator": {
        "name": "多变量方差算子",
        "param_count": 3,
        "attribute_types": ["numeric", "numeric", "numeric"],  # 需要三个数值属性
        "description": "计算多个特征值之间的方差"
    },
    "3d_euclidean_operator": {
        "name": "三维欧几里得算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],  # 需要两个数值属性
        "description": "计算三维空间中点之间的欧几里得距离"
    },
    "joint_probability_operator": {
        "name": "联合概率算子",
        "param_count": 2,
        "attribute_types": ["categorical", "categorical"],  # 需要两个分类属性
        "description": "计算多个事件或特征的联合发生概率"
    },
    "multidimensional_similarity_operator": {
        "name": "多维相似性算子",
        "param_count": 2,
        "attribute_types": ["numeric", "numeric"],  # 需要两个数值属性
        "description": "计算三维空间的余弦相似度"
    },
    "logical_and_operator": {
        "name": "逻辑与运算算子",
        "param_count": 0,  # 逻辑运算符不直接使用属性
        "attribute_types": [],
        "description": "对两个特征值进行逻辑与运算"
    },
    "logical_or_operator": {
        "name": "逻辑或运算算子",
        "param_count": 0,
        "attribute_types": [],
        "description": "对两个特征值进行逻辑或运算"
    },
    "logical_xor_operator": {
        "name": "逻辑异或运算算子",
        "param_count": 0,
        "attribute_types": [],
        "description": "对两个特征值进行逻辑异或运算"
    },
    "logical_implication_operator": {
        "name": "逻辑蕴含运算算子",
        "param_count": 0,
        "attribute_types": [],
        "description": "对两个特征值进行逻辑蕴含运算"
    },
    "logical_nand_operator": {
        "name": "逻辑与非运算算子",
        "param_count": 0,
        "attribute_types": [],
        "description": "对两个特征值进行逻辑与非运算"
    },
    "logical_nor_operator": {
        "name": "逻辑或非运算算子",
        "param_count": 0,
        "attribute_types": [],
        "description": "对两个特征值进行逻辑或非运算"
    },
    "logical_equivalence_operator": {
        "name": "逻辑等价运算算子",
        "param_count": 0,
        "attribute_types": [],
        "description": "对两个特征值进行逻辑等价运算"
    },
    "ternary_logical_and_operator": {
        "name": "三元逻辑与运算算子",
        "param_count": 0,
        "attribute_types": [],
        "description": "对三个特征值进行逻辑与运算"
    },
    "ternary_logical_or_operator": {
        "name": "三元逻辑或运算算子",
        "param_count": 0,
        "attribute_types": [],
        "description": "对三个特征值进行逻辑或运算"
    },
    "ternary_logical_xor_operator": {
        "name": "三元逻辑异或运算算子",
        "param_count": 0,
        "attribute_types": [],
        "description": "对三个特征值进行逻辑异或运算"
    },
    "ternary_logical_implication_operator": {
        "name": "三元逻辑蕴含运算算子",
        "param_count": 0,
        "attribute_types": [],
        "description": "对三个特征值进行逻辑蕴含运算"
    }
}

# 规则类型和状态
rule_types = ["重量风险", "价格风险", "品类风险", "产地风险", "企业信用风险", "税收风险", "检疫风险"]
rule_statuses = ["启用"]
operators = ["管理员"]


# 根据属性类型选择属性
def select_attributes_by_type(attribute_types):
    selected_attributes = []
    for attr_type in attribute_types:
        if attr_type == "numeric":
            selected_attributes.append(random.choice(numeric_attributes))
        elif attr_type == "categorical":
            selected_attributes.append(random.choice(categorical_attributes))
    return selected_attributes


# 生成分层规则结构
def generate_rule_structure(rule_type):
    # 根据规则类型确定基础算子
    if rule_type == "重量风险":
        base_operators = ["diff_operator", "comparison_operator", "ratio_operator"]
    elif rule_type == "价格风险":
        base_operators = ["ratio_operator", "comparison_operator", "multiplication_operator"]
    elif rule_type == "品类风险":
        base_operators = ["subset_judgment_operator", "joint_probability_operator"]
    elif rule_type == "产地风险":
        base_operators = ["subset_judgment_operator", "joint_probability_operator"]
    elif rule_type == "企业信用风险":
        base_operators = ["comparison_operator", "mean_operator", "variance_operator"]
    elif rule_type == "税收风险":
        base_operators = ["ratio_operator", "comparison_operator", "multiplication_operator"]
    else:  # 检疫风险
        base_operators = ["subset_judgment_operator", "joint_probability_operator"]

    # 确定规则复杂度 (1-3个基础算子 + 0-1个逻辑算子)
    num_base_operators = random.randint(1, 3)
    use_logical_operator = random.random() < 0.5  # 50%的概率使用逻辑算子

    # 选择基础算子
    selected_operators = random.sample(base_operators, min(num_base_operators, len(base_operators)))

    # 构建规则结构
    rule_structure = []

    # 添加基础算子
    for op in selected_operators:
        op_info = operators_info[op]
        param_count = op_info["param_count"]
        attribute_types = op_info["attribute_types"]

        # 选择适当类型的属性
        if param_count > 0 and attribute_types:
            attributes = select_attributes_by_type(attribute_types)
        else:
            attributes = []

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

    # 添加逻辑算子 (如果需要)
    if use_logical_operator and len(selected_operators) > 1:
        logical_operators = [k for k in operators_info.keys() if
                             "logical" in k and operators_info[k]["param_count"] == 0]
        if logical_operators:
            logical_op = random.choice(logical_operators)
            rule_structure.append([logical_op, [], None])

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
            if rule_type == "重量风险":
                rule_description = f"检测货物的申报重量与限重关系，防止超重申报"
            elif rule_type == "价格风险":
                rule_description = f"检测货物的申报价格与市场参考价格偏差，防止低报或高报价格"
            elif rule_type == "品类风险":
                rule_description = f"检测货物品类与申报是否一致，防止伪报品名"
            elif rule_type == "产地风险":
                rule_description = f"检测货物原产国与申报是否一致，防止伪报产地"
            elif rule_type == "企业信用风险":
                rule_description = f"检测货物申报企业的信用等级和历史违规情况"
            elif rule_type == "税收风险":
                rule_description = f"检测货物的关税、增值税和消费税申报准确性"
            else:  # 检疫风险
                rule_description = f"检测货物是否符合检疫要求和许可证要求"

            # 规则状态
            rule_status = random.choice(rule_statuses)

            # 生成规则结构
            rule_structure = generate_rule_structure(rule_type)

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