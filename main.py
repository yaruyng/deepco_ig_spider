# -*- coding: utf-8 -*-
"""
Instagram Spider 主入口
用于获取IG话题下用户列表和帖子评论用户列表
"""
import argparse

from ig_spider import IGSpider


def main():
    parser = argparse.ArgumentParser(
        description="Instagram Spider - 获取话题用户和帖子评论用户",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 交互模式（推荐）
  python main.py

  # 获取话题 #python 下的用户（最多50个帖子）
  python main.py --hashtag python --max-posts 50

  # 获取特定帖子的评论用户
  python main.py --post https://www.instagram.com/p/XXXXX/ --max-comments 100
        """
    )
    
    parser.add_argument(
        "--hashtag", "-t",
        type=str,
        help="要获取的话题标签（不含#号）"
    )
    
    parser.add_argument(
        "--media-id", "-m",
        type=str,
        help="要获取评论的帖子 media_id (pk)"
    )
    
    parser.add_argument(
        "--max-posts",
        type=int,
        default=50,
        help="话题最多获取的帖子数量（默认50）"
    )
    
    parser.add_argument(
        "--max-comments",
        type=int,
        default=100,
        help="帖子最多获取的评论数量（默认100）"
    )
    
    args = parser.parse_args()
    
    # 交互模式
    if not args.hashtag and not args.media_id:
        interactive_mode()
        return
    
    # 命令行模式
    spider = IGSpider()
    
    if not spider.is_logged_in:
        print("⚠ 未登录，请先登录")
        spider.interactive_login()
    
    if args.hashtag:
        print(f"\n📌 任务: 获取话题 #{args.hashtag} 下的用户")
        users = spider.get_hashtag_users(args.hashtag, args.max_posts)
        if users:
            spider.save_results(users, f"hashtag_{args.hashtag}_users")
        print(f"   结果: 获取到 {len(users)} 个用户")
    
    if args.media_id:
        print(f"\n💬 任务: 获取帖子评论用户")
        users = spider.get_post_comment_users(args.media_id, args.max_comments)
        if users:
            spider.save_results(users, f"post_{args.media_id}_comment_users", data_type="comment")
        print(f"   结果: 获取到 {len(users)} 个评论用户")


def interactive_mode():
    """交互模式"""
    print("=" * 60)
    print("🔍 Instagram Spider - 交互模式")
    print("=" * 60)
    
    spider = IGSpider()
    
    # 显示登录状态
    print(f"\n📱 当前状态: {spider.get_login_status()}")
    
    # 测试连接
    spider.test_connection()
    
    # 如果未登录，提示登录
    if not spider.is_logged_in:
        print("\n⚠ 提示: 需要登录才能获取 Instagram 数据")
        do_login = input("是否现在登录? (y/n): ").strip().lower()
        if do_login == 'y':
            spider.interactive_login()
    
    while True:
        print(f"\n📱 登录状态: {spider.get_login_status()}")
        print("\n请选择操作:")
        print("  1. 获取话题下的用户列表")
        print("  2. 获取帖子评论用户列表")
        print("  3. 获取话题下的帖子及评论（每帖一个sheet）")
        print("  4. 登录 (输入 sessionid)")
        print("  5. 登出")
        print("  6. 测试网络连接")
        print("  7. 退出")
        
        choice = input("\n请输入选项 (1-7): ").strip()
        
        if choice == "1":
            if not spider.is_logged_in:
                print("⚠ 请先登录后再操作")
                continue
            
            hashtag = input("请输入话题标签（不含#号）: ").strip()
            if not hashtag:
                print("⚠ 话题不能为空")
                continue
            
            max_posts = input("最多获取帖子数量（默认50）: ").strip()
            max_posts = int(max_posts) if max_posts.isdigit() else 50
            
            users = spider.get_hashtag_users(hashtag, max_posts)
            if users:
                spider.save_results(users, f"hashtag_{hashtag}_users")
        
        elif choice == "2":
            if not spider.is_logged_in:
                print("⚠ 请先登录后再操作")
                continue
            
            media_id = input("请输入帖子的 media_id (pk): ").strip()
            if not media_id:
                print("⚠ media_id 不能为空")
                continue
            
            max_comments = input("最多获取评论数量（默认100）: ").strip()
            max_comments = int(max_comments) if max_comments.isdigit() else 100
            
            users = spider.get_post_comment_users(media_id, max_comments)
            if users:
                spider.save_results(users, f"post_{media_id}_comment_users", data_type="comment")
        
        elif choice == "3":
            if not spider.is_logged_in:
                print("⚠ 请先登录后再操作")
                continue
            
            hashtag = input("请输入话题标签（不含#号）: ").strip()
            if not hashtag:
                print("⚠ 话题不能为空")
                continue
            
            max_posts = input("最多获取帖子数量（默认10）: ").strip()
            max_posts = int(max_posts) if max_posts.isdigit() else 10
            
            max_comments = input("每个帖子最多获取评论数量（默认50）: ").strip()
            max_comments = int(max_comments) if max_comments.isdigit() else 50
            
            posts_data = spider.get_hashtag_posts_with_comments(hashtag, max_posts, max_comments)
            if posts_data:
                spider.save_posts_with_comments(posts_data, f"hashtag_{hashtag}_posts_comments")
        
        elif choice == "4":
            if spider.is_logged_in:
                print(f"✓ 当前已登录")
                switch = input("是否切换账号? (y/n): ").strip().lower()
                if switch != 'y':
                    continue
                spider.logout()
            spider.interactive_login()
        
        elif choice == "5":
            if spider.is_logged_in:
                spider.logout()
            else:
                print("⚠ 当前未登录")
        
        elif choice == "6":
            spider.test_connection()
        
        elif choice == "7":
            print("\n👋 再见！")
            break
        
        else:
            print("⚠ 无效选项，请重新选择")


if __name__ == "__main__":
    main()
