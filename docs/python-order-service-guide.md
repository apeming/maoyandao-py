# Python 订单服务使用指南

## 概述

Python 订单服务是 JavaScript 版本的完整移植，使用 `curl_cffi` + `web3` 实现相同的功能。它提供了完整的订单管理功能，包括创建、签名和提交订单。

## 主要特性

- ✅ **完整功能移植**: 与 JavaScript 版本功能完全一致
- ✅ **策略模式**: 支持可插拔的请求策略
- ✅ **EIP-712 签名**: 完整支持结构化数据签名
- ✅ **安全检查**: 防止测试过程中意外下真实订单
- ✅ **Cookie 管理**: 自动处理认证 tokens
- ✅ **异步支持**: 全面的异步操作支持

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `web3>=7.0.0` - 以太坊区块链交互
- `curl-cffi>=0.7.0` - HTTP 客户端，支持浏览器指纹伪装
- `eth-account>=0.13.0` - 以太坊账户管理和签名

## 基本使用

### 1. 创建订单服务实例

```python
from order_service import OrderService

# 使用私钥创建服务实例
private_key = "0x你的私钥"
service = OrderService(private_key, {
    'strategy': 'curl_cffi',
    'timeout': 15,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# 初始化服务
await service.init()
```

### 2. 创建订单

```python
# 订单参数
params = {
    'token_amount': '1000000',  # 1 USDC (6位小数)
    'nft_token_id': '0x1234567890abcdef1234567890abcdef12345678'
}

# 创建限价订单
limit_order = service.create_limit_order(params)

# 创建市价订单
market_order = service.create_market_order(params)
```

### 3. 签名订单

```python
# 签名订单
signature = service.sign_order(limit_order)
print(f"订单签名: {signature}")
```

### 4. 登录流程

```python
try:
    # 获取登录消息
    login_message = await service.get_login_message()
    
    # 执行登录
    login_response = await service.login()
    print("登录成功!")
    
    # 获取认证 cookies
    auth_cookies = service.get_auth_cookies()
    if auth_cookies:
        print("认证 cookies 已设置")
        
except Exception as e:
    print(f"登录失败: {e}")
```

### 5. 下单（需要安全确认）

```python
try:
    # 安全检查：必须明确确认下真实订单
    response = await service.place_limit_order(
        params, 
        confirm_real_order=True  # 必需的安全参数
    )
    print("下单成功:", response)
    
except Exception as e:
    print(f"下单失败: {e}")
```

### 6. 清理资源

```python
# 使用完毕后清理资源
await service.destroy()
```

## 完整示例

```python
import asyncio
from order_service import OrderService

async def main():
    # 创建服务实例
    private_key = "0x你的私钥"
    service = OrderService(private_key)
    
    try:
        # 初始化
        await service.init()
        print(f"钱包地址: {service.wallet_address}")
        
        # 创建订单
        params = {
            'token_amount': '1000000',
            'nft_token_id': '0x1234567890abcdef1234567890abcdef12345678'
        }
        
        order = service.create_limit_order(params)
        signature = service.sign_order(order)
        
        print("订单创建并签名成功!")
        print(f"签名: {signature[:20]}...")
        
        # 如果需要登录和下单
        # await service.login()
        # await service.place_limit_order(params, confirm_real_order=True)
        
    except Exception as e:
        print(f"操作失败: {e}")
    
    finally:
        # 清理资源
        await service.destroy()

# 运行示例
asyncio.run(main())
```

## 安全特性

### 1. 真实订单安全检查

```python
# ❌ 这会失败 - 没有安全确认
await service.place_limit_order(params)
# 错误: 安全检查：您必须设置 confirm_real_order=True 来下真实订单

# ✅ 正确的方式 - 明确确认
await service.place_limit_order(params, confirm_real_order=True)
```

### 2. 测试与生产分离

```python
# 测试函数 - 只创建和签名，不提交
def test_order_creation():
    order = service.create_limit_order(test_params)
    signature = service.sign_order(order)
    # 不调用 place_limit_order

# 生产函数 - 需要明确确认
async def place_real_order():
    await service.place_limit_order(
        real_params, 
        confirm_real_order=True  # 必需确认
    )
```

## 策略管理

### 1. 获取策略信息

```python
strategy_info = service.get_strategy_info()
print(f"当前策略: {strategy_info['name']}")
print(f"策略类型: {strategy_info['type']}")
```

### 2. 切换策略

```python
# 切换到新策略（如果有多个可用）
await service.switch_strategy('new_strategy', {
    'timeout': 20,
    'user_agent': 'Custom User Agent'
})
```

### 3. Cookie 管理

```python
# 手动设置 cookies
auth_cookies = {
    'msu_wat': 'your_wat_token',
    'msu_wrt': 'your_wrt_token'
}
service.set_auth_cookies(auth_cookies)

# 获取当前 cookies
cookies = service.get_auth_cookies()

# 清除 cookies
service.clear_auth_cookies()
```

## 时间戳工具

```python
# 获取当前时间戳
timestamp_info = service.get_timestamp(0)
print(f"当前时间(秒): {timestamp_info['sec']}")

# 获取 7 天后的时间戳
future_timestamp = service.get_timestamp(7)
print(f"7天后: {future_timestamp['after_days_sec']}")

# 获取 1 天前的时间戳
past_timestamp = service.get_timestamp(-1)
print(f"1天前: {past_timestamp['after_days_sec']}")
```

## 错误处理

```python
try:
    await service.login()
except Exception as e:
    if "网络" in str(e):
        print("网络连接问题")
    elif "认证" in str(e):
        print("认证失败")
    else:
        print(f"未知错误: {e}")
```

## 测试

运行测试套件：

```bash
# 运行所有测试
pytest tests/test_python_order_service.py -v

# 运行特定测试
pytest tests/test_python_order_service.py::TestOrderService::test_create_limit_order -v

# 运行异步测试
pytest tests/test_python_order_service.py -k "asyncio" -v
```

## 与 JavaScript 版本的对比

| 功能 | JavaScript | Python | 说明 |
|------|------------|--------|------|
| 订单创建 | ✅ | ✅ | 完全一致 |
| EIP-712 签名 | ✅ | ✅ | 完全一致 |
| 登录流程 | ✅ | ✅ | 完全一致 |
| Cookie 管理 | ✅ | ✅ | 完全一致 |
| 策略模式 | ✅ | ✅ | 完全一致 |
| 安全检查 | ✅ | ✅ | 完全一致 |
| 异步支持 | ✅ | ✅ | 完全一致 |

## 注意事项

1. **私钥安全**: 永远不要在代码中硬编码私钥，使用环境变量
2. **测试环境**: 在测试时使用测试私钥和测试网络
3. **错误处理**: 始终包含适当的错误处理逻辑
4. **资源清理**: 使用完毕后调用 `destroy()` 清理资源
5. **安全确认**: 下真实订单时必须设置 `confirm_real_order=True`

## 故障排除

### 常见问题

1. **导入错误**: 确保安装了所有依赖
2. **网络超时**: 调整 timeout 配置
3. **签名失败**: 检查私钥格式和网络配置
4. **Cookie 问题**: 确保使用支持 Cookie 的策略

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查策略状态
print(service.get_strategy_info())

# 检查 cookies
print(service.get_auth_cookies())
```

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！