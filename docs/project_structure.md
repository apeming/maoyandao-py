# 项目结构说明

## 概述

本项目现在提供两种使用方式：
1. **FastAPI Web 服务** - RESTful API 接口，支持任何编程语言调用
2. **Python 原生库** - 直接在 Python 代码中使用的订单服务类

## 目录结构

```
.
├── app/                          # FastAPI 应用目录
│   ├── __init__.py
│   ├── main.py                   # FastAPI 应用入口
│   ├── core/                     # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py             # 应用配置
│   │   ├── order_service.py      # 订单服务核心
│   │   └── request_strategies/   # 请求策略
│   │       ├── __init__.py
│   │       ├── base_request_strategy.py
│   │       ├── curl_cffi_strategy.py
│   │       ├── proxy_manager.py
│   │       └── strategy_factory.py
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   └── order.py              # 订单相关模型
│   ├── services/                 # 业务服务
│   │   ├── __init__.py
│   │   └── order_service_wrapper.py  # 订单服务包装器
│   └── api/                      # API 路由
│       ├── __init__.py
│       └── v1/                   # API v1 版本
│           ├── __init__.py
│           ├── order.py          # 订单 API
│           └── health.py         # 健康检查 API
├── tests/                        # 测试文件
│   ├── test_api.py              # FastAPI 测试
│   └── test_python_order_service.py  # Python 原生库测试
├── examples/                     # 示例代码
│   ├── api_usage_example.py     # FastAPI 使用示例
│   ├── python_usage_example.py  # Python 原生库示例
│   ├── network_demo.py          # 网络请求演示
│   └── test_fastapi_network.py  # FastAPI 网络测试
├── docs/                         # 文档
│   ├── fastapi_usage.md         # FastAPI 使用指南
│   ├── project_structure.md     # 本文件
│   └── cleanup_summary.md       # 清理总结
├── tools/                        # 开发工具
│   ├── __init__.py
│   └── cleanup.py               # 项目清理工具
├── order_service.py             # 向后兼容导入
├── run_server.py                # FastAPI 服务器启动脚本
├── quick_start.py               # 快速启动演示
├── Dockerfile                   # Docker 配置
├── docker-compose.yml           # Docker Compose 配置
├── requirements.txt             # Python 依赖
└── README.md                    # 项目说明
```

## 架构设计

### FastAPI 应用架构

```
┌─────────────────┐
│   HTTP 请求     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   (app/main.py) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   API 路由      │
│ (app/api/v1/)   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   数据验证      │
│ (app/models/)   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   业务服务      │
│ (app/services/) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   订单服务      │
│ (order_service) │
└─────────────────┘
```

### 核心组件说明

#### 1. FastAPI 应用 (`app/main.py`)
- 应用入口点
- 中间件配置
- 路由注册
- 生命周期管理

#### 2. 配置管理 (`app/core/config.py`)
- 环境变量处理
- 应用配置集中管理
- 使用 Pydantic Settings

#### 3. 数据模型 (`app/models/order.py`)
- 请求/响应模型定义
- 数据验证规则
- 错误响应模型

#### 4. 业务服务 (`app/services/order_service_wrapper.py`)
- 封装原有的 OrderService
- 提供异步接口
- 服务实例缓存
- 错误处理和转换

#### 5. API 路由 (`app/api/v1/`)
- RESTful 接口定义
- HTTP 状态码处理
- 请求参数验证
- 响应格式化

## 使用方式对比

### FastAPI Web 服务

**优点：**
- 跨语言支持
- 标准 HTTP 接口
- 自动 API 文档
- 易于部署和扩展
- 支持负载均衡

**适用场景：**
- 微服务架构
- 多语言环境
- 需要 Web 接口
- 生产环境部署

**使用示例：**
```bash
# 启动服务
python run_server.py

# 调用 API
curl -X POST "http://localhost:8000/api/v1/order" \
  -H "Content-Type: application/json" \
  -d '{"nft_token_id": "123", "order_type": "market", ...}'
```

### Python 原生库

**优点：**
- 直接集成
- 更好的性能
- 完整的 Python 特性
- 更灵活的配置

**适用场景：**
- Python 项目集成
- 脚本和自动化
- 高性能要求
- 复杂业务逻辑

**使用示例：**
```python
from order_service import OrderService

service = OrderService(private_key)
await service.init()
result = await service.place_market_order(params)
```

## 安全特性

### 1. 强制确认机制
- 所有真实订单必须设置 `confirm_real_order=true`
- 防止测试过程中的意外下单

### 2. 参数验证
- Pydantic 模型严格验证
- 类型检查和格式验证
- 自动错误提示

### 3. 错误处理
- 统一的错误响应格式
- 详细的错误代码
- 安全的错误信息

### 4. 服务隔离
- 私钥基于哈希的服务缓存
- 避免服务实例混用
- 资源自动清理

## 部署选项

### 1. 开发环境
```bash
python run_server.py
```

### 2. 生产环境
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Docker 部署
```bash
docker build -t order-service .
docker run -p 8000:8000 order-service
```

### 4. Docker Compose
```bash
docker-compose up -d
```

## 扩展建议

### 1. 认证和授权
- JWT 令牌认证
- API 密钥管理
- 用户权限控制

### 2. 监控和日志
- 请求日志记录
- 性能监控
- 错误追踪

### 3. 缓存优化
- Redis 缓存
- 响应缓存
- 数据库连接池

### 4. 安全增强
- 请求频率限制
- IP 白名单
- 加密传输

## 测试策略

### 1. 单元测试
```bash
pytest tests/test_api.py
```

### 2. 集成测试
```bash
python examples/api_usage_example.py
```

### 3. 性能测试
- 使用 locust 或 ab 进行压力测试
- 监控响应时间和吞吐量

### 4. 安全测试
- 参数注入测试
- 认证绕过测试
- 错误处理测试

## 维护指南

### 1. 依赖更新
- 定期更新 requirements.txt
- 检查安全漏洞
- 测试兼容性

### 2. 代码质量
- 使用 black 格式化代码
- flake8 代码检查
- 类型注解完善

### 3. 文档维护
- 保持 API 文档更新
- 更新使用示例
- 记录变更日志

### 4. 监控和告警
- 服务健康检查
- 错误率监控
- 性能指标追踪