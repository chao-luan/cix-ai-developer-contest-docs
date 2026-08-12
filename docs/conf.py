project = "2026此芯科技Agentic AI开发者大赛技术开发指南"
author = "CIX"
copyright = "2026, CIX"

# 不显示版本号
release = ""

extensions = [
    "myst_parser",
    "sphinx_copybutton",
]

source_suffix = {
    ".md": "markdown",
}

master_doc = "index"
language = "zh_CN"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
]
myst_heading_anchors = 4

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# 关键：不要让 Sphinx 在页面标题后追加站点名/version/documentation
html_title = ""
html_short_title = ""

html_show_sourcelink = True

html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "includehidden": True,
    "titles_only": False,
}

copybutton_prompt_text = r"^(?:\$ |>>> |\.\.\. )"
copybutton_prompt_is_regexp = True
