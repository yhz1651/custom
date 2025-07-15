# 海关算子
By [@yhz1651](https://github.com/yhz1651)

### 项目简介
海关算子用于从指标系统的单维原始指标中提取多维特征，通过预设运算规则对申报信息（如重量、价格等核心指标）进行结构化分析，最终输出包含分步计算逻辑的多维特征结构，以及由大模型生成的语义化风险描述。

该工具可将分散的单维数据转化为可解释的风险判断依据，清晰呈现风险触发的计算链路与逻辑关系，为海关等场景的风险核查提供直观、可追溯的决策支持。

### 环境配置
```bash
# 创建默认环境
conda env create -f environment.yml

# 指定环境名称创建
conda env create -f environment.yml -n new_env_name

# 跨平台环境配置（兼容不同操作系统）
conda env create -f environment_cross_platform.yml

# 跨平台配置 + 指定环境名称
conda env create -f environment_cross_platform.yml -n new_env_name
```

### 启动服务
`python app.py`

> 若出现端口冲突，可修改 app.py 中的 port 参数调整端口，测试用例中的请求地址需同步更新。

### 接口测试用例

1. 方法一：curl测试

```bash
curl -X POST http://localhost:8000/explain_risk \
  -H "Content-Type: application/json" \
  -d '{
    "risk_features": {
      "申报重量": 55,
      "限重": 50,
      "申报价格": 100,
      "参考价格": 80
    },
    "rules": [
      ["diff_operator", ["申报重量", "限重"], 0],
      ["ratio_operator", ["申报价格", "参考价格"], 1.2],
      ["and_operator", [], null]
    ]
  }'
```

2. 方法二：postman测试

url: `http://localhost:8000/explain_risk`

参数类型：`Content-Type: application/json`

```json
{
  "risk_features": {
    "申报重量": 55,
    "限重": 50,
    "申报价格": 100,
    "参考价格": 80
  },
  "rules": [
    ["diff_operator", ["申报重量", "限重"], 0],
    ["ratio_operator", ["申报价格", "参考价格"], 1.2],
    ["and_operator", [], null]
  ]
}
```

**接口输出示例**

`multi_dimensional_structure`：包含原始特征、分步计算过程、中间结果及最终风险指标，清晰展示规则运算逻辑；

`semantic_description`：用自然语言解释风险判定依据、潜在影响及处理建议；

`summary`：风险结果摘要，快速呈现核心结论。
```json
{
  "multi_dimensional_structure": {
    "original_features": {
      "申报重量": 55,
      "限重": 50,
      "申报价格": 100,
      "参考价格": 80
    },
    "calculation_steps": [
      {
        "step": 1,
        "operator": "diff_operator",
        "input_features": {
          "申报重量": 55,
          "限重": 50
        },
        "threshold": 0,
        "result": 1,
        "description": "计算申报重量与限重的差值，判断是否大于等于阈值0，结果：满足条件"
      },
      {
        "step": 2,
        "operator": "ratio_operator",
        "input_features": {
          "申报价格": 100,
          "参考价格": 80
        },
        "threshold": 1.2,
        "result": 1,
        "description": "计算申报价格与参考价格的比值，判断是否大于等于阈值1.2，结果：满足条件"
      },
      {
        "step": 3,
        "operator": "and_operator",
        "input_results": [
          1,
          1
        ],
        "result": 1,
        "description": "逻辑与运算：所有条件([1, 1])均需满足，最终判定：触发风险"
      }
    ],
    "intermediate_results": [
      1,
      1
    ],
    "final_risk_indicator": 1,
    "rules_applied": [
      [
        "diff_operator",
        [
          "申报重量",
          "限重"
        ],
        0
      ],
      [
        "ratio_operator",
        [
          "申报价格",
          "参考价格"
        ],
        1.2
      ],
      [
        "and_operator",
        [],
        null
      ]
    ]
  },
  "semantic_description": "当申报重量**55**超过限重**50**，且申报价格**100**与参考价格**80**的比值达到**1.25**，即超出参考价格的**1.2**倍阈值时，判定为**伪瞒报高危风险**。此类风险可能导致货物实际重量或价值与申报信息存在显著偏差*运输安全风险**（如超载导致事故）、**环境安全风险**（如危险品运输失控）以及**贸易安全风险**（如走私、虚假申报引发的法律纠纷）。  \n需**立即触发人工查验**，并对货物进行**许可证溯源**及**运输路径核查**，确保申报信息真实有效，防止非法行为发生。",
  "summary": {
    "risk_indicator": 1,
    "risk_level": "高风险",
    "features_count": 4,
    "calculation_steps": 3
  }
} 
```

