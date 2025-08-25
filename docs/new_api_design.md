# 新 API 设计说明

## 🔄 API 设计变更

### 主要变更

1. **请求方法**: POST → GET
2. **私钥获取**: 请求参数 → 环境变量
3. **必需参数**: 仅 `nft_token_id`
4. **默认行为**: `order_type` 默认为 `market`

## 📋 新 API 接口

### 1. 创建订单

**GET** `/api/v1/order`

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `nft_token_id` | string | ✅ | - | NFT 代币ID |
| `order_type` | string | ❌ | `market` | 订单类型：`market` 或 `limit` |
| `amount` | number | ❌ | - | 代币数量（限价单时必需） |
| `confirm_real_order` | boolean | ❌ | `false` | 安全确认参数 |
| `rpc_url` | string | ❌ | - | 自定义 RPC URL |
| `use_proxy` | boolean | ❌ | - | 是否使用代理 |
| `timeout` | integer | ❌ | - | 请求超时时间 |

#### 使用示例

```bash
# 市价单（最简形式）
GET /api/v1/order?nft_token_id=123&confirm_real_order=true

# 限价单
GET /api/v1/order?nft_token_id=123&order_type=limit&amount=1.5&confirm_real_order=true
```

### 2. 获取价格

**GET** `/api/v1/price/{nft_token_id}`

#### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `nft_token_id` | string | ✅ | NFT 代币ID（路径参数） |

#### 使用示例

```bash
GET /api/v1/price/8279886802876316306180221210882
```

## 🔧 环境变量配置

### 必需环境变量

```env
PRIVATE_KEY=your_private_key_here
```

### 可选环境变量

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

## 🎯 业务逻辑

### 市价单流程

1. 接收 `nft_token_id` 参数
2. 从环境变量获取 `private_key`
3. 自动获取当前市场价格作为 `token_amount`
4. 创建并提交市价单

### 限价单流程

1. 接收 `nft_token_id` 和 `amount` 参数
2. 从环境变量获取 `private_key`
3. 使用用户提供的 `amount` 作为订单数量
4. 创建并提交限价单

## ✅ 优势

### 1. **简化调用**
- 只需要一个必需参数 `nft_token_id`
- GET 请求更适合简单的操作
- 减少了客户端的复杂性

### 2. **安全性提升**
- 私钥不在请求中传输
- 环境变量管理更安全
- 减少了敏感信息泄露风险

### 3. **易于使用**
- 可以直接在浏览器中测试
- cURL 命令更简洁
- 支持 URL 参数形式

### 4. **默认行为合理**
- 市价单是最常用的操作
- 减少了必需参数的数量
- 提供了合理的默认值

## 🔒 安全机制

### 1. **强制确认**
```bash
# ❌ 错误：缺少确认参数
GET /api/v1/order?nft_token_id=123

# ✅ 正确：包含确认参数
GET /api/v1/order?nft_token_id=123&confirm_real_order=true
```

### 2. **参数验证**
```bash
# ❌ 错误：限价单缺少 amount
GET /api/v1/order?nft_token_id=123&order_type=limit&confirm_real_order=true

# ✅ 正确：限价单包含 amount
GET /api/v1/order?nft_token_id=123&order_type=limit&amount=1.5&confirm_real_order=true
```

### 3. **环境变量检查**
- 服务启动时检查 `PRIVATE_KEY` 是否存在
- 请求时验证私钥配置
- 提供清晰的错误信息

## 📊 响应格式

### 成功响应
```json
{
  "success": true,
  "message": "订单创建成功",
  "order_id": "order_123",
  "transaction_hash": "0x...",
  "order_data": {...}
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE"
}
```

## 🧪 测试方法

### 1. 浏览器测试
直接在浏览器地址栏输入：
```
http://localhost:8000/api/v1/price/8279886802876316306180221210882
```

### 2. cURL 测试
```bash
# 获取价格
curl "http://localhost:8000/api/v1/price/8279886802876316306180221210882"

# 创建市价单（测试）
curl "http://localhost:8000/api/v1/order?nft_token_id=8279886802876316306180221210882&confirm_real_order=false"
```

### 3. Python 测试
```python
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # 获取价格
        response = await client.get("http://localhost:8000/api/v1/price/123")
        print(response.json())
        
        # 创建订单
        params = {"nft_token_id": "123", "confirm_real_order": True}
        response = await client.get("http://localhost:8000/api/v1/order", params=params)
        print(response.json())

asyncio.run(test_api())
```

## 🔄 迁移指南

### 从旧 API 迁移

#### 旧 API (POST)
```python
order_data = {
    "nft_token_id": "123",
    "order_type": "market",
    "private_key": "your_key",
    "confirm_real_order": True
}
response = await client.post("/api/v1/order", json=order_data)
```

#### 新 API (GET)
```python
params = {
    "nft_token_id": "123",
    "confirm_real_order": True
}
response = await client.get("/api/v1/order", params=params)
```

### 环境变量设置
```bash
# 设置环境变量
export PRIVATE_KEY=your_private_key_here

# 或在 .env 文件中
echo "PRIVATE_KEY=your_private_key_here" >> .env
```

## 🎉 总结

新的 API 设计更加简洁、安全和易用：

- ✅ **更简单**: 只需一个必需参数
- ✅ **更安全**: 私钥通过环境变量管理
- ✅ **更直观**: GET 请求符合 RESTful 规范
- ✅ **更灵活**: 支持默认行为和自定义参数
- ✅ **更易测试**: 可以直接在浏览器中使用

这种设计更适合生产环境的使用，同时保持了所有原有的功能和安全机制。