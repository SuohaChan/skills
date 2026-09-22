---
name: obsidian-cli-knowledge-base
description: Manage an Obsidian knowledge-base vault with the official Obsidian CLI. Use whenever the user asks to read, search, create, edit, classify, move, rename, archive, review, or automate notes, properties, tags, links, tasks, templates, or vault structure; follow the target vault's conventions and protect documented private or excluded paths.
---

# Obsidian CLI Knowledge Base

Use this skill for any requested operation on an Obsidian knowledge-base vault. Resolve the target vault and its local rules before acting; do not silently substitute a fixed path, taxonomy, or repository.

## CLI-first rule

- Prefer the official Obsidian CLI for all note operations. Common commands include `read`, `search`, `search:context`, `create`, `append`, `prepend`, `move`, `rename`, `open`, `file`, `files`, `property:set`, `property:remove`, `properties`, `tags`, `tasks`, `links`, `backlinks`, `unresolved`, `orphans`, `deadends`, `daily`, and `templates`.
- Use the `obsidian` command after PATH is available. The desktop app must be running for the official CLI.
- If the command is unavailable, diagnose the installer, registration, PATH, and running-app state before falling back to direct file access.
- Use `path=` for mutations when the exact vault-relative path is known. Inspect the target with `file` or `read` before changing it.
- Do not overwrite, delete, bulk-move, or rewrite notes unless the user requested that scope. Prefer a recoverable move to the target vault's archive location over permanent deletion.
- After every mutation, re-read the target and run a focused validation such as `properties`, `tags`, `unresolved`, or `files`.

## Read-only and scope boundaries

- For read-only audits, reviews, and simulations, do not execute `create`, `append`, `prepend`, `move`, `rename`, `property:set`, or `property:remove`. Use only read-only commands and describe planned mutations without performing them.
- Before any vault-wide inventory or review, read the vault policy for private or excluded paths. Exclude documented private paths from `files`, `search`, `tags`, `properties`, `tasks`, `links`, `backlinks`, `unresolved`, `orphans`, and `deadends` checks unless the user explicitly authorizes access.
- If the CLI cannot reliably scope a requested scan, stop and report that limitation.

## Read the vault's own rules first

- Discover or confirm the target with `obsidian vaults verbose` and `obsidian vault info=path`.
- Before making changes, look for a canonical vault policy, schema, index, or home note and read it through the CLI. A note such as `知识库规范.md` is only an example; do not assume a particular filename or folder layout in another vault.
- Treat the vault's own documentation as the source of truth for folders, properties, tags, templates, naming, and archival rules. This skill supplies CLI-first behavior, not a hard-coded personal taxonomy.
- If the vault has no rules, use judgment to propose a small convention and record it in a policy note before broad migrations. Do not silently impose a large framework.

## Shared note safety

- Preserve existing property names, types, allowed values, tags, links, and templates. Do not invent a second schema when the vault already has one.
- Do not add tags merely to force an uncertain classification, and do not create links just to eliminate orphan counts.
- Prefer one source of truth: link to an existing concept or update its existing note rather than duplicating a summary.
- Keep taxonomy changes separate from ordinary note edits. A redesign or migration requires an explicit scope and an inventory first.

## Read the relevant reference by task

Read only the reference needed for the requested branch:

- For capture, creation, archiving, or review, read [`references/workflows.md`](references/workflows.md).
- For folders, properties, tags, links, templates, or note organization, read [`references/note-organization.md`](references/note-organization.md).
- For a user-confirmed commit or push of vault changes, read [`references/git-delivery.md`](references/git-delivery.md). A read-only task must not enter that flow.

Do not read or apply a reference whose task branch was not requested. When a task spans branches, read each relevant reference and keep their scopes separate.

## Multiple vaults

Use `vault=<name>` or `vault=<id>` when the user explicitly targets another known vault. Do not assume that folders, properties, tags, templates, or links are shared across vaults; inspect the target vault's own rules before operating.

## Completion criteria

- Read-only work reports the commands and scope inspected without making mutations.
- Every mutation reports the exact target, re-reads the result, and runs a focused validation.
- If a rule, path, schema, command, or target cannot be confirmed, stop at the boundary and report the limitation instead of guessing.
