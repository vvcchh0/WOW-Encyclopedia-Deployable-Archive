# WoW archive project agreements

## Delegation and deletion ownership

The user requests Luna Max for connection/download work, bounded polling, file inventories, and non-destructive organization. The main agent owns planning, source acceptance, implementation decisions, deletion, and publication. Use a model actually offered by the current tools and report its exact name; do not silently substitute a different requested model. Do not start new recovery batches or schedules solely because this standing delegation preference exists.

- Give each executor a bounded task with exact inputs, a new output directory under `D:\WOW_Encyclopedia`, a deadline, and request/byte limits where applicable. Executors must not delegate again.
- Luna may read the assigned inputs, fetch approved public sources, write new downloads and reports, copy files, and create new compressed archives in its assigned directory. Existing files must be preserved. File organization means inventory, proposed mappings, copies, and new archives.
- Luna must not delete any file or directory, including temporary files, partial downloads, empty folders, caches, or its own outputs. It must not move or rename source files, overwrite or truncate existing files, or use cleanup tools. This covers shell commands, Python/Node/filesystem APIs, tool calls, and scripts with automatic cleanup, extraction overwrite, or destructive mirror behavior. Review third-party tools for these side effects before delegation.
- Luna must not perform Git cleanup/reset, commit/push, Release/deployment mutations, process termination, global configuration edits, permission changes, or automatic scheduling. Return proposed actions to the main agent.
- A child may execute an elevated command only after the main agent has reviewed the exact command, tool behavior, resolved paths, and task scope. It must not expand an approved command or reuse historical approval for another operation. If that review cannot be satisfied, return the command and evidence for the main agent to execute.
- Every deletion, including remote publication cleanup, belongs to the main agent. Before any authorized local deletion or directory move, inspect contents, resolve the precise absolute target, verify it against an explicit project allowlist, and verify any required backup. Never clean the user profile, `HOME`, `USERPROFILE`, or `CODEX_HOME` as a bulk target. Prefer PowerShell `-LiteralPath`; never pass computed cleanup paths across shells.

Subagents share the parent session's sandbox and approval settings. These instructions constrain their permitted work; they do not create an OS-level deny-delete permission. Never describe a prompt restriction as an enforced filesystem barrier. Do not loosen the parent sandbox or global settings to make an executor work.

## Files and retrieval

- Keep raw captures, source manifests, historical ZIPs, and accepted versions intact. Implement repairs in a new derived version.
- Before each network batch, request, or substantial write, keep at least 11,005,853,696 bytes free on D:. There is no fixed project-size cap.
- Prefer direct connections, then use `127.0.0.1:7890` only within the downloading process. Keep TLS verification enabled; do not change system DNS, proxy, hosts, or certificates.
- Use one serial Wayback fetcher, at least five seconds between request starts, and bounded requests, time, and bytes. Stop on 429/503 or five consecutive transport failures, honor Retry-After and at least 120 seconds of cooldown, and obtain a successful control after the latest failure before a new batch. Do not work around rate limits.
- Use existing HTTP/CDX/Common Crawl and related-source tools without paid Firecrawl calls. Record actual source dates, file validity, and unresolved network outcomes.

## Publication cadence

Read [the publication policy](docs/publication-policy.md) before publishing.

- Publish reviewed website fixes as needed and record progress in CHANGELOG.
- Publish a full offline ZIP only for a meaningful stage result or a significant offline-use fix. A new deployment number, completed download batch, or elapsed work session alone does not warrant a full package.
- Keep the latest package and selected milestones listed in `docs/release-history.md`. Back up release assets and metadata before pruning superseded publications, and preserve Git tags.
- Keep raw capture HTTP metadata private. Verify the live site and the extracted package separately when publishing both.
