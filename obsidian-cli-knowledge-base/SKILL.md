---
name: obsidian-cli-knowledge-base
description: Manage an Obsidian knowledge-base vault with the official Obsidian CLI. Use whenever the user asks to read, search, create, edit, classify, move, rename, archive, review, or automate notes, properties, tags, links, tasks, templates, or vault structure; follow the target vault's conventions and protect documented private or excluded paths.
---

# Obsidian CLI Knowledge Base

Follow this skill's workflow for the requested vault operation.

## CLI-first rule

- Prefer the official Obsidian CLI for all note operations. Common commands include `read`, `search`, `search:context`, `create`, `append`, `prepend`, `move`, `rename`, `open`, `file`, `files`, `property:set`, `property:remove`, `properties`, `tags`, `tasks`, `links`, `backlinks`, `unresolved`, `orphans`, `deadends`, `daily`, and `templates`.
- Use the `obsidian` command after PATH is available. The desktop app must be running for the official CLI.
- If the command is unavailable, diagnose the installer, registration, PATH, and running-app state before falling back to direct file access.
- Use `path=` for mutations when the exact vault-relative path is known. Inspect the target with `file` or `read` before changing it.
- Do not overwrite, delete, bulk-move, or rewrite notes unless the user requested that scope. Prefer a recoverable move to the target vault's archive location over permanent deletion.
- After every mutation, re-read the target and run a focused validation such as `properties`, `tags`, `unresolved`, or `files`.
- For read-only audits, reviews, and simulations, do not execute `create`, `append`, `prepend`, `move`, `rename`, `property:set`, or `property:remove`. Use only read-only commands and describe planned mutations without performing them.
- Before any vault-wide inventory or review, read the vault policy for private or excluded paths. Exclude documented private paths from `files`, `search`, `tags`, `properties`, `tasks`, `links`, `backlinks`, `unresolved`, `orphans`, and `deadends` checks unless the user explicitly authorizes access. If the CLI cannot reliably scope a requested scan, stop and report that limitation.

## Configurable Git completion policy

Git is the delivery layer for completed vault mutations; it is not a replacement for the official Obsidian CLI. This skill does not contain a repository URL, vault path, branch name, or remote name. Resolve them from the target vault and its existing Git configuration at runtime.

- For a read-only task, do not stage, commit, or push anything.
- For a task that changes notes or vault documentation, treat validation and a clear local change report as the default completion step. Commit only when the user explicitly asks for it or the vault's own policy requires it; push only after the user explicitly confirms the remote operation.
- When commit or push is requested, resolve the repository with `git -C <target-vault> rev-parse --show-toplevel`; inspect `git status --short`, `git remote -v`, the current branch, and its upstream. Never assume `origin`, `main`, or any particular hosting service.
- Capture the repository status before editing. If a target path already has a pre-existing modification or is untracked, separate the task's diff from the baseline; if that cannot be done reliably with patch-level staging, stop before committing and report the overlap.
- Preserve unrelated pre-existing work. Stage only the paths changed by the current task with `git add -- <specific paths>`; do not use `git add .` by default.
- Before committing, re-read changed notes, run the relevant Obsidian CLI validation, and run `git diff --check`. Group the current task's related mutations into one concise commit with a meaningful message.
- If the user confirms a push, use the resolved configured upstream. Never force-push, reset, discard changes, overwrite a remote, or create a remote merely to complete this workflow.
- After committing or pushing, verify `git status --short --branch` and report the commit and upstream result. If there is no repository, remote, upstream, authentication, network access, or a merge/conflict condition, preserve local changes, report the exact blocker, and stop the Git step safely.
- Do not commit secrets, tokens, private keys, or local device state. Check the repository's ignore rules before staging suspicious files.

The Git behavior may be configured per vault by its own policy note or by an explicit user request. The safe default is local validation and reporting; the vault's own conventions still control note structure, metadata, links, and folders.

## Read the vault's own rules first

- Discover or confirm the target with `obsidian vaults verbose` and `obsidian vault info=path`.
- Before making changes, look for a canonical vault policy, schema, index, or home note and read it through the CLI. A note such as `知识库规范.md` is only an example; do not assume a particular filename or folder layout in another vault.
- Treat the vault's own documentation as the source of truth for folders, properties, tags, templates, naming, and archival rules. This skill supplies the CLI-first behavior, not a hard-coded personal taxonomy.
- If the vault has no rules, use judgment to propose a small convention and record it in a policy note before broad migrations. Do not silently impose a large framework.

