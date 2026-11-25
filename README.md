# Agent 学习仓库（Python）

从普通开发转向 AI Agent 开发的练习。每一课是一个 Jupyter Notebook，从上往下一格一格运行，旁边都有和 C# 的对照。

| 课 | 内容 | 学到什么 |
|---|---|---|
| [01_doc_extract](01_doc_extract.ipynb) | 发票文字 → 校验过的 Python 对象 | 结构化输出、Pydantic 校验、带错误重试、准确率评估 |
| [02_tool_calling](02_tool_calling.ipynb) | 订单客服助手 | 工具定义、手写 Agent 循环、对话历史 |
| [03_mcp](03_mcp.ipynb) + [03_order_server.py](03_order_server.py) | 把第 2 课的订单工具做成 MCP Server | MCP 的 Host / Client / Server、tools 和 resources、stdio 传输、接入 Claude Code |
| [04_rag](04_rag.ipynb) + [knowledge/](knowledge/) | 订单客服知识库问答 | 切块、Embedding、向量检索 + BM25 混合检索、带引用回答、Agentic RAG、检索评估 |
| 05（计划） | 记忆与上下文工程 | 长对话压缩、摘要、跨会话记忆 |

## 开始

```bash
brew install uv            # Python 的包管理 + 虚拟环境工具，相当于 dotnet CLI + NuGet
uv sync                    # 按 pyproject.toml 装好 Python 和依赖，生成 .venv/
cp .env.example .env       # 然后在 .env 里填 LLM_API_KEY
uv run jupyter lab         # 浏览器里打开 notebook
```

也可以直接用 VS Code 打开 `.ipynb`，右上角内核选 `.venv`。

## 学习方式

1. **Notebook 用来学**：每格代码跑完马上看到结果，改一个参数再跑一次，适合做实验。
2. **把理解的写回去**：觉得哪里懂了，就在 notebook 里加一格 Markdown 用自己的话写下来。
3. **从第 3 课开始写 `.py`**：MCP Server 要作为独立进程运行，所以写成正常的 Python 文件；notebook 只用来当客户端做实验。

## 第 3 课的 MCP Server 单独怎么用

```bash
# 官方调试界面（MCP 版的 Swagger UI），需要 Node.js
npx @modelcontextprotocol/inspector uv run 03_order_server.py

# 接进 Claude Code（路径换成本仓库的绝对路径）
claude mcp add order-service -- uv run --directory /你的路径/agent-learning-py 03_order_server.py
```

> 用的是官方 `mcp` 包 2.x（`from mcp.server.mcpserver import MCPServer`）。网上很多教程是 1.x 的 `FastMCP` 写法，概念一样，导入路径不同。
