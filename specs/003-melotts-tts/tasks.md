# Tasks: MeloTTS support and model switching

**Status**: Rejected — фича не реализуется (нет русской модели MeloTTS); задачи оставлены как архив.

**Input**: Design documents from `/specs/003-melotts-tts/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Stories request functional verification; include integration checks per story.
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Add MeloTTS dependency to pyproject and lock in `pyproject.toml` and `uv.lock`
- [ ] T002 [P] Scaffold MeloTTS CLI entrypoint aligned with silero CLI in `src/cli/melo_tts.py`
- [ ] T003 [P] Refresh MeloTTS env/setup steps and verification flow in `specs/003-melotts-tts/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Add shared `TTSConfig` with engine enum, model, text_limit parsing/validation (fail startup on missing/invalid) in `src/utils/config.py`
- [ ] T005 [P] Introduce TTS engine/model enums and shared types used by providers in `src/synthesis/types.py`
- [ ] T006 [P] Enforce configured text_limit with friendly errors across bot validator and provider/CLI entrypoints in `src/bot/validators.py`, `src/synthesis/melotts.py`, `src/cli/melo_tts.py`, `src/cli/silero_tts.py`
- [ ] T007 Wire synthesis factory to accept config-selected engine and structured logging in `src/synthesis/__init__.py`
- [ ] T024 [P] Auto-download missing MeloTTS weights at startup with checksum/size validation and cache dir handling; fail startup on download error in `src/synthesis/melotts.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Синтез через MeloTTS (Priority: P1) 🎯 MVP

**Goal**: Бот озвучивает входящие посты через MeloTTS при выборе движка.

**Independent Test**: Включить MeloTTS в конфиге, отправить пост, получить аудио от MeloTTS.

### Tests for User Story 1

- [ ] T008 [P] [US1] Add integration test covering MeloTTS provider/CLI happy path in `tests/integration/test_melotts_provider.py`

### Implementation for User Story 1

- [ ] T009 [P] [US1] Implement `MeloTtsSynthesis` provider with load/prefix/limit handling in `src/synthesis/melotts.py`
- [ ] T010 [US1] Complete MeloTTS CLI wiring to provider and config overrides in `src/cli/melo_tts.py`
- [ ] T011 [US1] Allow `TTS_ENGINE=melotts` via bot entrypoint and factory usage in `src/cli/run_bot.py`
- [ ] T012 [US1] Emit MeloTTS metrics/log lines (engine, model, durations) in `src/synthesis/melotts.py`

**Checkpoint**: User Story 1 is fully functional and testable independently

---

## Phase 4: User Story 2 - Переключение движка и модели (Priority: P2)

**Goal**: Администратор переключает движок и модель через конфиг без деплоя.

**Independent Test**: Изменить конфиг на другой движок/модель, перезапустить, следующий пост озвучивается новым голосом.

### Tests for User Story 2

- [ ] T013 [P] [US2] Add integration test for engine/model switching between Silero и MeloTTS in `tests/integration/test_tts_switch.py`

### Implementation for User Story 2

- [ ] T014 [P] [US2] Enforce required model per engine with clear fail-fast startup errors and logs in `src/utils/config.py`
- [ ] T015 [US2] Update synthesis factory to drive provider choice from config (no manual env override) in `src/synthesis/__init__.py`
- [ ] T016 [US2] Ensure bot startup applies engine/model config and logs active selection in `src/cli/run_bot.py`

**Checkpoint**: User Stories 1 AND 2 work independently and respect config switching

---

## Phase 5: User Story 3 - Непрерывность работы (Priority: P3)

**Goal**: При недоступности движка бот не падает, даёт понятное сообщение, логирует проблему.

**Independent Test**: Симулировать недоступность выбранного движка, получить дружелюбное уведомление и лог без краша.

### Tests for User Story 3

- [ ] T017 [P] [US3] Add failure-path integration test for unavailable engine response in `tests/integration/test_tts_resilience.py`

### Implementation for User Story 3

- [ ] T018 [US3] Map provider exceptions to user-friendly messages with no auto-fallback in `src/bot/worker.py`
- [ ] T019 [P] [US3] Add explicit unavailability/timeout detection (no auto-switch) with clear errors in `src/synthesis/melotts.py` and `src/synthesis/silero.py`
- [ ] T020 [US3] Log structured failure events (engine/model/duration) to metrics/log files in `src/utils/logging.py`

**Checkpoint**: All user stories independently handle availability and messaging

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T021 [P] Update feature docs with engine/model configuration and failure modes in `specs/003-melotts-tts/plan.md`
- [ ] T022 Run quickstart verification steps for both engines and note results in `specs/003-melotts-tts/quickstart.md`
- [ ] T023 [P] Add synthesis performance check (p95 ≤5s for ≤1000 chars) capturing timings per engine in `tests/integration/test_tts_performance.py` and update logs/metrics

---

## Dependencies & Execution Order

- Setup → Foundational → User Stories (P1 → P2 → P3) → Polish
- User Story dependencies: US1 none; US2 depends on foundational and may reuse US1 provider artifacts but must be testable alone; US3 depends on foundational and uses providers from prior stories but validates resilience independently.

## Parallel Opportunities

- Setup: T002, T003 in parallel once dependency pin (T001) is chosen.
- Foundational: T005–T007, T024 can run in parallel after config shape (T004).
- US1: T008 and T009 can run in parallel; T010 depends on T009; T011 depends on T007; T012 after T009.
- US2: T013 can start after foundational; T014–T015 in parallel; T016 after T015.
- US3: T017 can start after providers exist; T018 after T015; T019 parallel with T018; T020 after provider error mapping.

## Implementation Strategy

- MVP first: Complete Setup → Foundational → US1; validate MeloTTS end-to-end before proceeding.
- Incremental: Add US2 for switching, then US3 for resilience; each story must remain independently testable via its integration check.
