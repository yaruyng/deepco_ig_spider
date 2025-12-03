# Instagram Spider

Instagram 数据采集工具，用于获取话题下的用户列表和帖子评论用户列表。

[English Documentation](README_EN.md)

## ✨ 功能特性

- 📌 **话题用户采集** - 获取指定话题标签下发帖的用户信息
- 💬 **帖子评论采集** - 获取指定帖子的评论用户列表（支持树形结构）
- 📊 **话题帖子+评论** - 批量获取话题下的帖子及其评论（每帖一个 Sheet）
- 🔐 **Session 持久化** - 登录状态自动保存，下次运行无需重新登录
- 📁 **多格式导出** - 支持导出为 Excel 和 JSON 格式

## 📦 安装

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/deepco_ig_spider.git
cd deepco_ig_spider
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 🚀 使用方法

### 交互模式（推荐）

```bash
python main.py
```

运行后会显示交互菜单：

```
请选择操作:
  1. 获取话题下的用户列表
  2. 获取帖子评论用户列表
  3. 获取话题下的帖子及评论（每帖一个sheet）
  4. 登录 (输入 sessionid)
  5. 登出
  6. 测试网络连接
  7. 退出
```

### 命令行模式

```bash
# 获取话题用户（最多获取 50 个帖子）
python main.py --hashtag python --max-posts 50

# 获取帖子评论用户
python main.py --media-id 1234567890 --max-comments 100
```

### 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--hashtag` | `-t` | 话题标签（不含#号） | - |
| `--media-id` | `-m` | 帖子的 media_id (pk) | - |
| `--max-posts` | - | 最多获取的帖子数量 | 50 |
| `--max-comments` | - | 最多获取的评论数量 | 100 |

## 🔐 登录说明

本工具需要 Instagram 账号的 Session 信息才能正常工作。

### 获取 Session 信息步骤：

1. 在浏览器中打开 Instagram 并登录
2. 按 `F12` 打开开发者工具
3. 切换到 `Network`（网络）标签页
4. 随便点击一个帖子，找到 API 请求
5. 在 `Request Headers` 中找到：
   - `Cookie` 中的 `sessionid`
   - `Cookie` 中的 `csrftoken`
   - `x-ig-www-claim`（可选）

### 登录方式

运行程序后选择 `4. 登录`，按提示输入获取到的信息。

登录成功后，Session 会自动保存到 `sessions/instagram_session.json`，下次运行时会自动加载。

## ⚙️ 配置说明

编辑 `config.py` 文件可以自定义配置：

```python
CONFIG = {
    # 每个话题最多获取的帖子数量
    "max_posts_per_hashtag": 50,
    
    # 每个帖子最多获取的评论数量
    "max_comments_per_post": 100,
    
    # 请求间隔（秒），避免被限流
    "request_delay": 2,
    
    # 输出目录
    "output_dir": "output",
    
    # 是否保存为 Excel
    "save_excel": True,
    
    # 是否保存为 JSON
    "save_json": False,
    
    # 是否保存原始 media JSON 数据
    "save_raw_json": False,
    
    # 请求超时时间（秒）
    "timeout": 30,
}
```

## 📂 输出文件

所有输出文件保存在 `output/` 目录下。

### 话题用户数据 (Excel)

| 字段 | 说明 |
|------|------|
| username | 用户名 |
| full_name | 全名 |
| pk | 帖子 ID |
| like_count | 点赞数 |
| comment_count | 评论数 |
| location_name | 位置名称 |
| location_address | 位置地址 |
| location_city | 城市 |
| text | 帖子内容 |
| text_translation | 翻译内容 |

### 评论用户数据 (Excel)

| 字段 | 说明 |
|------|------|
| level | 层级标记（子评论显示 └─） |
| username | 用户名 |
| full_name | 全名 |
| text | 评论内容 |
| comment_like_count | 评论点赞数 |
| child_comment_count | 子评论数 |
| pk | 评论 ID |
| media_id | 帖子 ID |

## 📁 项目结构

```
deepco_ig_spider/
├── main.py              # 主入口文件
├── ig_spider.py         # 爬虫核心模块
├── config.py            # 配置文件
├── requirements.txt     # 依赖列表
├── sessions/            # Session 存储目录
│   └── instagram_session.json
├── output/              # 输出文件目录
└── README.md
```

## ⚠️ 注意事项

1. **网络要求** - 需要能够访问 Instagram（可能需要 VPN）
2. **请求频率** - 请勿频繁请求，建议保持默认的请求间隔
3. **账号安全** - 请勿在不信任的环境下使用
4. **合规使用** - 请遵守 Instagram 的使用条款，仅用于合法用途

## 📄 License

MIT License
