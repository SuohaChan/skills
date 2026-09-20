---
name: obsidian-rag
description: Use the connected Obsidian RAG MCP whenever a request depends on the user's personal notes, learning records, project decisions, codebase knowledge, previous explanations, or local Markdown sources. Search the user's notes before answering those questions, read the relevant source when snippets are insufficient, and ground the response in citations. Do not use it for ordinary general-knowledge questions unless local context is requested.
compatibility: Requires an MCP client connection to the obsidian-rag server exposing search_notes, read_note, and index_status.
---

# Obsidian RAG retrieval

Use the local note repository as evidence when the user asks about their own knowledge, projects, previous decisions, or learning history.

## Retrieval workflow

1. Classify the request. Use this skill for personal notes, project history, design choices, implementation details, and questions that refer to something the user previously recorded.
2. Search first with `search_notes`. Use a focused query containing the important concept and the user's wording. Start with a small limit such as 4–6.
3. Inspect the citations. Prefer results whose source, heading, and snippet directly address the question.
4. Call `read_note` for the most relevant source when the snippet is incomplete, when several notes conflict, or when the answer depends on surrounding context. Use the cited line range as the starting point and expand only as needed.
5. Answer from the retrieved evidence. Separate what the notes state from any inference. Cite the note path and heading or line range so the user can return to the source.
6. If the search returns no useful result, say that the local knowledge base does not contain enough evidence. Then ask whether the user wants a general explanation or a new note created.

## Tool selection

- `search_notes(query, limit)`: semantic retrieval of indexed note chunks. This is the normal first call.
- `read_note(source, start_line, max_lines)`: read the original Markdown around a citation. The source must be a vault-relative path in the server whitelist.
- `index_status()`: inspect indexed file count, chunk count, embedding configuration, and index directory when freshness or configuration matters. It does not rebuild the index.

## Answer rules

- Treat Markdown as the source of truth for the user's recorded knowledge.
- Do not present a retrieved snippet as a complete note when surrounding context was not read.
- Keep citations close to the claims they support.
- When sources disagree, show the disagreement and identify which note is newer or more specific if that information is available.
- Do not query the local RAG for every generic question; use it when the answer depends on the user's repository.
- Do not invent a citation, file path, heading, or line range.

## Index freshness

The MCP server reads the existing index. If the user has recently changed notes and results look stale, call `index_status` and explain that the project must be refreshed with:

```powershell
cd D:\project\obsidian-rag-langchain
uv run obsidian-rag index
```

After rebuilding, restart the MCP server if it is already running so it reopens the updated Chroma index.

## Examples

### Personal project question

User: “我们现在的 RAG 为什么选 Chroma？”

Action: search for the project note and vector-database selection note, read the relevant sections, then explain the recorded reasons and any current limitations.

### Generic question

User: “什么是 BM25？”

Action: answer generally unless the user asks how BM25 is used in their RAG notes. If they do, search the local notes and connect the explanation to the project.
