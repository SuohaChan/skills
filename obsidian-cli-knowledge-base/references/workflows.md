# Obsidian CLI workflows

Read this file only for capture/creation, archiving, or review requests. The main Skill's CLI-first and safety boundaries still apply.

## Capture and creation

1. If the destination is uncertain, use the vault's capture or inbox convention.
2. Select the closest existing template or note pattern.
3. Check whether the intended path already exists. If it does, do not use `overwrite`; update the existing note, link to it, or ask the user to choose another path.
4. Fill in the content first, then add only the properties, tags, and links supported by the vault's rules and useful for retrieval.
5. Verify the created path, frontmatter, and links with the CLI.

## Archiving

1. Inspect the note and confirm it is complete, inactive, or obsolete.
2. Resolve the archive location and check for a destination collision. Stop rather than overwrite, merge, or silently rename. Record the source path, current properties, and the permitted-scope `unresolved` baseline before moving.
3. Move it with the CLI to the vault's archive location, if one exists, then apply the vault's archive status or metadata while retaining content, provenance, tags, and useful links.
4. Re-read the moved file and assert that the destination exists, the source is absent, the vault-defined archive metadata is present, and the permitted-scope `unresolved` count has not increased.
5. If a step fails, report the intermediate state instead of silently continuing.

## Review and read-only audit

Within the permitted scope, use the CLI to inspect `tasks todo verbose`, `unresolved verbose`, `orphans total`, `deadends total`, `tags counts`, and `properties counts`. Treat the results as signals for review, not automatic cleanup instructions.

For a read-only review, do not follow the mutation steps in the capture or archiving sections. Report findings and proposed actions without executing them.
