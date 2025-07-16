#!/bin/bash

echo "================================================"
echo "风险检测API测试脚本"
echo "================================================"
echo

# 检查服务是否运行
echo "检查服务健康状态..."
health_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$health_response" != "200" ]; then
    echo "❌ 服务未运行或无法访问，请先启动服务: python app.py"
    exit 1
fi
echo "✅ 服务运行正常"
echo

echo "================================================"
echo "测试案例1: 申报重量和价格双重异常 (curl命令)"
echo "================================================"
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
  }' | python -m json.tool

echo
echo "================================================"
echo "运行Python测试脚本 (包含3个测试案例)"
echo "================================================"
python test_cases.py

echo
echo "================================================"
echo "所有测试完成！"
echo "================================================"
