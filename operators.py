import math
from typing import Union, List, Set

# ==============================
# 一、属性算子（输入为特征值，输出0/1）
# ==============================

def cmp_operator(A: Union[int, float], B: Union[int, float]) -> int:
    """大小比较算子：A >= B 返回1，否则0"""
    return 1 if A >= B else 0

def diff_operator(A: Union[int, float], B: Union[int, float], threshold: Union[int, float]) -> int:
    """差值算子：A-B >= threshold 返回1，否则0"""
    return 1 if (A - B) >= threshold else 0

def mul_operator(A: Union[int, float], B: Union[int, float], threshold: Union[int, float]) -> int:
    """乘法算子：A*B >= threshold 返回1，否则0"""
    return 1 if (A * B) >= threshold else 0

def ratio_operator(A: Union[int, float], B: Union[int, float], threshold: Union[float, int]) -> int:
    """比值算子：A/B >= threshold 返回1，注意B不能为0（需提前处理业务层防除零）"""
    if B == 0:
        raise ValueError("除数B不能为0")
    return 1 if (A / B) >= threshold else 0

def diff_ratio_operator(A: Union[int, float], B: Union[int, float], threshold: float) -> int:
    """差分比率算子：(A-B)/B*100% >= threshold 返回1"""
    if B == 0:
        raise ValueError("基准值B不能为0")
    ratio = (A - B) / B * 100
    return 1 if ratio >= threshold else 0

def subset_operator(A: Set, B: Set) -> int:
    """子集判断算子：A是B的子集返回1，否则0"""
    return 1 if A.issubset(B) else 0

def avg_operator(A: Union[int, float], B: Union[int, float], threshold: Union[int, float]) -> int:
    """均值算子：(A+B)/2 >= threshold 返回1"""
    return 1 if (A + B) / 2 >= threshold else 0

def var_operator(A: Union[int, float], B: Union[int, float], threshold: Union[int, float]) -> int:
    """方差算子：计算两个值的方差并与阈值比较"""
    mean = (A + B) / 2
    variance = ((A - mean)**2 + (B - mean)**2) / 2
    return 1 if variance >= threshold else 0

def euclidean_distance_2d(x1: float, y1: float, x2: float, y2: float, threshold: float) -> int:
    """二维欧几里得距离算子：距离>=threshold返回1"""
    distance = math.hypot(x2 - x1, y2 - y1)
    return 1 if distance >= threshold else 0

def weighted_avg_operator(weights: List[float], values: List[float], threshold: float) -> int:
    """加权组合算子：加权和>=threshold返回1，weights与values长度需一致"""
    if len(weights) != len(values):
        raise ValueError("权重与特征值数量不一致")
    weighted_sum = sum(w * v for w, v in zip(weights, values))
    return 1 if weighted_sum >= threshold else 0

def cross_deviation_operator(A: float, B: float, C: float, threshold: float) -> int:
    """交叉偏差算子：|A-B|+|B-C|+|C-A| >= threshold 返回1"""
    deviation = abs(A - B) + abs(B - C) + abs(C - A)
    return 1 if deviation >= threshold else 0

def multivariate_var_operator(A: float, B: float, C: float, threshold: float) -> int:
    """多变量方差算子：计算三个值的方差并与阈值比较"""
    mean = (A + B + C) / 3
    variance = ((A - mean)**2 + (B - mean)**2 + (C - mean)**2) / 3
    return 1 if variance >= threshold else 0

def euclidean_distance_3d(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, threshold: float) -> int:
    """三维欧几里得距离算子：距离>=threshold返回1"""
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return 1 if distance >= threshold else 0

def joint_probability_operator(P_A: float, P_B_given_A: float, P_C_given_AB: float, threshold: float) -> int:
    """联合概率算子：P(A)*P(B|A)*P(C|AB) >= threshold 返回1"""
    joint_prob = P_A * P_B_given_A * P_C_given_AB
    return 1 if joint_prob >= threshold else 0

def cosine_similarity_3d(A: List[float], B: List[float], threshold: float) -> int:
    """三维余弦相似性算子：余弦相似度>=threshold返回1，A/B需为三维向量"""
    if len(A) != 3 or len(B) != 3:
        raise ValueError("输入向量必须为三维")
    dot_product = A[0]*B[0] + A[1]*B[1] + A[2]*B[2]
    norm_A = math.sqrt(A[0]**2 + A[1]**2 + A[2]**2)
    norm_B = math.sqrt(B[0]**2 + B[1]**2 + B[2]**2)
    if norm_A == 0 or norm_B == 0:
        return 0  # 零向量相似度定义为0
    cos_sim = dot_product / (norm_A * norm_B)
    return 1 if cos_sim >= threshold else 0

# ==============================
# 二、二元异常指标算子（输入为0/1，输出0/1）
# ==============================

def and_operator(A: int, B: int) -> int:
    """逻辑与算子：A和B均为1返回1，否则0"""
    return 1 if (A == 1 and B == 1) else 0

def or_operator(A: int, B: int) -> int:
    """逻辑或算子：A或B为1返回1，否则0"""
    return 1 if (A == 1 or B == 1) else 0

def xor_operator(A: int, B: int) -> int:
    """逻辑异或算子：A和B不同返回1，否则0"""
    return 1 if A != B else 0

def implication_operator(A: int, B: int) -> int:
    """逻辑蕴含算子：A为1且B为0时返回0，否则1（即¬A∨B）"""
    return 0 if (A == 1 and B == 0) else 1

def nand_operator(A: int, B: int) -> int:
    """逻辑与非算子：A和B均为1时返回0，否则1（即¬(A∧B)）"""
    return 0 if (A == 1 and B == 1) else 1

def nor_operator(A: int, B: int) -> int:
    """逻辑或非算子：A和B均为0时返回1，否则0（即¬(A∨B)）"""
    return 1 if (A == 0 and B == 0) else 0

def equivalence_operator(A: int, B: int) -> int:
    """逻辑等价算子：A和B相同返回1，否则0（即A≡B）"""
    return 1 if A == B else 0

# ==============================
# 三、三元异常指标算子（输入为0/1，输出0/1）
# ==============================

def and3_operator(A: int, B: int, C: int) -> int:
    """三元逻辑与算子：A、B、C均为1返回1，否则0"""
    return 1 if (A == 1 and B == 1 and C == 1) else 0

def or3_operator(A: int, B: int, C: int) -> int:
    """三元逻辑或算子：至少一个为1返回1，否则0"""
    return 1 if (A == 1 or B == 1 or C == 1) else 0

def xor3_operator(A: int, B: int, C: int) -> int:
    """三元逻辑异或算子：奇数个1返回1，否则0"""
    return 1 if (A + B + C) % 2 == 1 else 0

def implication3_operator(A: int, B: int, C: int) -> int:
    """三元逻辑蕴含算子：¬(A∧B∧¬C)，即A和B为1且C为0时返回0，否则1"""
    return 0 if (A == 1 and B == 1 and C == 0) else 1