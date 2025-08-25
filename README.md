# 订单服务

一个支持市价单和限价单交易的多语言工具包，提供 Python 原生库和 FastAPI Web 服务两种使用方式。

## 🚀 快速开始

### FastAPI Web 服务（推荐）

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python run_server.py

# 访问 API 文档
open http://localhost:8000/docs
```

### Python 原生库

```python
from order_service import OrderService

service = OrderService(private_key)
await service.init()
await service.login()
await service.place_market_order(params, confirm_real_order=True)
```

## 功能特性

- ✅ 自动登录认证和会话管理
- ✅ 市价单和限价单支持
- ✅ EIP-712 订单签名
- ✅ 自动费率和用户信息获取
- ✅ 批量下单支持
- 🆕 **策略模式请求系统** - 支持 CycleTLS 和 Puppeteer 策略
- 🆕 **智能反爬虫绕过** - 自动切换策略应对不同级别的检测
- 🆕 **Cloudflare 绕过支持** - 使用真实浏览器环境
- 🆕 **自动 Cookie 管理** - CYCLETLS 策略自动提取和管理认证 cookies

## 安装

```bash
npm install
```

## 配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 设置你的私钥：
```env
PRIVATE_KEY=your_private_key_here
RPC_URL=https://mainnet.base.org
```

## 使用方法

### 快速开始

```javascript
const { placeMarketOrder, placeLimitOrder } = require('./order-service');

// 市价单
const marketResult = await placeMarketOrder(privateKey, {
    tokenId: 'your-token-id',
    usdcAmount: 1000000, // 1 USDC
    side: 0, // 0=买，1=卖
    marketSlug: 'your-market-slug'
});

// 限价单
const limitResult = await placeLimitOrder(privateKey, {
    tokenId: 'your-token-id',
    price: 0.1, // 单价（美元）
    quantity: 10, // 数量
    side: 0, // 0=买，1=卖
    marketSlug: 'your-market-slug'
});
```

### 使用 OrderService 类

```javascript
import OrderService from './order-service.js';
import RequestStrategyFactory from './src/request-strategies/strategy-factory.js';

// 使用默认的 CycleTLS 策略
const orderService = new OrderService(privateKey);

// 或者明确指定策略
const orderService = new OrderService(privateKey, {
    strategy: RequestStrategyFactory.STRATEGIES.CYCLETLS, // 或 PUPPETEER
    timeout: 15000
});

await orderService.init();

// 下市价单
await orderService.placeMarketOrder({
    tokenId: 'your-token-id',
    usdcAmount: 1000000,
    side: 0,
    marketSlug: 'your-market-slug'
});

// 下限价单
await orderService.placeLimitOrder({
    tokenId: 'your-token-id',
    price: 0.15,
    quantity: 5,
    side: 0,
    marketSlug: 'your-market-slug'
});

// 获取活跃订单
const ordersResult = await orderService.getActiveOrders();
orderService.formatOrderInfo(ordersResult.orders);

// 获取投资组合信息
const portfolioResult = await orderService.getPortfolioPositions();
```

### 查询功能

```javascript
const { getActiveOrders, getPortfolioPositions } = require('./order-service');

// 获取活跃订单
const ordersResult = await getActiveOrders(privateKey);
console.log(`找到 ${ordersResult.totalOrders} 个活跃订单`);

// 获取投资组合信息
const portfolioResult = await getPortfolioPositions(privateKey);
console.log('用户积分:', portfolioResult.data.points);
```

## 运行示例

```bash
# 下单示例
npm run market     # 市价单示例
npm run limit      # 限价单示例
npm run example    # 运行所有下单示例

# 查询示例
npm run orders     # 获取活跃订单
npm run portfolio  # 获取投资组合信息
npm run monitor    # 监控订单状态变化

