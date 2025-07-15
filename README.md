# 海关算子

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

