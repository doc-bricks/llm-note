# llm-note

**llm-note** 是面向 LLM agent 的本地优先笔记引擎。它提供 SQLite 笔记日志和纯文本笔记本，不依赖托管服务或外部运行时依赖。

## 功能

- 保存结构化笔记、日志条目、分类、情绪值和提升标记。
- 使用可移植的纯文本笔记本。
- 通过 Python 或 CLI 搜索笔记。
- 创建头脑风暴条目，之后可转为任务、wiki 页面或 issue。
- 内置六种用户消息语言。

## 快速开始

```bash
pip install -e .
llm-note --locale zh-Hans write "发布前检查隐私" --cat release
llm-note --locale zh-Hans search 隐私
```

## 许可证

[MIT](LICENSE)
