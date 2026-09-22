# Note organization reference

Read this file when the user asks to classify, reorganize, template, or update note properties, tags, links, or folders. The target vault's existing policy remains authoritative.

## Apply the vault's model

- Use the existing folder convention when one exists. If the vault uses PARA, understand Projects, Areas, Resources, and Archives as lifecycle buckets; if it uses another method, follow that method instead.
- Use the vault's templates when available. If a requested note type has no template, create a minimal format consistent with nearby notes or propose a template for approval.
- Do not create folders, properties, tags, or links merely to satisfy a framework. They should make capture, retrieval, reuse, or review easier.

## Metadata and connections

- When a schema exists, use YAML frontmatter for durable notes and apply its required fields through CLI property commands or a matching template.
- Before setting a property, check the vault schema and existing property statistics. Use an explicit CLI type, validate enumerated values and ISO dates, preserve list properties as lists, and read the exact property back after writing.
- If the name, type, value, or format conflicts with the schema, refuse the mutation and report the conflict.
- When no schema exists, prefer a small set of structured fields whose meaning is clear from the vault's use case; document the choice in the vault policy.
- Treat tags as cross-cutting retrieval hints and links as semantic relationships. Whether a vault prefers tags, links, MOCs, Bases, or a combination is a local design choice.

## Writing discipline

1. Read the index or MOC first and search to confirm whether the concept already has a note.
2. If it exists, reference it with a wikilink or update the existing note rather than writing a second summary. Link the first occurrence only, to avoid link noise.
3. Extract a structural or cross-cutting concept into its own note when it is likely to be referenced by two or more notes; keep single-topic details in the specific note.
4. Keep one source of truth. A concept note describes the concept itself; usage and scenarios belong in the consumer note, linked back with a wikilink.
5. For concept or data-structure notes, prefer: one-line conclusion → underlying structure → usage → pitfalls → related links.

## Topic sub-folders

When a topic folder grows, group notes by content type instead of leaving everything flat. Use `概念/` for concepts, `技术/` for standards and protocols, `设备/` for hardware, and `流程/` for flows or mechanisms when those categories fit the vault's existing model. Keep layer overviews and index notes at the topic root. A folder with one or two notes can stay flat.

Move notes with `obsidian move` so links update automatically, then verify with `unresolved`.
