# 此芯 Agentic AI 创新应用大赛技术开发指南

本仓库是《此芯 Agentic AI 创新应用大赛技术开发指南》v0.8.5 的 Markdown / Read the Docs 版本，使用 Sphinx、MyST Parser 和 Read the Docs Theme 构建。

## 本地预览

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
sphinx-build -W -b html docs docs/_build/html
```

打开 `docs/_build/html/index.html` 查看本地站点。

## Read the Docs

根目录的 `.readthedocs.yaml` 已与当前 Sphinx 工程匹配。GitHub 仓库连接到 Read the Docs 后会自动构建。

## 路径规则

正文位于 `docs/`。目录和文件名统一采用英文小写 `kebab-case`，页面标题保留原文中文编号。
