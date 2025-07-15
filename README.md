# 海关算子

### 环境配置
```bash
conda env create -f environment.yml
conda env create -f environment.yml -n new_env_name # 指定环境名称
conda env create -f environment_cross_platform.yml # 跨平台环境配置
conda env create -f environment_cross_platform.yml -n new_env_name # 跨平台环境配置，指定环境名称
```

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

输出
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

