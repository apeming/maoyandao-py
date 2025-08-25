#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastAPI 订单服务测试
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """测试健康检查"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_create_order_without_confirmation():
    """测试不确认的订单创建（应该失败）"""
    order_data = {
        "nft_token_id": "test_token_id",
        "order_type": "market",
        "private_key": "test_private_key",
        "amount": 10,
        "confirm_real_order": False
    }
    
    response = client.post("/api/v1/order", json=order_data)
    assert response.status_code == 422  # 验证错误


def test_create_order_missing_amount():
    """测试缺少数量参数的订单创建（应该失败）"""
    order_data = {
        "nft_token_id": "test_token_id",
        "order_type": "market",
        "private_key": "test_private_key",
        "confirm_real_order": True
        # 缺少 amount 和 token_amount
    }
    
    response = client.post("/api/v1/order", json=order_data)
    assert response.status_code == 422  # 验证错误


def test_create_order_invalid_order_type():
    """测试无效订单类型（应该失败）"""
    order_data = {
        "nft_token_id": "test_token_id",
        "order_type": "invalid_type",
        "private_key": "test_private_key",
        "amount": 10,
        "confirm_real_order": True
    }
    
    response = client.post("/api/v1/order", json=order_data)
    assert response.status_code == 422  # 验证错误