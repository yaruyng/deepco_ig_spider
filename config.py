# -*- coding: utf-8 -*-
"""
Instagram Spider 配置文件
"""
import os

# 爬取配置
CONFIG = {
    # 每个话题最多获取的帖子数量
    "max_posts_per_hashtag": 50,
    
    # 每个帖子最多获取的评论数量
    "max_comments_per_post": 100,
    
    # 请求间隔（秒），避免被限流
    "request_delay": 2,
    
    # 输出目录
    "output_dir": "output",
    
    # 是否保存为Excel
    "save_excel": True,
    
    # 是否保存为JSON（用户信息）
    "save_json": False,
    
    # 是否保存原始 media JSON 数据
    "save_raw_json": False,
    
    # 请求超时时间（秒）
    "timeout": 30,
    
    # 最大重试次数
    "max_retries": 3,
}

# 创建输出目录
os.makedirs(CONFIG["output_dir"], exist_ok=True)

