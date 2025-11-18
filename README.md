# Bookmark Converter (书签转换工具)

> 将浏览器导出的 HTML 书签转换为美观、可交互的单文件导航页。

**作者**: shihuaidexianyu  
**日期**: 2025-11-18

## 项目简介

这是一个 Python 脚本，用于将符合 **Netscape Bookmark File Format**（通常由 Chrome、Edge、Firefox 等浏览器导出的书签文件格式）的 HTML 文件，转换为一个现代化的、包含内嵌 CSS 和 JavaScript 的单文件 HTML 导航页面。

转换后的页面具备搜索功能和响应式设计，所有资源（样式、脚本、图标数据）均打包在一个文件中，非常适合设为浏览器主页、离线浏览或分享给他人。

## 功能特性

* **零依赖单文件**：生成的 HTML 文件内嵌了所有的 CSS 样式和 JS 脚本，无需联网加载外部资源。
* **安全转换**：脚本会自动在原文件名后添加 `_nav` 后缀作为输出文件名（例如 `bookmarks.html` -> `bookmarks_nav.html`），**不会覆盖**原始文件。
* **搜索功能**：内置实时搜索框，可快速过滤查找书签。
* **响应式设计**：适配桌面端和移动端屏幕。
* **批量处理**：脚本会自动扫描当前目录下符合格式的 HTML 文件进行转换。

## 环境依赖

在运行脚本之前，请确保您的环境中已安装 Python 3.x，并安装了以下依赖库：

* **BeautifulSoup4**: 用于解析 HTML 文件结构。

### 安装依赖

```bash
pip install beautifulsoup4
````

## 使用方法

1.  **导出书签**：
    从您的浏览器中导出书签（通常为 `.html` 格式），确保其为 Netscape 格式（大多数现代浏览器默认即为此格式）。

2.  **放置文件**：
    将导出的书签 HTML 文件（例如 `bookmarks_18_11_2025.html`）放置在与本脚本 (`convert.py`) 相同的目录中。

3.  **运行脚本**：
    在终端或命令行中运行以下命令：

    ```bash
    python convert.py
    ```

4.  **查看结果**：
    运行完成后，当前目录下会生成一个新的 HTML 文件（例如 `bookmarks_18_11_2025_nav.html`）。双击该文件即可在浏览器中查看您的新导航页。

## 注意事项

  * 脚本默认假设输入的 HTML 文件符合 Netscape 书签标准格式。如果解析失败，请检查文件来源。
  * 如果您懂一些前端知识（HTML/CSS），可以自行修改脚本中的 `generate_html` 模板部分，以自定义页面配色或布局。

## 目录结构示例

```text
.
├── convert.py                  # 本脚本
├── bookmarks_2025.html         # 您导出的原始书签文件 (输入)
└── bookmarks_2025_nav.html     # 脚本自动生成的导航页 (输出)
```

## License

MIT License
