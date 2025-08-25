# FastAPI 订单服务使用指南

## 概述

这是一个基于 FastAPI 的异步订单服务，提供市价单和限价单的创建功能。服务封装了原有的 `OrderService` 类，提供了 RESTful API 接口。

## 架构设计

```
app/
├── __init__.py
├── main.py                    # FastAPI 应用入口
├── core/
│   ├── __init__.py
│   └── config.py             # 应用配置
├── models/
│   ├── __init__.py
│   └── order.py              # 数据模型
├── services/
│   ├── __init__.py
│   └── order_service_wrapper.py  # 订单服务包装器
└── api/
    ├── __init__.py
    └── v1/
        ├── __init__.py
        ├── order.py          # 订单 API 路由
        └── health.py         # 健康检查路由
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境配置

创建 `.env` 文件：

```env
# 应用配置
DEBUG=false
HOST=0.0.0.0
PORT=8000

# 区块链配置
RPC_URL=https://mainnet.base.org

# 请求配置
REQUEST_TIMEOUT=15
USE_PROXY=true
PROXY_FILE=proxies.txt

# 安全配置
REQUIRE_CONFIRMATION=true
```

## 启动服务

### 方式一：使用启动脚本
```bash
python run_server.py
```

### 方式二：直接运行
```bash
python -m app.main
```

### 方式三：使用 uvicorn
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API 接口

### 1. 健康检查

**GET** `/api/v1/health`

响应示例：
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. 创建订单

**POST** `/api/v1/order`

请求体：
```json
{
  "nft_token_id": "8279886802876316306180221210882",
  "order_type": "market",
  "private_key": "your_private_key_here",
  "amount": 10,
  "confirm_real_order": true
}
```

参数说明：
- `nft_token_id`: NFT 代币ID（必需）
- `order_type`: 订单类型，`market`（市价单）或 `limit`（限价单）
- `private_key`: 私钥（必需）
- `amount`: 代币数量，会自动转换为 wei 单位
- `token_amount`: 已经是 wei 单位的精确数量
- `confirm_real_order`: 安全确认参数，必须为 `true`

响应示例：
```json
{
  "success": true,
  "message": "订单创建成功",
  "order_id": "order_123",
  "transaction_hash": "0x...",
  "order_data": {...}
}
```

### 3. 获取商品价格

**GET** `/api/v1/price/{nft_token_id}?private_key=your_key`

响应示例：
```json
{
  "success": true,
  "price_wei": "1000000000000000000",
  "nft_token_id": "8279886802876316306180221210882"
}
```

## 使用示例

### Python 客户端示例

```python
import httpx
import asyncio

async def create_market_order():
    order_data = {
        "nft_token_id": "8279886802876316306180221210882",
        "order_type": "market",
        "private_key": "your_private_key_here",
        "amount": 10,
        "confirm_real_order": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/order",
            json=order_data
        )
        return response.json()

# 运行示例
result = asyncio.run(create_market_order())
print(result)
```

### cURL 示例

```bash
# 创建市价单
curl -X POST "http://localhost:8000/api/v1/order" \
  -H "Content-Type: application/json" \
  -d '{
    "nft_token_id": "8279886802876316306180221210882",
    "order_type": "market",
    "private_key": "your_private_key_here",
    "amount": 10,
    "confirm_real_order": true
  }'

# 获取价格
curl "http://localhost:8000/api/v1/price/8279886802876316306180221210882?private_key=your_key"
```

## 安全特性

### 1. 强制确认机制
所有真实订单都必须设置 `confirm_real_order=true`，防止测试过程中的意外下单。

### 2. 参数验证
使用 Pydantic 模型进行严格的参数验证，确保数据格式正确。

### 3. 错误处理
提供详细的错误信息和错误代码，便于调试和处理。

### 4. 服务实例缓存
对于相同私钥的请求，会复用服务实例，提高性能。

## 错误代码

| 错误代码 | 说明 |
|---------|------|
| `INVALID_PARAMETERS` | 请求参数错误 |
| `SECURITY_CHECK_FAILED` | 安全检查失败 |
| `AUTHENTICATION_REQUIRED` | 需要认证 |
| `RATE_LIMITED` | 请求频率限制 |
| `REQUEST_BLOCKED` | 请求被封禁 |
| `ITEM_NOT_FOR_SALE` | 商品不在售 |
| `UNSUPPORTED_ORDER_TYPE` | 不支持的订单类型 |
| `ORDER_CREATION_FAILED` | 订单创建失败 |
| `INTERNAL_SERVER_ERROR` | 服务器内部错误 |

## 测试

### 运行测试
```bash
pytest tests/
```

### 运行示例
```bash
python examples/api_usage_example.py
```

## API 文档

启动服务后，可以访问以下地址查看自动生成的 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 注意事项

1. **真实订单确认**: 所有真实订单都需要设置 `confirm_real_order=true`
2. **私钥安全**: 请妥善保管私钥，不要在日志中暴露
3. **代理配置**: 如果使用代理，请确保 `proxies.txt` 文件配置正确
4. **环境变量**: 敏感信息请通过环境变量配置，不要硬编码在代码中
5. **错误处理**: 请根据返回的错误代码进行相应的错误处理

## 生产部署建议

1. 使用 HTTPS
2. 配置适当的 CORS 策略
3. 添加请求频率限制
4. 配置日志记录
5. 使用负载均衡
6. 监控服务健康状态