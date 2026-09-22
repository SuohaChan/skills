# Index freshness for the current local adapter

This reference documents the current local deployment only. It is replaceable when the indexing project, command, or MCP lifecycle changes.

The MCP server reads the existing index. If recently changed notes do not appear, call `index_status` first and report the freshness limitation. To rebuild the current project index:

```powershell
cd D:\project\obsidian-rag-langchain
uv run obsidian-rag index
```

After rebuilding, restart the MCP server if it is already running so it reopens the updated Chroma index. Do not present this path or command as a universal requirement for other Obsidian RAG adapters.
