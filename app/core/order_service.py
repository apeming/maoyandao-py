#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from datetime import datetime, timezone
import  logging
import json
import time
from typing import Dict, Any, Optional, Union

from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data
from .request_strategies.strategy_factory import RequestStrategyFactory


logger = logging.getLogger(__name__)


class OrderService:
    """订单服务类 - 提供完整的订单管理功能"""
    
    # EIP-712 域数据
    DOMAIN = {
        'name': 'Marketplace',
        'version': '1.0',
        'chainId': 68414,
        'verifyingContract': '0xf1c82c082af3de3614771105f01dc419c3163352'
    }
    
    # EIP-712 类型定义
    TYPES = {
        'EIP712Domain': [
            {'name': 'name', 'type': 'string'},
            {'name': 'version', 'type': 'string'},
            {'name': 'chainId', 'type': 'uint256'},
            {'name': 'verifyingContract', 'type': 'address'}
        ],
        'Order': [
            {'name': 'isSeller', 'type': 'uint256'},
            {'name': 'maker', 'type': 'address'},
            {'name': 'listingTime', 'type': 'uint256'},
            {'name': 'expirationTime', 'type': 'uint256'},
            {'name': 'tokenAddress', 'type': 'address'},
            {'name': 'tokenAmount', 'type': 'uint256'},
            {'name': 'nftAddress', 'type': 'address'},
            {'name': 'nftTokenId', 'type': 'uint256'},
            {'name': 'salt', 'type': 'uint256'},
        ]
    }
    
    def __init__(self, private_key: str, options: Dict[str, Any] = None):
        """
        初始化订单服务
        
        Args:
            private_key: 私钥
            options: 配置选项
        """
        if options is None:
            options = {}
            
        self.private_key = private_key
        self.rpc_url = options.get('rpc_url', 'https://mainnet.base.org')
        
        # 初始化 Web3 和账户
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.account = Account.from_key(private_key)
        self.wallet_address = self.account.address
        
        # 认证信息存储
        self.auth_tokens = {
            'wat': None,
            'wrt': None,
            'wat_expire_at': None,
            'wrt_expire_at': None
        }
        
        # 请求策略配置
        self.strategy_type = options.get('strategy', RequestStrategyFactory.STRATEGIES['CURL_CFFI'])
        self.strategy_config = {
            'timeout': options.get('timeout', 15),
            'use_proxy': options.get('use_proxy', True),
            'proxy_file': options.get('proxy_file', 'proxies.txt'),
            **options.get('strategy_config', {})
        }
        
        # 创建请求策略实例
        self.request_strategy = RequestStrategyFactory.create(self.strategy_type, self.strategy_config)
    
    async def init(self):
        """初始化服务"""
        await self.request_strategy.init()
        logger.info(f"OrderService 初始化完成，使用策略: {self.request_strategy.get_name()}")
    
    def get_timestamp(self, n: int = 0) -> Dict[str, int]:
        """
        获取当前时间戳，并计算 n 天后的秒级时间戳
        
        Args:
            n: 需要往后（或往前）的天数，可为 0；负数表示往前
            
        Returns:
            包含毫秒、秒和 n 天后时间戳的字典
        """
        if not isinstance(n, (int, float)) or n != n:  # 检查 NaN
            raise TypeError('n 必须是数字')
        
        ms = int(time.time() * 1000)
        sec = int(time.time())
        
        ONE_DAY_SEC = 86400
        after_days_sec = sec + int(n * ONE_DAY_SEC)
        
        return {
            'ms': ms,
            'sec': sec,
            'after_days_sec': after_days_sec
        }
    
    def _process_token_amount(self, token_amount: Union[str, int, float]) -> str:
        """
        处理代币数量，转换为正确的单位
        
        Args:
            token_amount: 代币数量（可以是数字或字符串）
            
        Returns:
            处理后的代币数量字符串（wei 单位）
            
        Raises:
            ValueError: 当代币数量过大或无效时
        """
        # 转换为数字
        try:
            if isinstance(token_amount, str):
                amount = float(token_amount)
            else:
                amount = float(token_amount)
        except (ValueError, TypeError):
            raise ValueError(f'无效的代币数量: {token_amount}')
        
        # 检查是否为负数
        if amount < 0:
            raise ValueError('代币数量不能为负数')
        
        # 检查是否过大（防止用户弄错单位）
        # 假设最大合理数量为 1,000,000,000（10亿个代币）
        MAX_REASONABLE_AMOUNT = 1_000_000_000
        if amount > MAX_REASONABLE_AMOUNT:
            raise ValueError(f'代币数量过大: {amount}，可能单位错误。最大支持数量: {MAX_REASONABLE_AMOUNT}')
        
        # 转换为 wei 单位 (乘以 10^18)
        wei_amount = int(amount * 1_000_000_000_000_000_000)
        
        return str(wei_amount)
    
    def create_order(self, params: Dict[str, Any], is_seller: bool = False, expire_days: int = 3) -> Dict[str, Any]:
        """
        创建订单数据（市价单和限价单通用）
        
        Args:
            params: 订单参数
                - amount: 代币数量（会自动转换为 wei 单位）
                - token_amount: 已经是 wei 单位的代币数量（直接使用）
                - nft_token_id: NFT 代币ID
                注意：优先使用 token_amount，如果没有则使用 amount
            is_seller: 是否卖出
            expire_days: 订单过期天数

        Returns:
            订单数据字典
        """
        # 处理代币数量：优先使用 token_amount，否则转换 amount
        if 'token_amount' in params:
            processed_token_amount = str(params['token_amount'])
        elif 'amount' in params:
            processed_token_amount = self._process_token_amount(params['amount'])
        else:
            raise ValueError('必须提供 amount 或 token_amount 参数')
        
        nft_token_id = params['nft_token_id']
        
        timestamp_info = self.get_timestamp(expire_days)
        
        return {
            'isSeller': is_seller,
            'maker': self.wallet_address,
            'listingTime': str(timestamp_info['sec']),
            'expirationTime': str(timestamp_info['after_days_sec']),
            'tokenAddress': '0x07E49Ad54FcD23F6e7B911C2068F0148d1827c08',
            'tokenAmount': processed_token_amount,
            'nftAddress': '0x43DCff2A0cedcd5e10e6f1c18b503498dDCe60d5',
            'nftTokenId': nft_token_id,
            'salt': str(timestamp_info['ms'])
        }
    
    def create_market_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建市价单订单数据
        
        Args:
            params: 订单参数
                
        Returns:
            订单数据字典
        """
        return self.create_order(params)
    
    def create_limit_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建限价单订单数据
        
        Args:
            params: 订单参数
                
        Returns:
            订单数据字典
        """
        return self.create_order(params)
    
    def create_sell_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建卖出挂单订单数据
        
        Args:
            params: 订单参数
                
        Returns:
            订单数据字典
        """
        return self.create_order(params, True, 14)

    def sign_order(self, order: Dict[str, Any]) -> str:
        """
        签名订单

        Args:
            order: 订单数据

        Returns:
            签名字符串
        """
        # 准备签名用的订单数据
        order_for_signing = {
            'isSeller': 0,
            'maker': order['maker'].lower(),
            'listingTime': int(order['listingTime']),
            'expirationTime': int(order['expirationTime']),
            'tokenAddress': order['tokenAddress'].lower(),
            'tokenAmount': order['tokenAmount'],
            'nftAddress': order['nftAddress'].lower(),
            'nftTokenId': order['nftTokenId'].lower(),
            'salt': int(order['salt'])
        }
        
        # 构建完整的 EIP-712 消息
        full_message = {
            'types': self.TYPES,
            'primaryType': 'Order',
            'domain': self.DOMAIN,
            'message': order_for_signing
        }
        
        # 使用 full_message 参数进行编码
        encoded_data = encode_typed_data(full_message=full_message)
        signature = self.account.sign_message(encoded_data)
        
        return '0x' + signature.signature.hex()

    async def get_markets(self, filter: Dict[str, Any] = {}, sorting: str = 'ExploreSorting_RECENTLY_LISTED'):
        url = f"https://msu.io/marketplace/api/marketplace/explore/items"

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7,sl;q=0.6',
            'origin': 'https://msu.io',
            'referer': 'https://msu.io/marketplace',
        }

        markets = []

        # filter_example = {
        #     "name": "Salmon Sushi",
        #     "categoryNo": 0,
        #     "price": { "min": 0, "max": 9000 },
        #     "level": { "min": 0, "max": 250 },
        #     "starforce": { "min": 0, "max": 25 },
        #     "potential": { "min": 0, "max": 4 },
        #     "bonusPotential": { "min": 0, "max": 4 }
        # }

        try:
            response = await self.request_strategy.post(
                url,
                headers=headers,
                payload={
                    'filter': filter,
                    'sorting': sorting,
                    'walletAddr': self.wallet_address,
                    # "paginationParam": {
                    #     "pageNo": 1,
                    #     "pageSize": 135
                    # }
                }
            )

            if response['success']:
                data = response['data']

                items = data['items']
                # pagination_result = data['paginationResult']

                for item in items:
                    sales_info = item['salesInfo']
                    created_at = sales_info['createdAt']
                    created_at_dt = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                    created_at_ts = int(created_at_dt.timestamp())
                    markets.append({
                        'id': item['data']['itemId'],
                        'name': item['name'],
                        'token_id': sales_info['tokenId'],
                        'price_wei': sales_info['priceWei'],
                        'minimum_price_wei': sales_info['minimumPriceWei'],
                        'last_traded_price_wei': sales_info['lastTradedPriceWei'],
                        'created_at': created_at,
                        'created_at_ts': created_at_ts,
                    })

        except Exception as e:
            logger.error(e)

        return markets

    async def get_item_details(self, token_id: str) -> Dict[str, Any]:
        """
        获取商品详情
        
        Args:
            token_id: 商品代币ID
            
        Returns:
            商品详情数据
        """
        url = f'https://msu.io/marketplace/api/marketplace/items/{token_id}'
        
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7,sl;q=0.6',
            'origin': 'https://msu.io',
            'referer': 'https://msu.io/marketplace',
        }

        logger.info(f'[{token_id}] 获取商品详情')
        
        try:
            response = await self.request_strategy.get(url, headers=headers)

            if response['success']:
                data = response['data']
                if isinstance(data, str):
                    data = json.loads(data)

                logger.info(f'[{token_id}] 获取商品详情成功: {data}')

                created_at = data['salesInfo']["createdAt"]
                created_at_dt = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                data['createdAtTs'] = int(created_at_dt.timestamp())

                return data
            elif response['status'] == 429:
                raise Exception(f"获取订单详情失败: 请求太频繁")
            elif response['status'] == 403:
                raise Exception(f"获取订单详情失败: 请求被封禁")
            else:
                raise Exception(f"获取订单详情失败: {response['status']}")
        except Exception as e:
            raise e

    async def get_login_message(self) -> str:
        """
        获取登录消息
        
        Returns:
            登录消息字符串
        """
        url = 'https://msu.io/swapnwarp/api/web/message'
        payload = {'address': self.wallet_address}
        
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7,sl;q=0.6',
            'content-type': 'application/json',
            'origin': 'https://msu.io',
            'referer': 'https://msu.io/swapnwarp',
        }
        
        try:
            response = await self.request_strategy.post(url, payload, headers=headers)
            
            if response['success']:
                data = response['data']
                if isinstance(data, str):
                    data = json.loads(data)
                return data['message']
            elif response['status'] == 429:
                raise Exception(f"获取message失败: 请求太频繁")
            elif response['status'] == 403:
                raise Exception(f"获取message失败: 请求被封禁")
            else:
                raise Exception(f"获取message失败: {response['status']}")
        except Exception as e:
            raise e
    
    def sign_login_message(self, message: str) -> str:
        """
        签名登录消息
        
        Args:
            message: 登录消息
            
        Returns:
            签名字符串
        """
        from eth_account.messages import encode_defunct
        
        # 将文本消息编码为可签名的消息格式
        encoded_message = encode_defunct(text=message)
        signature = self.account.sign_message(encoded_message)
        return '0x' + signature.signature.hex()

    async def login(self) -> Dict[str, Any]:
        """
        执行登录流程
        
        Returns:
            登录响应数据
        """
        login_message = await self.get_login_message()

        signature = self.sign_login_message(login_message)
        
        url = 'https://msu.io/swapnwarp/api/web/signin-wallet'
        payload = {
            'address': self.wallet_address,
            'signature': signature,
            'walletType': 'WALLET_TYPE_METAMASK'
        }

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7,sl;q=0.6',
            'content-type': 'application/json',
            'origin': 'https://msu.io',
            'referer': 'https://msu.io/swapnwarp',
            'x-msu-address': payload['address']
        }
        
        try:
            response = await self.request_strategy.post(url, payload, headers=headers, timeout=15)
            
            # 从响应数据中提取认证信息并设置为 cookies
            try:
                response_data = response['data']
                if isinstance(response_data, str):
                    response_data = json.loads(response_data)
                
                if response_data.get('wat') and response_data.get('wrt'):
                    # 存储认证 tokens 到实例变量中
                    self.auth_tokens = {
                        'wat': response_data['wat'],
                        'wrt': response_data['wrt'],
                        'wat_expire_at': response_data.get('watExpireAt'),
                        'wrt_expire_at': response_data.get('wrtExpireAt')
                    }
                    
                    # 将认证信息设置为 cookies（msu_wat 和 msu_wrt）
                    if hasattr(self.request_strategy, 'set_cookies'):
                        auth_cookies = {
                            'msu_wat': response_data['wat'],
                            'msu_wrt': response_data['wrt']
                        }
                        self.request_strategy.set_cookies(auth_cookies)
                    
                    logger.info('登录成功')

                else:
                    logger.error('登录响应中未找到 wat 或 wrt tokens')
            except Exception as parse_error:
                logger.error(f'解析登录响应失败: {parse_error}')
            
            return response
        except Exception as e:
            logger.error(f'登录失败: {e}')
            raise e

    async def _single_purchase_task(self, params: Dict[str, Any], delay: int) -> Dict[str, Any]:
        """单个抢购任务"""
        nft_token_id = params['nft_token_id']
        url = f"https://msu.io/marketplace/api/marketplace/items/{nft_token_id}/buy"
        
        order = self.create_market_order(params)
        order_sign = self.sign_order(order)
        
        payload = {
            'order': order,
            'orderSign': order_sign
        }
        
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7,sl;q=0.6',
            'content-type': 'application/json',
            'origin': 'https://msu.io',
            'referer': 'https://msu.io/marketplace',
        }

        blocked_message = 'purchase blocked: the product is not ready for sale yet'
        
        try:
            # 延迟 delay_ms 毫秒
            if delay > 0:
                await asyncio.sleep(delay / 1000)
            
            logger.info(f'[{nft_token_id}] 等待 {delay}ms 后开始下单...')

            response = await self.request_strategy.post(url, payload, headers=headers)
            data = response['data']
            logger.info(f'{nft_token_id}] 等待 {delay}ms 后下单结果: {data}')
            message = data.get('message')

            if message != blocked_message:
                return response
            else:
                raise Exception(f'抢购失败: {message}')
                
        except Exception as e:
            # 失败后等待5秒再退出
            logger.error(f'[{nft_token_id}] 等待 {delay}ms 后下单失败: {e}')
            await asyncio.sleep(5)
            raise e

    async def place_market_order(self, params: Dict[str, Any], confirm_real_order: bool = False, concurrent_tasks: int = 300) -> Dict[str, Any]:
        """
        下市价单
        
        Args:
            params: 订单参数
                - nft_token_id: NFT 代币ID
                - amount: 代币数量（会自动转换为 wei 单位）
                - token_amount: 已经是 wei 单位的代币数量（直接使用）
                注意：优先使用 token_amount，如果没有则使用 amount
            confirm_real_order: 确认下真实订单的安全检查参数
            
        Returns:
            下单响应数据
        """
        # 安全检查：防止测试过程中意外下真实订单
        if not confirm_real_order:
            raise Exception('安全检查：您必须设置 confirm_real_order=True 来下真实订单')
        
        # 检查是否已认证
        if not self.is_authenticated():
            raise Exception('未认证：请先调用 login() 方法进行登录')

        wait_interval = 30
        created_at_ms = int(params['created_at_ts'] * 1000)

        logger.info(f"订单已创建 {int(time.time()) - params['created_at_ts']}s")

        while True:
            if int(time.time() * 1000) - created_at_ms >= int(wait_interval * 1000):
                break
            await asyncio.sleep(0.001)  # 1ms延迟

        logger.info('冷却期结束，开始启动抢购协程...')

        # 启动多个协程抢购
        tasks = []
        for i in range(concurrent_tasks):
            task = asyncio.create_task(self._single_purchase_task(params, i * 10))
            tasks.append(task)
        
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            
            # 取消剩余任务
            for task in pending:
                task.cancel()
            
            # 返回第一个成功的结果
            return await list(done)[0]
        except Exception as e:
            for task in tasks:
                if not task.done():
                    task.cancel()
            raise e


    async def place_limit_order(self, params: Dict[str, Any], confirm_real_order: bool = False) -> Dict[str, Any]:
        """
        下限价单
        
        Args:
            params: 订单参数
                - nft_token_id: NFT 代币ID
                - amount: 代币数量（会自动转换为 wei 单位）
                - token_amount: 已经是 wei 单位的代币数量（直接使用）
                注意：优先使用 token_amount，如果没有则使用 amount
            confirm_real_order: 确认下真实订单的安全检查参数
            
        Returns:
            下单响应数据
        """
        # 安全检查：防止测试过程中意外下真实订单
        if not confirm_real_order:
            raise Exception('安全检查：您必须设置 confirm_real_order=True 来下真实订单')
        
        # 检查是否已认证
        if not self.is_authenticated():
            raise Exception('未认证：请先调用 login() 方法进行登录')
        
        nft_token_id = params['nft_token_id']
        url = f"https://msu.io/marketplace/api/marketplace/items/{nft_token_id}/offer"
        
        order = self.create_limit_order(params)
        order_sign = self.sign_order(order)
        
        payload = {
            'order': order,
            'orderSign': order_sign
        }
        
        # 设置请求头（认证信息通过 cookies 携带）
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7,sl;q=0.6',
            'content-type': 'application/json',
            'origin': 'https://msu.io',
            'referer': 'https://msu.io/marketplace',
            # 'x-msu-address': self.wallet_address
        }
        
        try:
            response = await self.request_strategy.post(url, payload, headers=headers)
            logger.info('下单响应:', response['data'])
            return response
        except Exception as e:
            logger.error(f'下单失败: {e}')
            raise e
    
    async def place_sell_order(self, params: Dict[str, Any], confirm_real_order: bool = False) -> Dict[str, Any]:
        """
        卖单
        
        Args:
            params: 订单参数
                - nft_token_id: NFT 代币ID
                - token_amount: 已经是 wei 单位的代币数量（直接使用）
            confirm_real_order: 确认下真实订单的安全检查参数
            
        Returns:
            下单响应数据
        """
        # 安全检查：防止测试过程中意外下真实订单
        if not confirm_real_order:
            raise Exception('安全检查：您必须设置 confirm_real_order=True 来下真实订单')
        
        # 检查是否已认证
        if not self.is_authenticated():
            raise Exception('未认证：请先调用 login() 方法进行登录')
        
        nft_token_id = params['nft_token_id']
        url = f"https://msu.io/marketplace/api/marketplace/items/{nft_token_id}/register"
        
        order = self.create_sell_order(params)
        order_sign = self.sign_order(order)
        
        payload = {
            'order': order,
            'orderSign': order_sign
        }
        
        # 设置请求头（认证信息通过 cookies 携带）
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7,sl;q=0.6',
            'content-type': 'application/json',
            'origin': 'https://msu.io',
            'referer': 'https://msu.io/marketplace',
            # 'x-msu-address': self.wallet_address
        }
        
        try:
            response = await self.request_strategy.post(url, payload, headers=headers)
            logger.info('下单响应:', response['data'])
            return response
        except Exception as e:
            logger.error(f'下单失败: {e}')
            raise e

    async def switch_strategy(self, strategy_type: str, config: Dict[str, Any] = None):
        """
        切换请求策略
        
        Args:
            strategy_type: 新的策略类型
            config: 策略配置
        """
        if config is None:
            config = {}
            
        logger.info(f"切换请求策略从 {self.strategy_type} 到 {strategy_type}")
        
        # 销毁当前策略
        await self.request_strategy.destroy()
        
        # 创建新策略
        self.strategy_type = strategy_type
        self.strategy_config = {**self.strategy_config, **config}
        self.request_strategy = RequestStrategyFactory.create(self.strategy_type, self.strategy_config)
        
        # 初始化新策略
        await self.request_strategy.init()
        logger.info(f"策略切换完成，当前使用: {self.request_strategy.get_name()}")
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        获取当前使用的策略信息
        
        Returns:
            策略信息字典
        """
        return {
            'type': self.strategy_type,
            'name': self.request_strategy.get_name(),
            'config': self.strategy_config
        }
    
    def get_auth_cookies(self) -> Optional[Dict[str, str]]:
        """
        获取当前存储的认证 cookies
        
        Returns:
            认证 cookies 字典或 None
        """
        if hasattr(self.request_strategy, 'get_cookies'):
            return self.request_strategy.get_cookies()
        return None
    
    def set_auth_cookies(self, wat: str, wrt: str):
        """
        手动设置认证 cookies
        
        Args:
            wat: wat token 值
            wrt: wrt token 值
        """
        if hasattr(self.request_strategy, 'set_cookies'):
            auth_cookies = {
                'msu_wat': wat,
                'msu_wrt': wrt
            }
            self.request_strategy.set_cookies(auth_cookies)
            
            # 同时更新实例变量
            self.auth_tokens['wat'] = wat
            self.auth_tokens['wrt'] = wrt
            
            logger.info('已设置认证 cookies')
        else:
            logger.warning('当前策略不支持设置 cookies')
    
    def clear_auth_cookies(self):
        """清除认证 cookies"""
        if hasattr(self.request_strategy, 'clear_cookies'):
            self.request_strategy.clear_cookies()
            logger.info('已清除认证 cookies')
        
        # 同时清除实例变量
        self.clear_auth_tokens()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        获取包含认证信息的请求头
        
        Returns:
            包含认证信息的请求头字典
        """
        headers = {}
        
        if self.auth_tokens['wat']:
            headers['Authorization'] = f"Bearer {self.auth_tokens['wat']}"
        
        if self.auth_tokens['wrt']:
            headers['X-Refresh-Token'] = self.auth_tokens['wrt']
        
        # 添加地址头
        headers['x-msu-address'] = self.wallet_address
        
        return headers
    
    def is_authenticated(self) -> bool:
        """
        检查是否已认证
        
        Returns:
            是否已认证
        """
        return bool(self.auth_tokens['wat'] and self.auth_tokens['wrt'])
    
    def clear_auth_tokens(self):
        """清除认证信息"""
        self.auth_tokens = {
            'wat': None,
            'wrt': None,
            'wat_expire_at': None,
            'wrt_expire_at': None
        }
        logger.info('已清除认证信息')
    
    def get_proxy_info(self) -> Dict[str, Any]:
        """
        获取代理信息
        
        Returns:
            代理信息字典
        """
        if hasattr(self.request_strategy, 'get_proxy_info'):
            return self.request_strategy.get_proxy_info()
        return {'use_proxy': False, 'proxy_count': 0, 'proxy_available': False}
    
    def set_proxy_enabled(self, enabled: bool):
        """
        启用或禁用代理
        
        Args:
            enabled: 是否启用代理
        """
        if hasattr(self.request_strategy, 'set_proxy_enabled'):
            self.request_strategy.set_proxy_enabled(enabled)
        else:
            logger.warning('当前策略不支持代理配置')
    
    async def destroy(self):
        """清理资源"""
        if self.request_strategy:
            await self.request_strategy.destroy()