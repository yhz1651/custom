# 海关算子
By [@yhz1651](https://github.com/yhz1651)

## 项目简介
海关算子用于从指标系统的单维原始指标中提取多维特征，通过预设运算规则对申报信息（如重量、价格等核心指标）进行结构化分析，最终输出包含分步计算逻辑的多维特征结构，以及由大模型生成的语义化风险描述。

该工具可将分散的单维数据转化为可解释的风险判断依据，清晰呈现风险触发的计算链路与逻辑关系，为海关等场景的风险核查提供直观、可追溯的决策支持。

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
接口输出示例

`multi_dimensional_structure`：包含原始特征、分步计算过程、中间结果及最终风险指标，清晰展示规则运算逻辑；

`semantic_description`：用自然语言解释风险判定依据、潜在影响及处理建议；

`summary`：风险结果摘要，快速呈现核心结论。

### 案例1

**接口输入**

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

**接口输出**

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
### 案例2

**接口输入**

```bash
curl -X POST http://localhost:8000/explain_risk \
  -H "Content-Type: application/json" \
  -d '{
    "risk_features": {
      "申报数量": 1000, "历史平均数量": 500, "申报体积": 2.5, 
      "标准体积": 1.8, "申报频次": 15, "正常频次": 8
    },
    "rules": [
      ["ratio_operator", ["申报数量", "历史平均数量"], 1.5],
      ["ratio_operator", ["申报体积", "标准体积"], 1.3],
      ["ratio_operator", ["申报频次", "正常频次"], 1.5],
      ["and3_operator", [], null]
    ]
  }'
```

**接口输出**

```json
{
  "multi_dimensional_structure": {
    "original_features": {
      "申报数量": 1000,
      "历史平均数量": 500,
      "申报体积": 2.5,
      "标准体积": 1.8,
      "申报频次": 15,
      "正常频次": 8
    },
    "calculation_steps": [
      {
        "step": 1,
        "operator": "ratio_operator",
        "input_features": {
          "申报数量": 1000,
          "历史平均数量": 500
        },
        "threshold": 1.5,
        "result": 1,
        "description": "计算申报数量与历史平均数量的比值，判断是否大于等于阈值1.5，结果：满足条件"
      },
      {
        "step": 2,
        "operator": "ratio_operator",
        "input_features": {
          "申报体积": 2.5,
          "标准体积": 1.8
        },
        "threshold": 1.3,
        "result": 1,
        "description": "计算申报体积与标准体积的比值，判断是否大于等于阈值1.3，结果：满足条件"
      },
      {
        "step": 3,
        "operator": "ratio_operator",
        "input_features": {
          "申报频次": 15,
          "正常频次": 8
        },
        "threshold": 1.5,
        "result": 1,
        "description": "计算申报频次与正常频次的比值，判断是否大于等于阈值1.5，结果：满足条件"
      },
      {
        "step": 4,
        "operator": "and3_operator",
        "input_results": [
          1,
          1,
          1
        ],
        "result": 1,
        "description": "三元逻辑与运算：所有三个条件([1, 1, 1])均需满足，最终判定：触发风险"
      }
    ],
    "intermediate_results": [
      1,
      1,
      1
    ],
    "final_risk_indicator": 1,
    "rules_applied": [
      [
        "ratio_operator",
        [
          "申报数量",
          "历史平均数量"
        ],
        1.5
      ],
      [
        "ratio_operator",
        [
          "申报体积",
          "标准体积"
        ],
        1.3
      ],
      [
        "ratio_operator",
        [
          "申报频次",
          "正常频次"
        ],
        1.5
      ],
      [
        "and3_operator",
        [],
        null
      ]
    ]
  },
  "semantic_description": "当申报数量为1000，较历史平均数量500增长1.5倍；申报体积为2.5，超出标准体积1.8的1.3倍以上；申报频次为15，超过正常频次8的1.5倍以上时，判定为**伪瞒报高危风险**。此类风险可能导致**货物实际数量或体积与申报数输路径进行重点核查，确保申报信息真实准确，防止非法行为发生**。",
  "summary": {
    "risk_indicator": 1,
    "risk_level": "高风险",
    "features_count": 6,
    "calculation_steps": 4
  }
}
```
### 案例3

接口输入

```bash
curl -X POST http://localhost:8000/explain_risk \
  -H "Content-Type: application/json" \
  -d '{
    "risk_features": {
      "当前温度": -15.5, "标准温度": -18.0, "温度变化率": 0.8,
      "安全变化率": 0.5, "湿度偏差": 12.0, "湿度阈值": 10.0
    },
    "rules": [
      ["diff_operator", ["当前温度", "标准温度"], 2.0],
      ["cmp_operator", ["温度变化率", "安全变化率"], null],
      ["cmp_operator", ["湿度偏差", "湿度阈值"], null],
      ["or3_operator", [], null]
    ]
  }'
```

接口输出

```json
{
  "multi_dimensional_structure": {
    "original_features": {
      "当前温度": -15.5,
      "标准温度": -18.0,
      "温度变化率": 0.8,
      "安全变化率": 0.5,
      "湿度偏差": 12.0,
      "湿度阈值": 10.0
    },
    "calculation_steps": [
      {
        "step": 1,
        "operator": "diff_operator",
        "input_features": {
          "当前温度": -15.5,
          "标准温度": -18.0
        },
        "threshold": 2.0,
        "result": 1,
        "description": "计算当前温度与标准温度的差值，判断是否大于等于阈值2.0，结果：满足条件"
      },
      {
        "step": 2,
        "operator": "cmp_operator",
        "input_features": {
          "温度变化率": 0.8,
          "安全变化率": 0.5
        },
        "threshold": null,
        "result": 1,
        "description": "比较温度变化率与安全变化率的大小，判断温度变化率是否大于等于安全变化率，结果：满足条件"
      },
      {
        "step": 3,
        "operator": "cmp_operator",
        "input_features": {
          "湿度偏差": 12.0,
          "湿度阈值": 10.0
        },
        "threshold": null,
        "result": 1,
        "description": "比较湿度偏差与湿度阈值的大小，判断湿度偏差是否大于等于湿度阈值，结果：满足条件"
      },
      {
        "step": 4,
        "operator": "or3_operator",
        "input_results": [
          1,
          1,
          1
        ],
        "result": 1,
        "description": "三元逻辑或运算：任一条件([1, 1, 1])满足即可，最终判定：触发风险"
      }
    ],
    "intermediate_results": [
      1,
      1,
      1
    ],
    "final_risk_indicator": 1,
    "rules_applied": [
      [
        "diff_operator",
        [
          "当前温度",
          "标准温度"
        ],
        2.0
      ],
      [
        "cmp_operator",
        [
          "温度变化率",
          "安全变化率"
        ],
        null
      ],
      [
        "cmp_operator",
        [
          "湿度偏差",
          "湿度阈值"
        ],
        null
      ],
      [
        "or3_operator",
        [],
        null
      ]
    ]
  },
  "semantic_description": "当当前温度（-15.5℃）高于标准温度（-18.0℃）2.0℃以上，且温度变化率（0.8）大于等于安全变化率（0.5），同时湿度偏差（12.0%）超过湿度阈值（10.0%）时，判定为**伪瞒报高危风险**。此类风险可能导致运输过程中因温关许可证信息，确保运输路径与存储条件符合规范要求**。",
  "summary": {
    "risk_indicator": 1,
    "risk_level": "高风险",
    "features_count": 6,
    "calculation_steps": 4
  }
}               
```

## 风险检测API测试案例说明

本文档描述了风险检测API的三个测试案例，每个案例展示了不同的风险检测场景和算子组合。

### 案例概览

| 案例 | 场景 | 算子类型 | 逻辑组合 | 预期结果 |
|------|------|----------|----------|----------|
| 案例1 | 申报重量和价格双重异常 | diff_operator + ratio_operator | and_operator | 高风险 |
| 案例2 | 货物申报三维异常检测 | 三个ratio_operator | and3_operator | 高风险 |
| 案例3 | 冷链运输温度异常监控 | diff_operator + 两个cmp_operator | or3_operator | 高风险 |

## 详细案例说明

### 案例1: 申报重量和价格双重异常

**场景描述**: 检测货物申报中的重量超限和价格异常情况

**输入特征**:
- 申报重量: 55kg
- 限重: 50kg  
- 申报价格: 100元
- 参考价格: 80元

**检测规则**:
1. `diff_operator`: 申报重量 - 限重 ≥ 0 (检查是否超重)
2. `ratio_operator`: 申报价格/参考价格 ≥ 1.2 (检查价格是否异常偏高)
3. `and_operator`: 两个条件都满足才触发风险

**计算过程**:
- 重量差值: 55 - 50 = 5 ≥ 0 → 满足条件 (1)
- 价格比值: 100/80 = 1.25 ≥ 1.2 → 满足条件 (1)  
- 逻辑与: 1 AND 1 = 1 → 触发风险

**风险类型**: 申报重量超限且价格异常的复合风险

### 案例2: 货物申报三维异常检测

**场景描述**: 检测货物申报中数量、体积、频次的三维异常模式

**输入特征**:
- 申报数量: 1000件
- 历史平均数量: 500件
- 申报体积: 2.5m³
- 标准体积: 1.8m³
- 申报频次: 15次/月
- 正常频次: 8次/月

**检测规则**:
1. `ratio_operator`: 申报数量/历史平均数量 ≥ 1.5
2. `ratio_operator`: 申报体积/标准体积 ≥ 1.3  
3. `ratio_operator`: 申报频次/正常频次 ≥ 1.5
4. `and3_operator`: 三个条件都满足才触发风险

**计算过程**:
- 数量比值: 1000/500 = 2.0 ≥ 1.5 → 满足条件 (1)
- 体积比值: 2.5/1.8 = 1.39 ≥ 1.3 → 满足条件 (1)
- 频次比值: 15/8 = 1.875 ≥ 1.5 → 满足条件 (1)
- 三元逻辑与: 1 AND 1 AND 1 = 1 → 触发风险

**风险类型**: 货物申报三维指标全面异常的高危风险

### 案例3: 冷链运输温度异常监控

**场景描述**: 检测冷链运输过程中的温度、湿度异常情况

**输入特征**:
- 当前温度: -15.5°C
- 标准温度: -18.0°C
- 温度变化率: 0.8°C/小时
- 安全变化率: 0.5°C/小时
- 湿度偏差: 12.0%
- 湿度阈值: 10.0%

**检测规则**:
1. `diff_operator`: 当前温度 - 标准温度 ≥ 2.0 (检查温度偏差)
2. `cmp_operator`: 温度变化率 ≥ 安全变化率 (检查变化率)
3. `cmp_operator`: 湿度偏差 ≥ 湿度阈值 (检查湿度)
4. `or3_operator`: 任一条件满足就触发风险

**计算过程**:
- 温度差值: -15.5 - (-18.0) = 2.5 ≥ 2.0 → 满足条件 (1)
- 变化率比较: 0.8 ≥ 0.5 → 满足条件 (1)
- 湿度比较: 12.0 ≥ 10.0 → 满足条件 (1)
- 三元逻辑或: 1 OR 1 OR 1 = 1 → 触发风险

**风险类型**: 冷链运输环境控制异常风险