# Vault Git delivery reference

Read this file only when the user explicitly requests a commit or push after a vault mutation. Git is the delivery layer for completed changes, not a replacement for the official Obsidian CLI.

## Before committing

1. Resolve the repository with `git -C <target-vault> rev-parse --show-toplevel`.
2. Inspect `git status --short`, `git remote -v`, the current branch, and its upstream. Never assume `origin`, `main`, or a hosting service.
3. Capture the repository status before editing. Separate the current task's diff from pre-existing modifications; if that cannot be done reliably, stop before committing.
4. Re-read changed notes, run the relevant Obsidian CLI validation, and run `git diff --check`.
5. Check ignore rules before staging suspicious files. Do not commit secrets, tokens, private keys, or local device state.

## Commit and push

- Stage only paths changed by the current task with `git add -- <specific paths>`; do not use `git add .` by default.
- Group the current task's related mutations into one concise commit with a meaningful message.
- Push only after the user explicitly confirms the remote operation. Never force-push, reset, discard changes, overwrite a remote, or create a remote merely to complete this workflow.
- After committing or pushing, verify `git status --short --branch` and report the commit and upstream result.

## Safe stop conditions

If there is no repository, remote, upstream, authentication, network access, or if a merge/conflict condition appears, preserve local changes, report the exact blocker, and stop the Git step safely.
