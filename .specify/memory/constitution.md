<!-- Sync Impact Report: Version unknown → 1.0.0 | Modified principles: none (new) | Added sections: Core Principles, Operational Constraints, Development Workflow, Governance | Removed sections: none | Templates updated: plan-template.md ✅, spec-template.md ✅, tasks-template.md ✅, commands/* ⚠️ (no command templates present) | Follow-up TODOs: none -->

# tg-say-my-post Constitution

## Core Principles

### Pythonic Modularity
Build in idiomatic Python with current libraries, managed by `uv`, and keep each module runnable on its own for fast verification and minimal coupling.

### Pluggable Speech Synthesis with CLI
Expose a stable synthesis interface that can swap implementations; every implementation must provide a CLI entry point to run and inspect its behavior independently.

### Telegram
Bot should always answer to user with russian langauge.
In debug mode in case of error during processing it should send error trace to user.
Protect the bot by enabling a whitelist of allowed Telegram users; any request from non-whitelisted users is rejected without side effects.

### Transparent Logging
Log incoming messages and key synthesis steps as plain text with clear labels and timestamps to make troubleshooting straightforward.

### Simple and YAGNI
Favor the smallest working solution, avoid speculative abstractions, and add only the dependencies and features required for the current need.

## Operational Constraints

Configuration is driven by environment variables (including the Telegram whitelist and synthesis choices). The project runs in Docker, is managed with `uv`, and keeps the structure small and easy to navigate.

## Development Workflow

Each module must be executable directly (or via its CLI) for quick checks. Implementations of the speech synthesis interface must be verifiable from the command line. Run tests after code changes to ensure stability, keeping the suite lean and focused on behavior that matters.

## Git

Use conventional commits to write commit messages

## Governance

This constitution is the authoritative baseline. Amendments require documenting the change, rationale, and expected impact in a PR before adoption. Use semantic versioning; increase MAJOR for breaking governance changes, MINOR for added or expanded principles/sections, and PATCH for clarifications. Reviews must confirm compliance with principles (Pythonic modularity, pluggable synthesis with CLI, whitelist enforcement, logging, simplicity) and that configuration remains environment-driven and Docker/uv-compatible.

**Version**: 1.0.0 | **Ratified**: 2025-12-10 | **Last Amended**: 2025-12-10