## Apply the vault's model, not a fixed model

- Use the existing folder convention when one exists. If the vault uses PARA, understand Projects, Areas, Resources, and Archives as lifecycle buckets; if it uses another method, follow that method instead.
- Use the vault's templates when available. If a requested note type has no template, create a minimal format consistent with nearby notes or propose a template for approval.
- Do not create folders, properties, tags, or links merely to satisfy a framework. They should make capture, retrieval, reuse, or review easier.

Keep taxonomy changes separate from ordinary note edits. A redesign or migration requires an explicit scope and should be preceded by an inventory.

## Interpret metadata and connections

- Preserve existing property names, types, and allowed values. Do not invent a second schema when the vault already has one.
- When a schema exists, use YAML frontmatter for durable notes and apply its required fields through CLI property commands or a matching template.
- Before setting a property, check the vault schema and existing property statistics. Use an explicit CLI type, validate enumerated values and ISO dates, preserve list properties as lists, and read the exact property back after writing. If the name, type, value, or format conflicts with the schema, refuse the mutation and report the conflict.
- When no schema exists, prefer a small set of structured fields whose meaning is clear from the vault's use case; document the choice in the vault policy.
- Treat tags as cross-cutting retrieval hints and links as semantic relationships. Whether a vault prefers tags, links, MOCs, Bases, or a combination is a local design choice.
- Do not add tags merely to force an uncertain classification, and do not create links just to eliminate orphan counts.

## Writing discipline: link, don't duplicate

Before writing or expanding a note, apply these rules:

1. **Read the index first.** Check the vault's index / MOC notes and run `search` to confirm whether the concept already has a note.
2. **Link instead of copy.** If it exists, reference it with a wikilink, or update the existing note rather than writing a second summary somewhere else. Link the first occurrence only, to avoid link noise.
3. **Extract general concepts into their own note.** If a knowledge point is structural or cross-cutting and likely to be referenced by two or more notes, give it its own note and let specific notes link to it. Keep single-topic details in the specific note.
4. **Keep one source of truth.** Duplicated content drifts and ends up contradicting itself.
5. **Keep concept notes clean; put applications in the consumer note.** A concept note describes the concept itself. Usage and scenarios belong in the note that uses it, linked back with a wikilink. Ask: does this content still hold without the consumer? If yes, it belongs in the concept note; if no, keep it in the consumer note.
6. **Lead with the underlying structure.** For concept or data-structure notes, explain what the thing is at the implementation level before how to use it. A useful order is: one-line conclusion → underlying structure → usage → pitfalls → related links.

## Sub-folder grouping inside a topic

When a topic folder grows, group notes by content type instead of leaving everything flat. Use `概念/` for concepts, `技术/` for standards and protocols, `设备/` for hardware, and `流程/` for flows or mechanisms when those categories fit the vault's existing model. Keep layer overviews and index notes at the topic root. Create sub-folders only when there is enough content to justify them; a folder with one or two notes can stay flat. Move notes with `obsidian move` so links update automatically, then verify with `unresolved`.

## Standard workflows

### Capture and creation

1. If the destination is uncertain, use the vault's capture/inbox convention.
2. Select the closest existing template or note pattern.
3. Check whether the intended path already exists. If it does, do not use `overwrite`; update the existing note, link to it, or ask the user to choose another path.
4. Fill in the content first, then add only the properties, tags, and links supported by the vault's rules and useful for retrieval.
5. Verify the created path, frontmatter, and links.

### Archiving

1. Inspect the note and confirm it is complete, inactive, or obsolete.
2. Resolve the archive location and check for a destination collision; stop rather than overwrite, merge, or silently rename. Record the source path, current properties, and the permitted-scope `unresolved` baseline before moving.
3. Move it with CLI to the vault's archive location, if one exists, then apply the vault's archive status or metadata while retaining content, provenance, tags, and useful links.
4. Re-read the moved file and assert that the destination exists, the source is absent, the vault-defined archive metadata is present, and the permitted-scope `unresolved` count has not increased. If a step fails, report the intermediate state instead of silently continuing.

### Review

Within the permitted scope, use the CLI to inspect `tasks todo verbose`, `unresolved verbose`, `orphans total`, `deadends total`, `tags counts`, and `properties counts`. Treat the results as signals for review, not automatic cleanup instructions.

## Multiple vaults

Use `vault=<name>` or `vault=<id>` when the user explicitly targets another known vault. Do not assume that folders, properties, tags, templates, or links are shared across vaults; inspect the target vault's own rules before operating.
