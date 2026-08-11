project = "此芯 Agentic AI 创新应用大赛技术开发指南"
author = "CIX"
copyright = "2026, CIX"
release = "0.8.5"

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
html_show_sourcelink = True
html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

copybutton_prompt_text = r"^(?:\$ |>>> |\.\.\. )"
copybutton_prompt_is_regexp = True
