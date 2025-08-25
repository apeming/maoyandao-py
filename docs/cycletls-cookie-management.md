# CYCLETLS Cookie 管理功能

## 概述

CYCLETLS 策略现在支持自动管理认证 cookies，特别是针对 MSU.io 平台所需的 `wat` 和 `wrt` tokens。这些 tokens 会自动从登录响应中提取，并在后续请求中作为 `msu_wat` 和 `msu_wrt` cookies 发送。

## 核心功能

### 1. 自动 Cookie 提取

当服务器在响应中设置 `wat` 和 `wrt` cookies 时，CYCLETLS 策略会：
- 自动提取这些 cookies
- 将 `wat` 映射为 `msu_wat`
- 将 `wrt` 映射为 `msu_wrt`
- 保存原始的 `wat` 和 `wrt` cookies
- 在后续请求中自动包含这些 cookies

### 2. 自动请求携带

所有通过 CYCLETLS 策略发送的请求都会自动包含已存储的 cookies，无需手动设置。

### 3. Cookie 管理 API

OrderService 提供了便捷的 cookie 管理方法：

```javascript
// 获取当前存储的 cookies
const cookies = orderService.getAuthCookies();

// 手动设置 cookies
orderService.setAuthCookies({
    'msu_wat': 'your_wat_token',
    'msu_wrt': 'your_wrt_token'
});

// 清除所有 cookies
orderService.clearAuthCookies();
```

## 使用示例

### 基本使用

```javascript
import OrderService from './order-service.js';
import RequestStrategyFactory from './src/request-strategies/strategy-factory.js';

const orderService = new OrderService(privateKey, {
    strategy: RequestStrategyFactory.STRATEGIES.CYCLETLS
});

await orderService.init();

// 登录会自动提取和存储认证 cookies
await orderService.login();

// 后续 API 调用会自动使用这些 cookies
await orderService.placeLimitOrder({
    tokenAmount: '10000000000000000000',
    nftTokenId: '8286772944986971539464905786114'
});
```

### 会话持久化

```javascript
// 保存 cookies 到本地存储
const cookies = orderService.getAuthCookies();
localStorage.setItem('auth_cookies', JSON.stringify(cookies));

// 从本地存储恢复 cookies
const savedCookies = JSON.parse(localStorage.getItem('auth_cookies'));
if (savedCookies) {
    orderService.setAuthCookies(savedCookies);
}
```

### 手动 Cookie 管理

```javascript
// 检查当前 cookies
const cookies = orderService.getAuthCookies();
console.log('当前 cookies:', Object.keys(cookies));

// 添加自定义 cookies
orderService.setAuthCookies({
    'custom_token': 'value',
    'session_preference': 'dark_mode'
});

// 清除过期的 cookies
orderService.clearAuthCookies();
```

## 技术实现

### Cookie 提取逻辑

```javascript
_extractCookies(response) {
    if (response.headers && response.headers['set-cookie']) {
        const setCookieHeaders = Array.isArray(response.headers['set-cookie']) 
            ? response.headers['set-cookie'] 
            : [response.headers['set-cookie']];

        setCookieHeaders.forEach(cookieHeader => {
            if (typeof cookieHeader === 'string') {
                const cookieParts = cookieHeader.split(';')[0].split('=');
                if (cookieParts.length === 2) {
                    const [name, value] = cookieParts;
                    
                    // 提取 wat 和 wrt，并存储为 msu_wat 和 msu_wrt
                    if (name.trim() === 'wat') {
                        this.cookies['msu_wat'] = value.trim();
                    } else if (name.trim() === 'wrt') {
                        this.cookies['msu_wrt'] = value.trim();
                    }
                    
                    // 也保存原始 cookie 名称
                    this.cookies[name.trim()] = value.trim();
                }
            }
        });
    }
}
```

### 请求自动携带

```javascript
// GET 请求
async get(url, options = {}) {
    // 添加已存储的 cookies
    if (Object.keys(this.cookies).length > 0) {
        requestOptions.cookies = this.cookies;
    }
    
    const response = await this.cycleTLS(url, requestOptions, 'get');
    this._extractCookies(response); // 提取新的 cookies
    return this._formatResponse(response);
}
```

## 安全考虑

1. **Cookie 存储**: Cookies 仅在内存中存储，不会自动持久化到磁盘
2. **过期检查**: 建议实现 JWT token 过期检查逻辑
3. **清理机制**: 应用退出时自动清理 cookies
4. **传输安全**: 所有 cookies 通过 HTTPS 传输

## 故障排除

### 常见问题

1. **Cookies 未被提取**
   - 检查服务器响应是否包含 `set-cookie` 头
   - 确认 cookie 名称是否为 `wat` 和 `wrt`

2. **后续请求未携带 cookies**
   - 验证策略类型是否为 CYCLETLS
   - 检查 cookies 是否已正确存储

3. **登录失败**
   - 可能遇到 Cloudflare 挑战，需要调整 JA3 指纹或 User-Agent

### 调试方法

```javascript
// 检查 cookie 状态
const cookies = orderService.getAuthCookies();
console.log('当前 cookies:', cookies);

// 检查策略信息
const strategyInfo = orderService.getStrategyInfo();
console.log('策略信息:', strategyInfo);
```

## 最佳实践

1. **定期检查 Cookie 有效性**: 实现 JWT token 过期检查
2. **错误处理**: 在 cookie 过期时自动重新登录
3. **会话管理**: 合理使用会话持久化功能
4. **安全清理**: 应用退出时清除敏感 cookies

## 相关文件

- `src/request-strategies/cycletls-strategy.js` - CYCLETLS 策略实现
- `order-service.js` - OrderService 主要逻辑
- `examples/cycletls-cookie-demo.js` - 使用示例
- `tests/test-cookie-extraction.js` - Cookie 提取测试