# 策略模式示例
npm run test-strategies  # 测试请求策略
npm run demo-strategies  # 策略切换演示
npm run usage-example    # 实际使用示例
```

## 请求策略

本项目支持两种请求策略来应对不同级别的反爬虫检测：

### CycleTLS 策略（默认）
- **优点**: 速度快，资源消耗少
- **适用**: 基本的反爬虫检测
- **使用场景**: 大部分正常请求

### Puppeteer 策略
- **优点**: 真实浏览器环境，绕过能力强
- **适用**: 高级反爬虫检测（如 Cloudflare）
- **使用场景**: CycleTLS 失败时的备选方案

### 自动策略切换

```javascript
// 创建具有自动回退的服务
const orderService = new OrderService(privateKey);
await orderService.init();

try {
    await orderService.getLoginMessage();
} catch (error) {
    // 自动切换到 Puppeteer 策略
    await orderService.switchStrategy(
        RequestStrategyFactory.STRATEGIES.PUPPETEER,
        { headless: true, turnstile: true }
    );
    await orderService.getLoginMessage(); // 重试
}
```

详细的策略使用指南请参考 [策略模式文档](docs/strategy-pattern-guide.md)。

## Cookie 管理

CYCLETLS 策略支持自动管理认证 cookies，特别是 MSU.io 平台所需的 `wat` 和 `wrt` tokens：

### 自动 Cookie 管理

```javascript
import OrderService from './order-service.js';

const orderService = new OrderService(privateKey, {
    strategy: RequestStrategyFactory.STRATEGIES.CYCLETLS
});

await orderService.init();

// 登录会自动提取 wat 和 wrt cookies，并映射为 msu_wat 和 msu_wrt
await orderService.login();

// 后续请求会自动携带这些认证 cookies
await orderService.placeLimitOrder({...});
```

### 手动 Cookie 管理

```javascript
// 获取当前存储的 cookies
const cookies = orderService.getAuthCookies();
console.log('认证 cookies:', cookies);

// 手动设置 cookies（用于会话恢复）
orderService.setAuthCookies({
    'msu_wat': 'your_wat_token',
    'msu_wrt': 'your_wrt_token'
});

// 清除所有 cookies
orderService.clearAuthCookies();
```

### Cookie 管理工具

项目提供了命令行工具来管理认证 cookies：

```bash
# 显示当前 cookies 状态
node tools/cookie-manager.js status

# 执行登录并保存 cookies
node tools/cookie-manager.js login

# 从文件恢复 cookies
node tools/cookie-manager.js restore

# 清除所有 cookies
node tools/cookie-manager.js clear
```

详细的 Cookie 管理指南请参考 [Cookie 管理文档](docs/cycletls-cookie-management.md)。

## 参数说明

### 市价单参数
- `tokenId`: 代币ID
- `usdcAmount`: USDC金额（微单位，1 USDC = 1000000）
- `side`: 买卖方向（0=买，1=卖）
- `marketSlug`: 市场标识符

### 限价单参数
- `tokenId`: 代币ID
- `price`: 单价（美元）
- `quantity`: 数量
- `side`: 买卖方向（0=买，1=卖）
- `marketSlug`: 市场标识符

## 合约信息

- **合约地址**: `0xa4409d988ca2218d956beefd3874100f444f0dc3`
- **网络**: Base (Chain ID: 8453)
- **EIP-712 域名**: `Limitless CTF Exchange`

## 🌐 FastAPI Web 服务

### 特性

- ✅ **RESTful API**: 标准的 HTTP 接口，支持任何编程语言调用
- ✅ **异步处理**: 基于 FastAPI 的高性能异步服务
- ✅ **自动文档**: Swagger UI 和 ReDoc 自动生成的 API 文档
- ✅ **数据验证**: Pydantic 模型确保请求数据的正确性
- ✅ **安全机制**: 强制确认参数防止意外下单
- ✅ **错误处理**: 详细的错误信息和状态码
- ✅ **服务缓存**: 智能的服务实例缓存提高性能

### API 接口

#### 创建订单
```http
GET /api/v1/order?nft_token_id=8279886802876316306180221210882&confirm_real_order=true

