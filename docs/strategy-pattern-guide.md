# 请求策略模式使用指南

## 概述

本项目实现了策略模式来管理不同的 HTTP 请求方式，支持在 `CycleTLS` 和 `Puppeteer` 策略之间灵活切换，以应对不同级别的反爬虫检测。

## 可用策略

### 1. CycleTLS 策略
- **适用场景**: 基本的反爬虫检测
- **优点**: 速度快，资源消耗少
- **缺点**: 可能无法绕过高级的反爬虫检测（如 Cloudflare）

### 2. Puppeteer 策略  
- **适用场景**: 高级反爬虫检测（如 Cloudflare）
- **优点**: 真实浏览器环境，绕过能力强
- **缺点**: 速度较慢，资源消耗大

## 基本使用

### 创建 OrderService 实例

```javascript
import OrderService from './order-service.js';
import RequestStrategyFactory from './src/request-strategies/strategy-factory.js';

// 使用默认的 CycleTLS 策略
const orderService = new OrderService(privateKey);

// 或者明确指定策略
const orderService = new OrderService(privateKey, {
    strategy: RequestStrategyFactory.STRATEGIES.CYCLETLS,
    timeout: 15000
});

// 使用 Puppeteer 策略
const orderService = new OrderService(privateKey, {
    strategy: RequestStrategyFactory.STRATEGIES.PUPPETEER,
    headless: true,
    strategyConfig: {
        turnstile: true,
        args: ['--no-sandbox']
    }
});
```

### 初始化和使用

```javascript
// 初始化服务
await orderService.init();

// 使用服务（API 保持不变）
const message = await orderService.getLoginMessage();
await orderService.login();
```

## 动态策略切换

### 运行时切换策略

```javascript
// 初始使用 CycleTLS
const orderService = new OrderService(privateKey, {
    strategy: RequestStrategyFactory.STRATEGIES.CYCLETLS
});

await orderService.init();

try {
    // 尝试使用 CycleTLS
    await orderService.getLoginMessage();
} catch (error) {
    console.log('CycleTLS 失败，切换到 Puppeteer');
    
    // 切换到 Puppeteer 策略
    await orderService.switchStrategy(
        RequestStrategyFactory.STRATEGIES.PUPPETEER,
        {
            headless: true,
            turnstile: true
        }
    );
    
    // 重试请求
    await orderService.getLoginMessage();
}
```

### 获取策略信息

```javascript
const strategyInfo = orderService.getStrategyInfo();
console.log('当前策略:', strategyInfo);
// 输出: { type: 'cycletls', name: 'CycleTLSStrategy', config: {...} }
```

## 配置选项

### CycleTLS 策略配置

```javascript
const config = {
    strategy: RequestStrategyFactory.STRATEGIES.CYCLETLS,
    ja3: 'custom_ja3_fingerprint',
    userAgent: 'Custom User Agent',
    timeout: 10000
};
```

### Puppeteer 策略配置

```javascript
const config = {
    strategy: RequestStrategyFactory.STRATEGIES.PUPPETEER,
    headless: false,           // 是否无头模式
    timeout: 30000,           // 请求超时时间
    strategyConfig: {
        turnstile: true,      // 启用验证码解决
        args: [               // Chrome 启动参数
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--start-maximized'
        ],
        proxy: {              // 代理配置（可选）
            host: 'proxy-host',
            port: 'proxy-port',
            username: 'username',
            password: 'password'
        }
    }
};
```

## 高级用法

### 自定义请求策略

如果需要添加新的请求策略，可以继承 `BaseRequestStrategy`：

```javascript
import BaseRequestStrategy from './src/request-strategies/base-request-strategy.js';

class CustomStrategy extends BaseRequestStrategy {
    async init() {
        // 初始化逻辑
    }
    
    async get(url, options = {}) {
        // GET 请求实现
    }
    
    async post(url, data = {}, options = {}) {
        // POST 请求实现
    }
    
    async destroy() {
        // 清理资源
    }
}
```

### Puppeteer 特有功能

当使用 Puppeteer 策略时，可以访问额外的浏览器功能：

```javascript
if (orderService.requestStrategy instanceof PuppeteerStrategy) {
    // 等待页面元素
    await orderService.requestStrategy.waitForSelector('.login-button');
    
    // 点击元素
    await orderService.requestStrategy.click('.login-button');
    
    // 输入文本
    await orderService.requestStrategy.type('#username', 'myusername');
    
    // 获取和设置 cookies
    const cookies = await orderService.requestStrategy.getCookies();
    await orderService.requestStrategy.setCookies(cookies);
    
    // 执行自定义 JavaScript
    const result = await orderService.requestStrategy.evaluate(() => {
        return document.title;
    });
}
```

## 最佳实践

### 1. 渐进式策略使用

```javascript
async function robustRequest(orderService, requestFn) {
    const strategies = [
        RequestStrategyFactory.STRATEGIES.CYCLETLS,
        RequestStrategyFactory.STRATEGIES.PUPPETEER
    ];
    
    for (const strategy of strategies) {
        try {
            if (orderService.strategyType !== strategy) {
                await orderService.switchStrategy(strategy);
            }
            
            return await requestFn();
        } catch (error) {
            console.log(`策略 ${strategy} 失败:`, error.message);
            if (strategy === strategies[strategies.length - 1]) {
                throw error; // 最后一个策略也失败了
            }
        }
    }
}

// 使用示例
const result = await robustRequest(orderService, () => 
    orderService.getLoginMessage()
);
```

### 2. 资源管理

```javascript
// 始终在使用完毕后清理资源
try {
    await orderService.init();
    // 使用服务...
} finally {
    await orderService.destroy();
}
```

### 3. 错误处理

```javascript
try {
    await orderService.getLoginMessage();
} catch (error) {
    if (error.message.includes('Cloudflare')) {
        // 检测到 Cloudflare，切换策略
        await orderService.switchStrategy(
            RequestStrategyFactory.STRATEGIES.PUPPETEER
        );
        // 重试
    } else {
        // 其他错误处理
        throw error;
    }
}
```

## 运行示例

```bash
# 测试策略功能
npm run test-strategies

# 运行策略演示
npm run demo-strategies

# 运行完整测试
npm test
```

## 注意事项

1. **资源管理**: Puppeteer 策略会启动浏览器进程，务必调用 `destroy()` 方法清理资源
2. **性能考虑**: Puppeteer 策略比 CycleTLS 慢，建议优先使用 CycleTLS
3. **环境要求**: Puppeteer 策略在 Linux 环境下可能需要安装额外的依赖
4. **并发限制**: Puppeteer 策略不适合高并发场景，建议控制并发数量

## 故障排除

### Puppeteer 启动失败
```bash
# Linux 环境安装依赖
sudo apt-get install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget
```

### 内存不足
```javascript
// 使用更轻量的配置
const orderService = new OrderService(privateKey, {
    strategy: RequestStrategyFactory.STRATEGIES.PUPPETEER,
    strategyConfig: {
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--memory-pressure-off'
        ]
    }
});
```