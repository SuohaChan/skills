# 评测状态

## 已完成

- 已保存变更前的 `obsidian-rag` 快照：`baseline/obsidian-rag.SNAPSHOT.md`。
- `obsidian-rag/evals/evals.json` JSON 可解析。
- `obsidian-rag/evals/holdout.json` JSON 可解析。
- 仓库结构检查通过：`python .\scripts\validate_all.py`。
- 主 Skill 保留了检索顺序、证据规则、引用规则和失败边界。
- 明显依赖当前环境的索引刷新命令已移动到 `obsidian-rag/references/index-freshness.md`。
- 未修改 `anime-schedule`、`desktop-screenshot`、`power-on-computer`。

## 尚未完成

- 当前评测通过 Claude CLI 注入旧版/新版 Skill 文本，验证路由和证据策略；没有连接 Obsidian RAG MCP，因此没有产生真实的笔记检索内容或端到端引用质量结论。
- 需要在具备 MCP 的 Agent 会话中复核工具实际调用、检索结果和最终回答质量。

## 评测纪律

在获得真实运行结果前，不把静态检查通过写成行为评测通过，也不填写推测的分数。后续运行应分别保存旧版和新版结果，并对训练集与 holdout 使用相同的评分标准。

## 当前策略评测结果

结果文件：`evaluation-results/policy-eval.json`。

| 数据集 | 旧版 | 新版 | 结论 |
| --- | ---: | ---: | --- |
| 训练集触发判断 | 8/8 | 8/8 | 无回归 |
| Holdout 触发判断 | 3/4 | 4/4 | 新版改善 1 个近邻边界 |

改善案例：`holdout-citation-boundary`。旧版将“只告诉我原文支持的结论”误判为不需要本地检索；新版会先检索并在回答中区分直接证据与推断。
