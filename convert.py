# program: bookmark converter
# description: 将符合 Netscape 书签格式的 HTML 文件转换为单文件 HTML
# author: shihuaidexianyu
# date: 2025-11-18
# 
# 说明：
# 运行之后可以将当前目录下的符合 Netscape 书签格式的 HTML 文件
# 转换为一个包含内嵌 CSS/JS 的单文件 HTML 导航页面，方便离线浏览和分享。
# 生成的文件会在原文件名后添加 "_nav" 后缀，以避免覆盖原始文件。
#
# 使用方法：
# 1. 将符合 Netscape 书签格式(例如chrome导出的书签)的 HTML 文件放在与本脚本相同的目录下。
# 2. 运行脚本：python convert.py
# 3. 脚本会生成对应的单文件 HTML，文件名为原文件名加上 "_nav.html" 后缀。
#
# 注意事项：
# - 脚本假设输入的 HTML 文件符合 Netscape 书签格式。
# - 生成的 HTML 文件包含简单的搜索功能和响应式设计，适合在各种设备上浏览。
# - 如果需要自定义样式或功能，可以修改脚本中的 HTML 模板部分。
# 依赖项：
# 需要安装 BeautifulSoup 库，可以通过 pip 安装：
# pip install beautifulsoup4


import json
from bs4 import BeautifulSoup
from pathlib import Path

# 统一的工作目录
BASE_DIR = Path(__file__).resolve().parent

# 生成文件时附带的后缀，避免覆盖原始 HTML
OUTPUT_SUFFIX = "_nav.html"


def parse_bookmarks(file_path: Path):
    """解析 Netscape 格式的书签文件，提取一级分类及其链接"""
    if not file_path.exists():
        raise FileNotFoundError(f"书签文件不存在: {file_path}")

    text = file_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(text, "html.parser")

    bookmarks_data = []

    # Netscape 书签结构通常是 <DL><p><DT><H3>分类</H3><DL>...</DL>
    # 这里遍历所有包含 H3 的 DT，把其后面的兄弟 DL 当成该分类的内容容器
    for dt in soup.find_all("dt"):
        h3 = dt.find("h3")
        if not h3:
            continue

        category_name = h3.get_text(strip=True)
        if not category_name:
            continue

        # 示例：重命名某些系统文件夹
        if category_name == "Bookmarks bar":
            category_name = "常用收藏"

        # 先尝试从当前 DT 下找 DL；如果没有，再看下一个兄弟标签
        dl = dt.find("dl")
        if dl is None:
            sibling = dt.find_next_sibling("dl")
            if sibling:
                dl = sibling

        if dl is None:
            continue

        items = []

        # Netscape 导出通常是 <DL><p> 包裹若干 <DT>，此处通过祖先 DL 限定在当前分类
        direct_dts = [
            child
            for child in dl.find_all("dt")
            if child.find_parent("dl") is dl
        ]

        for child in direct_dts:
            a = child.find("a", recursive=False)
            if not a:
                continue
            title = a.get_text(strip=True) or a.get("href") or "未命名链接"
            url = a.get("href")
            if not url:
                continue

            icon = a.get("icon") or ""
            add_date = a.get("add_date") or ""

            items.append(
                {
                    "title": title,
                    "url": url,
                    "icon": icon,
                    "date": add_date,
                }
            )

        if items:
            bookmarks_data.append(
                {
                    "category": category_name,
                    "links": items,
                }
            )

    return bookmarks_data


