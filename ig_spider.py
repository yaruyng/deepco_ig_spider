# -*- coding: utf-8 -*-
"""
Instagram Spider 核心模块
用于获取话题下的用户列表和帖子评论用户列表
基于 Instagram GraphQL API
"""
import json
import os
import random
import time
from datetime import datetime
from typing import Optional

import pandas as pd
import requests

from config import CONFIG

# Session 文件存储路径
SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)


# User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


class IGSpider:
    """Instagram 爬虫类 - 基于 GraphQL API"""
    
    def __init__(self):
        """初始化爬虫"""
        self.session = requests.Session()
        self.session_id = None
        self.csrf_token = None
        self.ig_www_claim = None
        self.is_logged_in = False
        self.username = None
        
        # 设置默认 headers
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/",
            "X-Requested-With": "XMLHttpRequest",
        })
        
        # 尝试加载已保存的 session
        self._try_load_session()
    
    def _try_load_session(self) -> bool:
        """尝试加载已保存的 session"""
        session_file = os.path.join(SESSION_DIR, "instagram_session.json")
        
        if not os.path.exists(session_file):
            return False
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.session_id = data.get("session_id")
            self.csrf_token = data.get("csrf_token")
            self.ig_www_claim = data.get("ig_www_claim")
            self.username = data.get("username")
            
            if self.session_id:
                self._set_cookies()
                # 验证 session 是否有效
                if self._verify_session():
                    self.is_logged_in = True
                    print(f"✓ 已加载保存的登录状态: @{self.username or 'unknown'}")
                    return True
                else:
                    print("⚠ 保存的登录状态已过期，请重新登录")
                    return False
        except Exception as e:
            print(f"⚠ 加载 session 失败: {e}")
            return False
        
        return False
    
    def _set_cookies(self):
        """设置 cookies"""
        if self.session_id:
            self.session.cookies.set("sessionid", self.session_id, domain=".instagram.com")
        if self.csrf_token:
            self.session.cookies.set("csrftoken", self.csrf_token, domain=".instagram.com")
            self.session.headers["X-CSRFToken"] = self.csrf_token
    
    def _save_session(self):
        """保存 session 到文件"""
        session_file = os.path.join(SESSION_DIR, "instagram_session.json")
        
        data = {
            "session_id": self.session_id,
            "csrf_token": self.csrf_token,
            "ig_www_claim": self.ig_www_claim,
            "username": self.username,
            "saved_at": datetime.now().isoformat(),
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("✓ 登录状态已保存，下次运行将自动登录")
    
    def _verify_session(self) -> bool:
        """验证 session 是否有效"""
        try:
            resp = self.session.get(
                "https://www.instagram.com/accounts/edit/",
                timeout=15,
                allow_redirects=False
            )
            # 如果返回 200 说明已登录，302 重定向说明未登录
            return resp.status_code == 200
        except Exception:
            return False
    
    def set_session_id(self, session_id: str, csrf_token: str = None, ig_www_claim: str = None) -> bool:
        """
        手动设置 session_id
        
        Args:
            session_id: Instagram 的 sessionid cookie
            csrf_token: csrf token
            ig_www_claim: x-ig-www-claim header
        """
        self.session_id = session_id.strip()
        self.csrf_token = csrf_token.strip() if csrf_token else None
        self.ig_www_claim = ig_www_claim.strip() if ig_www_claim else None
        
        self._set_cookies()
        
        print("🔄 正在验证 session...")
        
        if self._verify_session():
            self.is_logged_in = True
            self._save_session()
            print("✓ Session 验证成功！已登录")
            return True
        else:
            print("✗ Session 无效，请检查 sessionid 是否正确")
            return False
    
    def interactive_login(self) -> bool:
        """交互式登录 - 手动输入 sessionid"""
        print("\n" + "=" * 60)
        print("🔐 Instagram 登录 - 手动输入 Session")
        print("=" * 60)
        print("\n获取信息的步骤：")
        print("1. 在浏览器中打开 Instagram 并登录")
        print("2. 按 F12 打开开发者工具")
        print("3. 切换到 Network (网络) 标签页")
        print("4. 随便点击一个帖子，找到 API 请求")
        print("5. 在 Request Headers 中找到以下值：")
        print("   - cookie 中的 sessionid")
        print("   - cookie 中的 csrftoken")
        print("   - x-ig-www-claim")
        print("=" * 60)
        
        session_id = input("\n请粘贴 sessionid 的值: ").strip()
        if not session_id:
            print("✗ sessionid 不能为空")
            return False
        
        csrf_token = input("请粘贴 csrftoken 的值: ").strip()
        if not csrf_token:
            print("✗ csrftoken 不能为空")
            return False
        
        ig_www_claim = input("请粘贴 x-ig-www-claim 的值 (可选，直接回车跳过): ").strip()
        
        return self.set_session_id(session_id, csrf_token, ig_www_claim if ig_www_claim else None)
    
    def logout(self):
        """登出并删除保存的 session"""
        session_file = os.path.join(SESSION_DIR, "instagram_session.json")
        if os.path.exists(session_file):
            os.remove(session_file)
        
        self.session_id = None
        self.csrf_token = None
        self.is_logged_in = False
        self.username = None
        self.session.cookies.clear()
        
        print("✓ 已登出")
    
    def get_login_status(self) -> str:
        """获取登录状态"""
        if self.is_logged_in:
            return f"已登录" + (f": @{self.username}" if self.username else "")
        return "未登录"
    
    def test_connection(self) -> bool:
        """测试与 Instagram 的连接"""
        print("🔍 正在测试网络连接...")
        
        try:
            resp = self.session.get("https://www.instagram.com/", timeout=15)
            if resp.status_code == 200:
                print("  ✓ Instagram 连接正常")
                return True
            else:
                print(f"  ✗ Instagram 返回状态码: {resp.status_code}")
                return False
        except Exception as e:
            print(f"  ✗ 连接失败: {e}")
            print("  提示: 请检查 VPN 是否正常工作")
            return False
    
    def _api_request(self, url: str, params: dict = None) -> Optional[dict]:
        """
        发送 API 请求并获取 JSON 响应
        
        Args:
            url: API URL
            params: 请求参数
        
        Returns:
            JSON 响应数据
        """
        try:
            time.sleep(CONFIG.get("request_delay", 2) + random.uniform(0, 1))
            
            # 从 cookie 中获取 csrftoken
            csrftoken = self.csrf_token or self.session.cookies.get("csrftoken", "")
            
            # 设置 API 请求必要的请求头
            headers = {
                "X-IG-App-ID": "936619743392459",
                "X-ASBD-ID": "359341",
                "X-CSRFToken": csrftoken,
                "X-IG-WWW-Claim": self.ig_www_claim or "0",
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "*/*",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }
            
            resp = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=CONFIG.get("timeout", 30)
            )
            
            # 调试信息
            content_type = resp.headers.get('Content-Type', '')
            if 'json' not in content_type and 'text/html' in content_type:
                print(f"⚠ 返回了 HTML 而不是 JSON，可能需要重新登录")
                print(f"  Content-Type: {content_type}")
                return None
            
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                print("⚠ 请求过于频繁，等待 60 秒...")
                time.sleep(60)
                return self._api_request(url, params)
            elif resp.status_code == 401:
                print("✗ 未授权，请检查登录状态")
                return None
            else:
                print(f"⚠ API 请求失败，状态码: {resp.status_code}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"⚠ 响应不是有效的 JSON: {e}")
            # 打印前 200 个字符帮助调试
            if 'resp' in locals():
                print(f"  响应内容前 200 字符: {resp.text[:200]}...")
            return None
        except Exception as e:
            print(f"⚠ 请求异常: {e}")
            return None
    
    def get_hashtag_users(self, hashtag: str, max_posts: Optional[int] = None) -> list[dict]:
        """
        获取特定话题下发帖用户列表 (通过搜索 API)
        
        Args:
            hashtag: 话题标签（不含#号）
            max_posts: 最多获取的帖子数量
        
        Returns:
            用户信息列表
        """
        import uuid
        
        if max_posts is None:
            max_posts = CONFIG.get("max_posts_per_hashtag", 50)
        
        users = {}
        print(f"\n📌 正在获取话题 #{hashtag} 下的用户...")
        
        # 使用 Instagram 搜索 API (你提供的实际接口)
        api_url = "https://www.instagram.com/api/v1/fbsearch/web/top_serp/"
        
        # 生成 rank_token
        rank_token = str(uuid.uuid4())
        
        params = {
            "enable_metadata": "true",
            "query": f"#{hashtag}",
            "search_session_id": "",
            "rank_token": rank_token,
        }
        
        # 添加必要的 headers
        self.session.headers.update({
            "X-IG-App-ID": "936619743392459",
        })
        
        # 收集原始 media 数据
        all_raw_medias = []
        
        try:
            next_max_id = None
            
            while len(users) < max_posts:
                if next_max_id:
                    params["next_max_id"] = next_max_id
                
                print(f"  请求 API...")
                data = self._api_request(api_url, params)
                
                if not data:
                    print("✗ 无法获取话题数据")
                    break
                
                # 打印返回的数据结构（调试用）
                print(f"  返回数据 keys: {list(data.keys())}")
                
                # 解析返回的数据 - 适配多种可能的结构
                medias = self._extract_medias_from_response(data)
                
                # 收集原始数据
                all_raw_medias.extend(medias)
                
                if not medias:
                    print("  没有找到媒体数据")
                    break
                
                print(f"  找到 {len(medias)} 个帖子")
                
                for media_item in medias:
                    if len(users) >= max_posts:
                        break
                    
                    # 处理数据结构: media_item -> media -> caption -> user
                    media = media_item.get("media", media_item)
                    caption = media.get("caption") or {}
                    user = caption.get("user") or {}
                    location = media.get("location") or {}
                    
                    username = user.get("username")
                    if username and username not in users:
                        # 固定字段，按照 JSON 结构，缺失则为 None
                        users[username] = {
                             # caption.user 字段
                            "username": user.get("username"),
                            "full_name": user.get("full_name"),
                            # media 字段
                            "pk": media.get("pk"),
                            "like_count": media.get("like_count"),
                            "comment_count": media.get("comment_count"),
                             # location 字段
                            "location_name": location.get("name"),
                            "location_address": location.get("address"),
                            "location_city": location.get("city"),
                            "location_short_name": location.get("short_name"),
                            # caption 字段
                            "content_type": caption.get("content_type"),
                            "text": caption.get("text"),
                            "text_translation": caption.get("text_translation"),
                        }
                        print(f"  [{len(users)}/{max_posts}] 用户: @{username}")
                
                # 获取下一页 - next_max_id 在 media_grid 下面
                media_grid = data.get("media_grid", {})
                next_max_id = media_grid.get("next_max_id") or data.get("next_max_id")
                if not next_max_id:
                    print("  没有更多数据")
                    break
            
            print(f"✓ 共获取 {len(users)} 个唯一用户")
            
            # 保存原始 media 数据
            if all_raw_medias:
                self.save_raw_medias(all_raw_medias, f"hashtag_{hashtag}_medias")
            
            # 返回用户列表和最后的 next_max_id
            result = list(users.values())
            # 保存 next_max_id 供后续使用
            self.last_next_max_id = next_max_id
            
            return result
            
        except Exception as e:
            print(f"✗ 获取话题失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_hashtag_posts_with_comments(self, hashtag: str, max_posts: int = 10, 
                                         max_comments_per_post: int = 50) -> dict:
        """
        获取话题下的帖子及其评论
        
        Args:
            hashtag: 话题标签（不含#号）
            max_posts: 最多获取的帖子数量
            max_comments_per_post: 每个帖子最多获取的评论数量
        
        Returns:
            {post_pk: {post_info, comments: [...]}, ...}
        """
        print(f"\n📌 正在获取话题 #{hashtag} 下的帖子及评论...")
        
        # 先获取话题下的帖子
        posts_data = {}
        
        # 使用搜索 API
        import uuid
        api_url = "https://www.instagram.com/api/v1/fbsearch/web/top_serp/"
        rank_token = str(uuid.uuid4())
        
        params = {
            "enable_metadata": "true",
            "query": f"#{hashtag}",
            "search_session_id": "",
            "rank_token": rank_token,
        }
        
        self.session.headers.update({
            "X-IG-App-ID": "936619743392459",
        })
        
        try:
            print(f"  获取帖子列表...")
            data = self._api_request(api_url, params)
            
            if not data:
                print("✗ 无法获取话题数据")
                return {}
            
            medias = self._extract_medias_from_response(data)
            
            if not medias:
                print("✗ 没有找到帖子")
                return {}
            
            print(f"  找到 {len(medias)} 个帖子，开始获取评论...")
            
            count = 0
            for media_item in medias:
                if count >= max_posts:
                    break
                
                media = media_item.get("media", media_item)
                media_pk = media.get("pk")
                caption = media.get("caption") or {}
                user = caption.get("user") or {}
                location = media.get("location") or {}
                
                if not media_pk:
                    continue
                
                # 保存帖子信息
                posts_data[media_pk] = {
                    "post_info": {
                        "pk": media_pk,
                        "username": user.get("username", ""),
                        "full_name": user.get("full_name", ""),
                        "text": caption.get("text", ""),
                        "like_count": media.get("like_count", 0),
                        "comment_count": media.get("comment_count", 0),
                        "location_name": location.get("name", ""),
                    },
                    "comments": []
                }
                
                print(f"\n  [{count + 1}/{max_posts}] 帖子 {media_pk} - @{user.get('username', 'N/A')}")
                
                # 获取该帖子的评论
                comment_users = self._get_post_comments_list(str(media_pk), max_comments_per_post)
                posts_data[media_pk]["comments"] = comment_users
                
                print(f"    获取到 {len(comment_users)} 条评论")
                
                count += 1
            
            print(f"\n✓ 共获取 {len(posts_data)} 个帖子及其评论")
            return posts_data
            
        except Exception as e:
            print(f"✗ 获取话题帖子及评论失败: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _get_post_comments_list(self, media_id: str, max_comments: int) -> list[dict]:
        """获取帖子评论列表（不去重，支持分页）"""
        comments_list = []
        
        api_url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
        params = {
            "can_support_threading": "true",
            "permalink_enabled": "false",
        }
        
        try:
            data = self._api_request(api_url, params)
            
            if not data:
                return []
            
            # 处理第一页评论
            comments = data.get("comments", [])
            self._process_comments_page(comments, comments_list, media_id, max_comments)
            
            # 分页获取更多评论
            next_cursor = data.get("next_min_id")
            while next_cursor and len(comments_list) < max_comments:
                params["min_id"] = next_cursor
                data = self._api_request(api_url, params)
                
                if not data:
                    break
                
                comments = data.get("comments", [])
                self._process_comments_page(comments, comments_list, media_id, max_comments)
                
                next_cursor = data.get("next_min_id")
            
            return comments_list
            
        except Exception:
            return []
    
    def _process_comments_page(self, comments: list, comments_list: list, media_id: str, max_comments: int):
        """处理一页评论数据"""
        for comment in comments:
            if len(comments_list) >= max_comments:
                break
            
            user = comment.get("user", {})
            comment_data = {
                "level": "",
                "username": user.get("username", ""),
                "full_name": user.get("full_name", ""),
                "text": comment.get("text", ""),
                "comment_like_count": comment.get("comment_like_count", 0),
                "child_comment_count": comment.get("child_comment_count", 0),
                "pk": comment.get("pk"),
                "media_id": media_id,
            }
            comments_list.append(comment_data)
            
            # 获取子评论
            child_count = comment.get("child_comment_count", 0)
            if child_count > 0 and len(comments_list) < max_comments:
                comment_pk = comment.get("pk")
                if comment_pk:
                    child_comments = self._get_child_comments_list(media_id, str(comment_pk), max_comments - len(comments_list))
                    comments_list.extend(child_comments)
    
    def _get_child_comments_list(self, media_id: str, comment_pk: str, max_count: int) -> list[dict]:
        """获取子评论列表（支持分页）"""
        child_list = []
        
        api_url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/{comment_pk}/child_comments/"
        params = {
            "min_id": "",
            "is_chronological": "true",
            "paging_direction": "view_more",
        }
        
        try:
            data = self._api_request(api_url, params)
            
            if not data:
                return []
            
            # 处理第一页子评论
            child_comments = data.get("child_comments", [])
            self._process_child_comments_page(child_comments, child_list, media_id, max_count)
            
            # 分页获取更多子评论
            next_cursor = data.get("next_min_id")
            while next_cursor and len(child_list) < max_count:
                params["min_id"] = next_cursor
                data = self._api_request(api_url, params)
                
                if not data:
                    break
                
                child_comments = data.get("child_comments", [])
                self._process_child_comments_page(child_comments, child_list, media_id, max_count)
                
                next_cursor = data.get("next_min_id")
            
            return child_list
            
        except Exception:
            return []
    
    def _process_child_comments_page(self, child_comments: list, child_list: list, media_id: str, max_count: int):
        """处理一页子评论数据"""
        for child in child_comments:
            if len(child_list) >= max_count:
                break
            
            user = child.get("user", {})
            child_list.append({
                "level": "  └─",
                "username": user.get("username", ""),
                "full_name": user.get("full_name", ""),
                "text": child.get("text", ""),
                "comment_like_count": child.get("comment_like_count", 0),
                "child_comment_count": 0,
                "pk": child.get("pk"),
                "media_id": media_id,
            })
    
    def save_posts_with_comments(self, posts_data: dict, filename: str) -> str:
        """
        保存帖子及评论到 Excel（每个帖子一个 sheet）
        
        Args:
            posts_data: {post_pk: {post_info, comments}, ...}
            filename: 文件名（不含扩展名）
        
        Returns:
            保存的文件路径
        """
        if not posts_data:
            print("⚠ 没有数据需要保存")
            return ""
        
        output_dir = CONFIG.get("output_dir", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = f"{output_dir}/{filename}_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            sheet_index = 1
            
            for post_pk, post_data in posts_data.items():
                post_info = post_data["post_info"]
                comments = post_data["comments"]
                
                # Sheet 名称：序号_用户名（限制长度）
                username = post_info.get("username", "unknown")[:15]
                sheet_name = f"{sheet_index}_{username}"[:31]  # Excel sheet 名最长 31 字符
                
                # 创建数据
                rows = []
                
                # 第一行：帖子信息（特殊标记）
                rows.append({
                    "level": "📌",
                    "username": post_info.get('username', ''),
                    "full_name": post_info.get("full_name", ""),
                    "text": post_info.get("text", ""),
                    "comment_like_count": f"👍{post_info.get('like_count', 0)}",
                    "child_comment_count": f"💬{post_info.get('comment_count', 0)}",
                    "pk": post_info.get("pk"),
                    "media_id": "",
                })
                
                # 评论数据
                for comment in comments:
                    rows.append(comment)
                
                if not rows:
                    rows.append({"username": "无评论"})
                
                # 写入 sheet
                df = pd.DataFrame(rows, columns=self.EXCEL_COLUMNS_COMMENT)
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                
                # 设置列宽
                worksheet = writer.sheets[sheet_name]
                column_widths = {
                    'level': 5,
                    'username': 30,
                    'full_name': 30,
                    'text': 60,
                    'comment_like_count': 30,
                    'child_comment_count': 30,
                    'pk': 20,
                    'media_id': 20,
                }
                
                for i, col in enumerate(self.EXCEL_COLUMNS_COMMENT):
                    col_letter = chr(65 + i)
                    width = column_widths.get(col, 15)
                    worksheet.column_dimensions[col_letter].width = width
                
                sheet_index += 1
        
        print(f"📊 已保存Excel: {excel_path}")
        print(f"   共 {len(posts_data)} 个 sheet（每个帖子一个）")
        return excel_path
    
    def _extract_medias_from_response(self, data: dict) -> list:
        """从 API 响应中提取媒体列表"""
        medias = []
        
        # 实际结构: media_grid -> sections -> layout_content -> medias
        if "media_grid" in data:
            sections = data["media_grid"].get("sections", [])
            for section in sections:
                layout_content = section.get("layout_content", {})
                section_medias = layout_content.get("medias", [])
                medias.extend(section_medias)
            return medias
        
        # 备用结构1: sections 直接在顶层
        if "sections" in data:
            for section in data["sections"]:
                layout_content = section.get("layout_content", {})
                section_medias = layout_content.get("medias", [])
                medias.extend(section_medias)
            return medias
        
        # 备用结构2: medias 直接在顶层
        if "medias" in data:
            return data["medias"]
        
        # 备用结构3: items
        if "items" in data:
            return data["items"]
        
        return medias
    
   
    def get_post_comment_users(self, media_id: str, 
                                max_comments: Optional[int] = None) -> list[dict]:
        """
        获取特定帖子下评论用户列表 (通过 API)
        返回树形结构的评论列表（父评论后跟随其子评论）
        
        Args:
            media_id: 帖子的 media_id (pk)
            max_comments: 最多获取的评论数量
        
        Returns:
            评论列表（按树形顺序）
        """
        if max_comments is None:
            max_comments = CONFIG.get("max_comments_per_post", 100)
        
        media_id = media_id.strip()
        if not media_id:
            print("✗ media_id 不能为空")
            return []
        
        comments_list = []  # 使用列表保持顺序
        print(f"\n💬 正在获取帖子 {media_id} 的评论（树形结构）...")
        
        # 使用评论 API
        api_url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
        params = {
            "can_support_threading": "true",
            "permalink_enabled": "false",
        }
        
        # 添加必要的 headers
        self.session.headers.update({
            "X-IG-App-ID": "936619743392459",
        })
        
        try:
            data = self._api_request(api_url, params)
            
            if not data:
                print("✗ 无法获取评论数据")
                return []
            
            # 显示帖子信息
            caption = data.get("caption", {})
            if caption:
                print(f"  帖子作者: @{caption.get('user', {}).get('username', 'N/A')}")
                print(f"  评论数: {data.get('comment_count', 'N/A')}")
            
            # 解析第一层评论
            comments = data.get("comments", [])
            
            for comment in comments:
                if len(comments_list) >= max_comments:
                    break
                
                # 添加父评论
                user = comment.get("user", {})
                parent_comment = {
                    "level": "",
                    "username": user.get("username", ""),
                    "full_name": user.get("full_name", ""),
                    "text": comment.get("text", ""),
                    "comment_like_count": comment.get("comment_like_count", 0),
                    "child_comment_count": comment.get("child_comment_count", 0),
                    "pk": comment.get("pk"),
                    "media_id": media_id,
                }
                comments_list.append(parent_comment)
                print(f"  [{len(comments_list)}] @{user.get('username', '')} - {comment.get('text', '')[:30]}...")
                
                # 获取子评论并紧跟在父评论后面
                child_count = comment.get("child_comment_count", 0)
                if child_count > 0 and len(comments_list) < max_comments:
                    comment_pk = comment.get("pk")
                    if comment_pk:
                        print(f"    ↳ 获取 {child_count} 条子评论...")
                        child_comments = self._get_child_comments_for_tree(
                            media_id, str(comment_pk), 
                            max_comments - len(comments_list)
                        )
                        comments_list.extend(child_comments)
            
            # 如果有更多第一层评论，继续获取
            next_cursor = data.get("next_min_id")
            while next_cursor and len(comments_list) < max_comments:
                params["min_id"] = next_cursor
                data = self._api_request(api_url, params)
                
                if not data:
                    break
                
                comments = data.get("comments", [])
                for comment in comments:
                    if len(comments_list) >= max_comments:
                        break
                    
                    user = comment.get("user", {})
                    parent_comment = {
                        "level": "",
                        "username": user.get("username", ""),
                        "full_name": user.get("full_name", ""),
                        "text": comment.get("text", ""),
                        "comment_like_count": comment.get("comment_like_count", 0),
                        "child_comment_count": comment.get("child_comment_count", 0),
                        "pk": comment.get("pk"),
                        "media_id": media_id,
                    }
                    comments_list.append(parent_comment)
                    print(f"  [{len(comments_list)}] @{user.get('username', '')} - {comment.get('text', '')[:30]}...")
                    
                    # 获取子评论
                    child_count = comment.get("child_comment_count", 0)
                    if child_count > 0 and len(comments_list) < max_comments:
                        comment_pk = comment.get("pk")
                        if comment_pk:
                            child_comments = self._get_child_comments_for_tree(
                                media_id, str(comment_pk),
                                max_comments - len(comments_list)
                            )
                            comments_list.extend(child_comments)
                
                next_cursor = data.get("next_min_id")
            
            print(f"✓ 共获取 {len(comments_list)} 条评论（树形结构）")
            return comments_list
            
        except Exception as e:
            print(f"✗ 获取帖子评论失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_child_comments_for_tree(self, media_id: str, comment_pk: str, max_count: int) -> list:
        """获取子评论列表（用于树形结构）"""
        child_list = []
        
        api_url = f"https://i.instagram.com/api/v1/media/{media_id}/comments/{comment_pk}/child_comments/"
        params = {
            "min_id": "",
            "is_chronological": "true",
            "paging_direction": "view_more",
        }
        
        try:
            data = self._api_request(api_url, params)
            if not data:
                return child_list
            
            child_comments = data.get("child_comments", [])
            
            for child in child_comments:
                if len(child_list) >= max_count:
                    break
                
                user = child.get("user", {})
                child_data = {
                    "level": "  └─",  # 子评论缩进标记
                    "username": user.get("username", ""),
                    "full_name": user.get("full_name", ""),
                    "text": child.get("text", ""),
                    "comment_like_count": child.get("comment_like_count", 0),
                    "child_comment_count": 0,
                    "pk": child.get("pk"),
                    "media_id": media_id,
                }
                child_list.append(child_data)
                print(f"      └─ @{user.get('username', '')} - {child.get('text', '')[:25]}...")
            
            return child_list
            
        except Exception:
            return child_list
    
    def save_raw_medias(self, medias: list[dict], filename: str) -> str:
        """
        保存原始 media JSON 数据
        
        Args:
            medias: media 数据列表
            filename: 文件名（不含扩展名）
        
        Returns:
            保存的文件路径
        """
        # 检查是否需要保存原始 JSON
        if not CONFIG.get("save_raw_json", True):
            return ""
        
        if not medias:
            print("⚠ 没有数据需要保存")
            return ""
        
        output_dir = CONFIG.get("output_dir", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = f"{output_dir}/{filename}_{timestamp}_raw.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(medias, f, ensure_ascii=False, indent=2)
        
        print(f"📄 已保存原始 JSON: {json_path}")
        return json_path
    
    # 话题用户 Excel 列顺序
    EXCEL_COLUMNS_HASHTAG = [
        "username",
        "full_name",
        "pk",
        "like_count",
        "comment_count",
        "location_name",
        "location_address",
        "location_city",
        "location_short_name",
        "content_type",
        "text",
        "text_translation",
    ]
    
    # 评论用户 Excel 列顺序
    EXCEL_COLUMNS_COMMENT = [
        "level",
        "username",
        "full_name",
        "text",
        "comment_like_count",
        "child_comment_count",
        "pk",
        "media_id",
    ]
    
    def save_results(self, data: list[dict], filename: str, data_type: str = "hashtag") -> dict[str, str]:
        """
        保存结果到文件
        
        Args:
            data: 数据列表
            filename: 文件名（不含扩展名）
            data_type: 数据类型 ("hashtag" 或 "comment")
        
        Returns:
            保存的文件路径字典
        """
        if not data:
            print("⚠ 没有数据需要保存")
            return {}
        
        # 根据数据类型选择列
        if data_type == "comment":
            excel_columns = self.EXCEL_COLUMNS_COMMENT
            column_widths = {
                'level': 5,
                'username': 30,
                'full_name': 30,
                'text': 60,
                'comment_like_count': 30,
                'child_comment_count': 30,
                'pk': 20,
                'media_id': 20,
            }
        else:
            excel_columns = self.EXCEL_COLUMNS_HASHTAG
            column_widths = {
                'username': 20,
                'full_name': 25,
                'pk': 25,
                'like_count': 12,
                'comment_count': 15,
                'location_name': 25,
                'location_address': 30,
                'location_city': 20,
                'location_short_name': 25,
                'content_type': 15,
                'text': 80,
                'text_translation': 80,
            }
        
        saved_files = {}
        output_dir = CONFIG.get("output_dir", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{filename}_{timestamp}"
        
        # 保存为Excel
        if CONFIG.get("save_excel", True):
            excel_path = f"{output_dir}/{base_filename}.xlsx"
            
            # 确保所有记录都有固定的列，缺失的设为 None
            normalized_data = []
            for row in data:
                normalized_row = {col: row.get(col) for col in excel_columns}
                normalized_data.append(normalized_row)
            
            # 使用固定列顺序创建 DataFrame
            df = pd.DataFrame(normalized_data, columns=excel_columns)
            
            # 写入 Excel 并设置列宽
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                
                # 设置列宽
                worksheet = writer.sheets['Sheet1']
                
                for i, col in enumerate(excel_columns):
                    col_letter = chr(65 + i)  # A, B, C, ...
                    width = column_widths.get(col, 15)
                    worksheet.column_dimensions[col_letter].width = width
            
            saved_files["excel"] = excel_path
            print(f"📊 已保存Excel: {excel_path}")
        
        # 保存为JSON
        if CONFIG.get("save_json", True):
            json_path = f"{output_dir}/{base_filename}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            saved_files["json"] = json_path
            print(f"📄 已保存JSON: {json_path}")
        
        return saved_files


if __name__ == "__main__":
    print("=" * 50)
    print("Instagram Spider 测试")
    print("=" * 50)
    print("\n请在 main.py 中运行具体的爬取任务")
