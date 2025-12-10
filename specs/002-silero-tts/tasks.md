# Tasks: Silero TTS module with metrics

## Phase 1: Setup
- [x] T001 Verify torch/silero deps and add to pyproject.toml if missing
- [x] T002 Ensure uv lock updated after new deps (`uv lock`)

## Phase 2: Foundational
- [x] T003 Update synthesis interface to support duration/metrics output in src/synthesis/interface.py
- [x] T004 Define Silero config schema (voice/lang/format/device/paths) in src/utils/config.py
- [x] T005 Add logging helpers for timing (synth_ms, model_load_ms) in src/utils/logging.py

## Phase 3: User Story 1 — Синтез через CLI (P1)
- [x] T006 [US1] Implement Silero synthesizer class using torch hub in src/synthesis/silero.py
- [x] T007 [US1] Wire Silero into synthesis factory/selector in src/synthesis/__init__.py or stub
- [x] T008 [US1] Create CLI command src/cli/silero_tts.py accepting text/file, using config defaults
- [x] T009 [US1] Add input validation (length ≤1000, charset) in CLI handler src/cli/silero_tts.py
- [x] T010 [US1] Save audio to output path with format handling (wav/mp3) in src/cli/silero_tts.py
- [x] T011 [US1] Log path + metrics to stdout and return exit code 0/!=0 accordingly
- [x] T012 [P] [US1] Unit tests for CLI and synthesizer (happy path/error) in tests/unit/test_silero_cli.py
- [x] T028 [US1] Negative CLI cases: missing/unwritable output dir or config → non-zero exit and clear error message (extend tests/unit/test_silero_cli.py)

## Phase 4: User Story 2 — Конфиг (P2)
- [x] T013 [US2] Load defaults from config file and override via env for Silero settings in src/utils/config.py
- [x] T014 [US2] Validate config (supported voice/lang/format, output dir existence/creation) in src/utils/config.py
- [x] T015 [P] [US2] Tests for config/env overrides in tests/unit/test_config_silero.py

## Phase 5: User Story 3 — Метрики (P3)
- [x] T016 [US3] Measure model load time once and expose in logs/CLI output in src/synthesis/silero.py
- [x] T017 [US3] Capture per-request synth_ms and audio duration in src/synthesis/silero.py
- [x] T018 [US3] Emit metrics to stdout/file channel (human-readable) in src/utils/logging.py or CLI
- [x] T019 [P] [US3] Tests for metrics values and formatting in tests/unit/test_silero_metrics.py
- [x] T027 [US3] Add perf check/benchmark for SC-001 (<=8s, 48kHz) in tests/integration/test_silero_perf.py

## Phase 6: User Story 4 — Интеграция в бота (P2)
- [x] T020 [US4] Inject Silero synthesizer into bot worker pipeline in src/bot/worker.py
- [x] T021 [US4] Add fallback text response when Silero недоступен; no audio send in src/bot/handlers.py
- [x] T022 [US4] Log synth_ms/duration per bot request in src/bot/handlers.py
- [x] T023 [P] [US4] Integration tests for bot flow with Silero and failure fallback in tests/integration/test_bot_silero.py

## Phase 7: Polish & Cross-Cutting
- [x] T024 Update quickstart with Silero env vars/CLI usage in specs/002-silero-tts/quickstart.md (SC-002, SC-004)
- [x] T025 Document clarifications and fallback behavior in specs/002-silero-tts/spec.md if needed (FR-009, FR-006)
- [x] T026 Run full test suite (uv run pytest) and fix issues (SC-001–SC-005)

## Dependencies
- Setup → Foundational → US1 → US2 (config) → US3 (metrics) → US4 (bot) → Polish

## Parallel Opportunities
- T012, T015, T019, T023 can run in parallel after respective implementation stubs exist.

## MVP Scope
- Complete US1 (T006–T012) to deliver working CLI synthesis with metrics output and deterministic audio.

## Implementation Strategy
- Follow phases in order; keep interfaces swappable. Favor deterministic outputs and clear logs. Use config overrides via env for deploy.