def generate_html(data, output_file: Path):
    """生成包含 CSS/JS 的单文件 HTML"""

    # 确保输出的 JSON 安全嵌入到 <script> 中
    json_data = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的导航 | My Bookmarks</title>
    <style>
        :root {{
            --bg-color: #f4f6f8;
            --card-bg: #ffffff;
            --text-main: #333;
            --text-sub: #888;
            --accent: #007aff;
            --shadow: 0 4px 12px rgba(0,0,0,0.05);
            --shadow-hover: 0 8px 24px rgba(0,0,0,0.12);
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-color: #1a1a1a;
                --card-bg: #2c2c2c;
                --text-main: #e0e0e0;
                --text-sub: #aaa;
                --shadow: 0 4px 12px rgba(0,0,0,0.2);
            }}
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            transition: background-color 0.3s;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            padding: 40px 0;
            animation: fadeInDown 0.8s ease;
        }}

        .search-box {{
            width: 100%;
            max-width: 500px;
            padding: 15px 25px;
            border-radius: 30px;
            border: none;
            background: var(--card-bg);
            box-shadow: var(--shadow);
            font-size: 16px;
            color: var(--text-main);
            outline: none;
            transition: all 0.3s;
        }}

        .search-box:focus {{
            box-shadow: 0 0 0 2px var(--accent), var(--shadow);
            transform: scale(1.02);
        }}

        .category-section {{
            margin-bottom: 40px;
            opacity: 0;
            transform: translateY(20px);
            animation: fadeInUp 0.6s ease forwards;
        }}

        .category-title {{
            font-size: 1.2rem;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 4px solid var(--accent);
            color: var(--text-main);
            font-weight: 600;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}

        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 15px;
            display: flex;
            align-items: center;
            text-decoration: none;
            color: var(--text-main);
            box-shadow: var(--shadow);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            position: relative;
            overflow: hidden;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-hover);
        }}

        .card::after {{
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            background: radial-gradient(circle, rgba(255,255,255,0.3) 10%, transparent 10.01%);
            background-repeat: no-repeat;
            background-position: 50%;
            transform: scale(10, 10);
            opacity: 0;
            transition: transform .5s, opacity 1s;
            pointer-events: none;
        }}

        .card:active::after {{
            transform: scale(0, 0);
            opacity: .3;
            transition: 0s;
        }}

        .card-icon {{
            width: 32px;
            height: 32px;
            margin-right: 12px;
            border-radius: 6px;
            object-fit: contain;
        }}

        .card-info {{
            flex: 1;
            overflow: hidden;
        }}

        .card-title {{
            font-size: 14px;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .no-result {{
            text-align: center;
            color: var(--text-sub);
            padding: 20px;
            display: none;
        }}

        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes fadeInUp {{
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>My Bookmark Space</h1>
        <input type="text" id="searchInput" class="search-box" placeholder="搜索书签 / Type to search...">
    </div>

    <div id="content-area"></div>
    <div id="no-result" class="no-result">没有找到相关书签</div>
</div>

<script>
    const bookmarksData = {json_data};

    const contentArea = document.getElementById('content-area');
    const searchInput = document.getElementById('searchInput');
    const noResult = document.getElementById('no-result');

    function render(filterText = '') {{
        contentArea.innerHTML = '';
        let hasResult = false;
        let delayCounter = 0;

        const keyword = filterText.toLowerCase();

        bookmarksData.forEach(group => {{
            const filteredLinks = group.links.filter(link => {{
                const title = (link.title || '').toLowerCase();
                const url = (link.url || '').toLowerCase();
                return !keyword || title.includes(keyword) || url.includes(keyword);
            }});

            if (filteredLinks.length > 0) {{
                hasResult = true;

                const section = document.createElement('div');
                section.className = 'category-section';
                section.style.animationDelay = `${{delayCounter * 0.1}}s`;
                delayCounter++;

                const h2 = document.createElement('div');
                h2.className = 'category-title';
                h2.textContent = group.category;
                section.appendChild(h2);

                const grid = document.createElement('div');
                grid.className = 'grid';

                filteredLinks.forEach(link => {{
                    const a = document.createElement('a');
                    a.className = 'card';
                    a.href = link.url;
                    a.target = '_blank';

                    const img = document.createElement('img');
                    img.className = 'card-icon';
                    img.src = link.icon || 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjY2NjIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiLz48bGluZSB4MT0iMiIgeTE9IjEyIiB4Mj0iMjIiIHkyPSIxMiIvPjxwYXRoIGQ9Ik0xMiAyYTE1LjMgMTUuMyAwIDAgMSA0IDEwIDE1LjMgMTUuMyAwIDAgMS00IDEwIDE1LjMgMTUuMyAwIDAgMS00LTEwIDE1LjMgMTUuMyAwIDAgMSA0LTEweiIvPjwvc3ZnPg==';

                    const info = document.createElement('div');
                    info.className = 'card-info';

                    const titleEl = document.createElement('div');
                    titleEl.className = 'card-title';
                    titleEl.textContent = link.title;

                    info.appendChild(titleEl);
                    a.appendChild(img);
                    a.appendChild(info);
                    grid.appendChild(a);
                }});

                section.appendChild(grid);
                contentArea.appendChild(section);
            }}
        }});

        noResult.style.display = hasResult ? 'none' : 'block';
    }}

    render();

    searchInput.addEventListener('input', (e) => {{
        render(e.target.value);
    }});

    document.addEventListener('keydown', (e) => {{
        if (e.key === '/' && document.activeElement !== searchInput) {{
            e.preventDefault();
            searchInput.focus();
        }}
    }});
</script>

</body>
</html>
"""

    output_file.write_text(html_template, encoding="utf-8")
    print(f"转换成功！请打开 {output_file.name} 查看效果。")


if __name__ == "__main__":
    html_files = sorted(
        f
        for f in BASE_DIR.glob("*.html")
        if (
            f.is_file()
            and not f.name.endswith(OUTPUT_SUFFIX)
            and not f.name.endswith(".tmp.html")
            and not f.stem.startswith("my_nav_page")
        )
    )

    if not html_files:
        print("未在目录中找到需要处理的 HTML 文件。")
        raise SystemExit(0)

    generated_files = []

    for html_file in html_files:
        print(f"正在处理 {html_file.name} ...")
        try:
            data = parse_bookmarks(html_file)
        except FileNotFoundError as exc:
            print(f"错误：{exc}")
            continue

        if not data:
            print(f"警告：{html_file.name} 未解析到任何书签，已跳过。")
            continue

        output_file = html_file.with_name(f"{html_file.stem}{OUTPUT_SUFFIX}")
        generate_html(data, output_file)
        generated_files.append(output_file.name)

    if generated_files:
        print("\n已生成以下文件：")
        for filename in generated_files:
            print(f" - {filename}")
    else:
        print("没有成功生成任何文件，请检查源 HTML 是否符合 Netscape 书签格式。")