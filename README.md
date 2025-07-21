# 基于“物-事-证”的多维特征提取与描述算法
By [@yhz1651](https://github.com/yhz1651)

- [项目简介](#项目简介)
- [环境配置](#环境配置)
- [启动服务](#启动服务)
- [接口输入输出示例](#接口输入输出示例)
  - [测试方法](#测试方法)
  - [案例1：申报重量与商品编码匹配性校验](#案例1申报重量与商品编码匹配性校验)
  - [案例2：完税价格异常校验](#案例2完税价格异常校验)
  - [案例3：数量与税额匹配性核查](#案例3数量与税额匹配性核查)
  - [案例4：报关单单价与总价匹配性校验](#案例4报关单单价与总价匹配性校验)
- [参考资料](#参考资料)



## 项目简介
海关监管在维护国家经济安全和国际贸易秩序中至关重要，但面临多时空要素风险关联内隐、态势判别复杂、跨部门联动局限等挑战。人工监管压力大，且存在单指标阈值预警误报率高、指标命名描述体系混乱等问题，智慧海关建设迫在眉睫，因此开展基于 “物 - 事 - 证” 的多维特征提取与描述算法研究。

围绕 “物 - 事 - 证 - 场 - 人” 维度，设计了属性算子和异常指标算子（含二元、三元算子）进行多维风险特征提取，输出均为是否异常。同时建立风险指标统一标识规则，按算子类型规范命名格式，并提出 “算子展开 - 业务匹配 - 大模型总结” 的描述方法，通过复杂指标拆分、业务场景关联等流程生成自然语言描述，提升海关监管精准度与效率。

## 环境配置

```bash
# 创建默认环境
conda env create -f env/environment.yml

# 指定环境名称创建
conda env create -f env/environment.yml -n new_env_name

# 跨平台环境配置（兼容不同操作系统）
conda env create -f env/environment_cross_platform.yml

# 跨平台配置 + 指定环境名称
conda env create -f env/environment_cross_platform.yml -n new_env_name
```

## 启动服务

`python app.py`

> 若出现端口冲突，可修改 app.py 中的 port 参数调整端口，测试用例中的请求地址需同步更新。

## 接口输入输出示例

### 测试方法
1. 方法一：curl测试

```bash
curl -X POST http://localhost:8000/explain_risk \
  -H "Content-Type: application/json" \
  -d '{
    "risk_features": {
      ……
    },
    "rules": [
      ……
    ]
  }'
```

2. 方法二：postman测试

url: `http://localhost:8000/explain_risk`

参数类型：`Content-Type: application/json`

参数：
```json
{
  "risk_features": {
    ……
  },
  "rules": [
    ……
  ]
}
```
接口输出示例

`multi_dimensional_structure`：包含原始特征、分步计算过程、中间结果及最终风险指标，清晰展示规则运算逻辑；

`semantic_description`：用自然语言解释风险判定依据、潜在影响及处理建议；

`summary`：风险结果摘要，快速呈现核心结论。

### 案例1：申报重量与商品编码匹配性校验

**接口输入**

```bash
curl -X POST http://localhost:8000/explain_risk \
  -H "Content-Type: application/json" \
  -d '{
    "risk_features": {
      "申报重量": 55, 
      "商品编码对应标准重量上限": 50,  
      "申报单价": 100,  
      "同商品编码平均单价": 80  
    },
    "rules": [
      ["diff_operator", ["申报重量", "商品编码对应标准重量上限"], 0],  
      ["ratio_operator", ["申报单价", "同商品编码平均单价"], 1.2],  
      ["and_operator", [], null]  
    ]
  }'
```

**接口输出**

```json
{
  "multi_dimensional_structure": {
    "original_features": {
      "申报重量": 55,
      "商品编码对应标准重量上限": 50,
      "申报单价": 100,
      "同商品编码平均单价": 80
    },
    "calculation_steps": [
      {
        "step": 1,
        "operator": "diff_operator",
        "input_features": {
          "申报重量": 55,
          "商品编码对应标准重量上限": 50
        },
        "threshold": 0,
        "result": 1,
        "description": "计算申报重量与商品编码对应标准重量上限的差值，判断是否大于等于阈值0，结果：满足条件"
      },
      {
        "step": 2,
        "operator": "ratio_operator",
        "input_features": {
          "申报单价": 100,
          "同商品编码平均单价": 80
        },
        "threshold": 1.2,
        "result": 1,
        "description": "计算申报单价与同商品编码平均单价的比值，判断是否大于等于阈值1.2，结果：满足条件"
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
          "商品编码对应标准重量上限"
        ],
        0
      ],
      [
        "ratio_operator",
        [
          "申报单价",
          "同商品编码平均单价"
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
  "semantic_description": "当申报重量（55）超过商品编码对应的标准重量上限（50），且申报单价（100）与同商品编码平均单价（80）的比值达到1.2及以上时，判定为**伪瞒报高危风险**。此类风险可能导致货物实际重量与申报不一致，存在隐瞒真实货物信息、虚报货量以逃避监管或获取非法利益的可能性，从而威胁运输安全、海关监管秩隐患，甚至可能造成环境污染或其他安全事故。\n\n对此，应立即触发人工查验，核实货物实际重量与申报一致性；同时开展许可证溯源核查，确认货物来源合法性；并对运输路径进行进一步核查，防止异常货物流入市场，确保供应链安全与合规性。",
  "summary": {
    "risk_indicator": 1,
    "risk_level": "高风险",
    "features_count": 4,
    "calculation_steps": 3
  }
}
```

**业务价值**

该案例针对报关单中 "商品编号（HS 编码）" 关联的重量监管标准和价格区间，通过双重校验识别两类高风险行为：一是超量申报（如实际重量 55kg 超过 HS 编码对应的 50kg 标准上限），可能涉及逃避许可证管理或虚报货物规模；二是价格异常偏高（如申报单价 100 元 /kg 远超同 HS 编码平均 80 元 /kg 的 1.2 倍阈值），可能存在虚假贸易套汇或骗取补贴的风险。
通过diff_operator（重量差值）与ratio_operator（价格比值）的组合校验，既能精准锁定超量申报的违规，又能捕捉价格异常的疑点，为海关 "风险布控" 提供数据支撑，减少人工审核的遗漏率，同时保障贸易数据的真实性与监管的精准性。


### 案例2：完税价格异常校验

**接口输入**

```bash
curl -X POST http://localhost:8000/explain_risk \
  -H "Content-Type: application/json" \
  -d '{
    "risk_features": {
      "申报币值": 1000,  
      "汇率": 6.9,  
      "系统计算完税价格": 6900,  
      "申报完税价格": 8000  
    },
    "rules": [
      ["ratio_operator", ["申报完税价格", "系统计算完税价格"], 1.1],  
      ["diff_operator", ["申报完税价格", "系统计算完税价格"], 500],  
      ["and_operator", [], null] 
    ]
  }'
```

**接口输出**

```json
{
  "multi_dimensional_structure": {
    "original_features": {
      "申报币值": 1000,
      "汇率": 6.9,
      "系统计算完税价格": 6900,
      "申报完税价格": 8000
    },
    "calculation_steps": [
      {
        "step": 1,
        "operator": "ratio_operator",
        "input_features": {
          "申报完税价格": 8000,
          "系统计算完税价格": 6900
        },
        "threshold": 1.1,
        "result": 1,
        "description": "计算申报完税价格与系统计算完税价格的比值，判断是否大于等于阈值1.1，结果：满足条件"
      },
      {
        "step": 2,
        "operator": "diff_operator",
        "input_features": {
          "申报完税价格": 8000,
          "系统计算完税价格": 6900
        },
        "threshold": 500,
        "result": 1,
        "description": "计算申报完税价格与系统计算完税价格的差值，判断是否大于等于阈值500，结果：满足条件"
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
        "ratio_operator",
        [
          "申报完税价格",
          "系统计算完税价格"
        ],
        1.1
      ],
      [
        "diff_operator",
        [
          "申报完税价格",
          "系统计算完税价格"
        ],
        500
      ],
      [
        "and_operator",
        [],
        null
      ]
    ]
  },
  "semantic_description": "当申报完税价格（8000）与系统计算完税价格（6900）的比值大于等于1.1且两者的差值大于等于500时，判定为**伪瞒报高危风险**。此类风险可能导致申报价格与实际价值存在显著差异，存在虚假申报、逃税或走私的可能性，进而威胁贸易安全与海关监管的有效性。\n\n该风险可能引发海关对货物的真实价值产生质。\n\n因此，需**立即触发人工查验**，对货物的实际状况、申报资料及运输路径进行核查，并开展**许可证溯源**与**运输路径核查**，以确保货物合法合规，防止潜在风险扩大。",
  "summary": {
    "risk_indicator": 1,
    "risk_level": "高风险",
    "features_count": 4,
    "calculation_steps": 3
  }
}
```

**应用价值**

该案例针对海关报关单中 "完税价格" 这一核心监管指标，通过校验企业申报的完税价格与系统按 "申报币值 × 汇率" 计算结果的一致性，可有效识别两类风险：一是企业通过虚增完税价格骗取出口退税，二是通过伪报币值或汇率操纵完税价格逃避监管。借助双重算子（比值 + 差值）的组合校验，既能捕捉比例异常（如超 10% 溢价），又能识别绝对金额异常（如差值超 500 元），为海关审价环节提供精准的风险指向，减少人工复核成本，保障税收征管准确性。

### 案例3：数量与税额匹配性核查

接口输入

```bash
curl -X POST http://localhost:8000/explain_risk \
  -H "Content-Type: application/json" \
  -d '{
    "risk_features": {
      "法定数量": 100,  
      "实际数量": 120,  
      "税率": 0.13,  
      "申报税额": 1300,  
      "系统计算税额": 1560  
    },
    "rules": [
      ["diff_operator", ["实际数量", "法定数量"], 10],  
      ["ratio_operator", ["系统计算税额", "申报税额"], 1.1], 
      ["and_operator", [], null] 
    ]
  }'
```

接口输出

```json
{
  "multi_dimensional_structure": {
    "original_features": {
      "法定数量": 100,
      "实际数量": 120,
      "税率": 0.13,
      "申报税额": 1300,
      "系统计算税额": 1560
    },
    "calculation_steps": [
      {
        "step": 1,
        "operator": "diff_operator",
        "input_features": {
          "实际数量": 120,
          "法定数量": 100
        },
        "threshold": 10,
        "result": 1,
        "description": "计算实际数量与法定数量的差值，判断是否大于等于阈值10，结果：满足条件"
      },
      {
        "step": 2,
        "operator": "ratio_operator",
        "input_features": {
          "系统计算税额": 1560,
          "申报税额": 1300
        },
        "threshold": 1.1,
        "result": 1,
        "description": "计算系统计算税额与申报税额的比值，判断是否大于等于阈值1.1，结果：满足条件"
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
          "实际数量",
          "法定数量"
        ],
        10
      ],
      [
        "ratio_operator",
        [
          "系统计算税额",
          "申报税额"
        ],
        1.1
      ],
      [
        "and_operator",
        [],
        null
      ]
    ]
  },
  "semantic_description": "当实际数量（120）超过法定数量（100）且差值达到或超过阈值10，同时系统计算税额（1560）与申报税额（1300）的比值达到或超过阈值1.1时，判定为**伪瞒报高危风险**。此类风险可能导致**货物实际数量与申报不一致，存在虚报或隐瞒真实数量的可能性，可能引发走私、逃税、监管漏洞等问题，严重时会影响运量；开展许可证溯源核查，确认合法来源；对运输路径进行重点检查，防止非法转移或隐藏货物**。",
  "summary": {
    "risk_indicator": 1,
    "risk_level": "高风险",
    "features_count": 5,
    "calculation_steps": 3
  }
}    
```

**应用价值**

该案例聚焦报关单中 "法定数量" 与 "应征税额" 的关联性，通过比对实际查验数量与申报数量的差异、系统计算税额与申报税额的比例，可精准识别企业少报数量（如实际多装货物）或低报税额（如隐瞒部分应税金额）的违规行为。在海关实际监管中，数量与税额的不匹配往往是走私、偷逃税的典型特征，该案例通过双重算子校验，能提前锁定高风险报关单，提升查验针对性，减少国家税收流失，同时规范贸易秩序。

### 案例4：报关单单价与总价匹配性校验

**接口输入**

```bash
curl -X POST http://localhost:8000/explain_risk \
  -H "Content-Type: application/json" \
  -d '{
    "risk_features": {
      "关税税率": 0.1,  
      "增值税税率": 0.13,  
      "消费税税率": 0.05,  
      "完税价格": 10000,  
      "申报关税税额": 800, 
      "申报增值税税额": 1200  
    },
    "rules": [
      ["mul_operator", ["完税价格", "关税税率"], 900], 
      ["ratio_operator", ["申报增值税税额", "申报关税税额"], 1.4], 
      ["and_operator", [], null]  
    ]
  }'
```

**接口输出**

```json
{
  "multi_dimensional_structure": {
    "original_features": {
      "关税税率": 0.1,
      "增值税税率": 0.13,
      "消费税税率": 0.05,
      "完税价格": 10000,
      "申报关税税额": 800,
      "申报增值税税额": 1200
    },
    "calculation_steps": [
      {
        "step": 1,
        "operator": "mul_operator",
        "input_features": {
          "完税价格": 10000,
          "关税税率": 0.1
        },
        "threshold": 900,
        "result": 1,
        "description": "应用mul_operator算子，结果：满足条件"
      },
      {
        "step": 2,
        "operator": "ratio_operator",
        "input_features": {
          "申报增值税税额": 1200,
          "申报关税税额": 800
        },
        "threshold": 1.4,
        "result": 1,
        "description": "计算申报增值税税额与申报关税税额的比值，判断是否大于等于阈值1.4，结果：满足条件"
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
        "mul_operator",
        [
          "完税价格",
          "关税税率"
        ],
        900
      ],
      [
        "ratio_operator",
        [
          "申报增值税税额",
          "申报关税税额"
        ],
        1.4
      ],
      [
        "and_operator",
        [],
        null
      ]
    ]
  },
  "semantic_description": "当**申报增值税税额与申报关税税额的比值大于等于1.4**且**所有计算条件均满足**时，判定为**伪瞒报高危风险**。此类风险可能导致**企业通过虚报货物价值来降低实际应缴税款，从而逃避监管、扰乱正常贸易秩序，甚至引发走私或税务欺诈行为**，对**贸易安全、税收征管及运输合规性**构成严重威胁。\n\n需源**，确认进出口资质是否齐全有效；并对**运输路径进行核查**，排查是否存在非法转运或绕关行为，确保货物真实性和合规性。",
  "summary": {
    "risk_indicator": 1,
    "risk_level": "高风险",
    "features_count": 6,
    "calculation_steps": 3
  }
}
```

**业务价值**

该案例运用乘法算子、比值算子和差分比率算子，针对报关单中价格相关核心数据进行多维校验。通过计算申报单价与法定数量的乘积（应等于申报总价，若偏差超 500 元）、申报总价与同商品编号平均总价的比值（超 1.2 倍）及两者的差分比率（超 0.15），可精准识别企业通过拆分申报、虚增数量等方式操纵价格的风险。此类校验能有效防范企业利用价格差异偷逃税款或虚报贸易规模，为海关价格核查提供量化风险依据，既保障国家税收安全，又维护规范的贸易计价秩序。

## 参考资料
《基于“物-事-证”的多维特征提取与描述算法研究报告》