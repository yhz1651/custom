import csv
import random
import time
from datetime import datetime, timedelta

# 定义海关相关的属性字段
customs_attributes = [
    "申报重量", "限重", "申报价格", "参考价格", "货物类型",
    "原产国", "目的国", "贸易方式", "运输方式", "企业信用等级",
    "历史违规次数", "关税税率", "增值税率", "消费税率", "检疫要求",
    "许可证要求", "包装类型", "危险品等级", "货物价值", "运输温度"
]

# 定义属性算子（使用英文表示）
attribute_operators = [
    "comparison_operator", "difference_operator", "multiplication_operator",
    "ratio_operator", "differential_ratio_operator", "subset_judgment_operator",
    "mean_operator", "variance_operator", "euclidean_distance_operator",
    "weighted_combination_operator", "cross_deviation_operator",
    "multivariate_variance_operator", "3d_euclidean_operator",
    "joint_probability_operator", "multidimensional_similarity_operator"
]

# 定义二元异常指标算子（使用英文表示）
binary_anomaly_operators = [
    "logical_and_operator", "logical_or_operator", "logical_xor_operator",
    "logical_implication_operator", "logical_nand_operator",
    "logical_nor_operator", "logical_equivalence_operator"
]

# 定义三元异常指标算子（使用英文表示）
ternary_anomaly_operators = [
    "ternary_logical_and_operator", "ternary_logical_or_operator",
    "ternary_logical_xor_operator", "ternary_logical_implication_operator"
]

# 规则类型和状态
rule_types = ["重量风险", "价格风险", "品类风险", "产地风险", "企业信用风险", "税收风险", "检疫风险"]
rule_statuses = ["启用"]
# rule_statuses = ["启用", "禁用", "测试中", "待审核"]
operators = ["管理员"]
# operators = ["海关管理员", "系统自动", "风险分析师", "审计员", "监管官员"]


# 生成规则数据
def generate_rules_data(num_records, output_file):
    # CSV文件头
    fieldnames = [
        "rule_id", "rule_name", "rule_description", "rule_type", "rule_status",
        "related_attributes", "related_operators", "threshold", "calculation_method",
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

            # 相关属性（2-4个）
            num_attrs = random.randint(2, 4)
            related_attributes = random.sample(customs_attributes, num_attrs)

            # 相关算子（1-3个）
            num_ops = random.randint(1, 3)
            # 80%的概率使用属性算子，20%的概率使用异常指标算子
            if random.random() < 0.8:
                related_operators = random.sample(attribute_operators, num_ops)
            else:
                # 从二元和三元异常指标算子中随机选择
                if random.random() < 0.7:
                    related_operators = random.sample(binary_anomaly_operators, num_ops)
                else:
                    related_operators = random.sample(ternary_anomaly_operators, num_ops)

            # 阈值（根据算子类型生成不同的阈值）
            threshold = []
            for op in related_operators:
                if "comparison" in op or "difference" in op or "multiplication" in op:
                    threshold.append(round(random.uniform(-100, 100), 2))
                elif "ratio" in op or "differential" in op:
                    threshold.append(round(random.uniform(0.5, 2.0), 2))
                elif "subset" in op or "logical" in op:
                    threshold.append(random.choice([0, 1]))
                else:  # 其他算子
                    threshold.append(round(random.uniform(0, 10), 2))

            # 计算方法描述
            calculation_method = f"使用{', '.join(related_operators)}对{', '.join(related_attributes)}进行计算，"
            calculation_method += f"阈值设置为{threshold}，用于检测{rule_type.lower()}。"

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
                "related_attributes": "|".join(related_attributes),
                "related_operators": "|".join(related_operators),
                "threshold": "|".join(map(str, threshold)),
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