# 市价单（默认）
GET /api/v1/order?nft_token_id=8279886802876316306180221210882&confirm_real_order=true

# 限价单
GET /api/v1/order?nft_token_id=8279886802876316306180221210882&order_type=limit&amount=1.5&confirm_real_order=true
```

#### 获取价格
```http
GET /api/v1/price/{nft_token_id}
```

#### 健康检查
```http
GET /api/v1/health
```

### 使用示例

#### Python 客户端
```python
import httpx
import asyncio

async def create_market_order():
    params = {
        "nft_token_id": "8279886802876316306180221210882",
        "confirm_real_order": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/order",
            params=params
        )
        return response.json()

async def create_limit_order():
    params = {
        "nft_token_id": "8279886802876316306180221210882",
        "order_type": "limit",
        "amount": 1.5,
        "confirm_real_order": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/order",
            params=params
        )
        return response.json()

# 使用示例
market_result = asyncio.run(create_market_order())
limit_result = asyncio.run(create_limit_order())
```

#### cURL 示例
```bash
# 市价单
curl "http://localhost:8000/api/v1/order?nft_token_id=8279886802876316306180221210882&confirm_real_order=true"

# 限价单
curl "http://localhost:8000/api/v1/order?nft_token_id=8279886802876316306180221210882&order_type=limit&amount=1.5&confirm_real_order=true"

# 获取价格
curl "http://localhost:8000/api/v1/price/8279886802876316306180221210882"
```

### 部署

#### Docker 部署
```bash
# 构建镜像
docker build -t order-service .

# 运行容器
docker run -p 8000:8000 --env-file .env order-service
```

#### Docker Compose
```bash
docker-compose up -d
```

### 文档

- 📚 [FastAPI 使用指南](docs/fastapi_usage.md)
- 🏗️ [项目结构说明](docs/project_structure.md)
- 🔧 [API 示例代码](examples/api_usage_example.py)
- 🐍 [Python 原生库示例](examples/python_usage_example.py)
- 🚀 [快速启动演示](quick_start.py)

## 🐍 Python 原生库

原有的 Python 订单服务库，提供完整的订单管理功能。

### 安装和使用

```python
# 方式1: 向后兼容导入（推荐）
from order_service import OrderService

# 方式2: 直接从核心模块导入
from app.core.order_service import OrderService

# 创建服务实例
service = OrderService(private_key)
await service.init()

# 登录认证
await service.login()

# 下市价单
await service.place_market_order({
    'nft_token_id': 'your_token_id',
    'amount': 10
}, confirm_real_order=True)

# 下限价单
await service.place_limit_order({
    'nft_token_id': 'your_token_id',
    'token_amount': '1000000000000000000'
}, confirm_real_order=True)
```

## 🛠️ 开发工具

### 项目清理
```bash
# 清理缓存文件、日志文件和临时文件
python3 tools/cleanup.py

# 验证核心模块导入
python3 tools/verify_core_imports.py
```

### 测试
```bash
# 运行 FastAPI 测试
pytest tests/test_api.py -v

# 运行 Python 原生库测试
pytest tests/test_python_order_service.py -v

# 运行所有测试
pytest tests/ -v
```

### 代码格式化
```bash
# 格式化代码
black .

# 代码检查
flake8 .
```

## 📁 项目结构

```
.
├── app/                      # FastAPI 应用
│   ├── main.py              # 应用入口
│   ├── api/v1/              # API 路由
│   ├── models/              # 数据模型
│   ├── services/            # 业务服务
│   └── core/                # 核心模块
│       ├── config.py        # 应用配置
│       ├── order_service.py # 订单服务核心
│       └── request_strategies/ # 请求策略
├── examples/                # 使用示例
├── tests/                   # 测试文件
├── docs/                    # 文档
├── tools/                   # 开发工具
├── order_service.py         # 向后兼容导入
└── run_server.py           # 服务器启动脚本
```

## 许可证

MIT License