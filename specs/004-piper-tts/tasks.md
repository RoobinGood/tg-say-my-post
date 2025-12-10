# Tasks: Piper TTS support and model switching

**Status**: Planned

**Input**: Design documents from `/specs/004-piper-tts/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Stories request functional verification; include integration checks per story.
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Add Piper dependency to `pyproject.toml` and lock in `uv.lock`
- [x] T002 [P] Scaffold Piper CLI entrypoint aligned with silero CLI in `src/cli/piper_tts.py`
- [x] T003 [P] Ensure Piper setup/verification steps reflected in `specs/004-piper-tts/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Add shared `TTSConfig` with engine enum, model, text_limit parsing/validation (fail startup on missing/invalid) in `src/utils/config.py`
- [x] T005 [P] Introduce TTS engine/model enums and shared types used by providers in `src/synthesis/types.py`
- [x] T006 [P] Enforce configured text_limit with friendly errors across bot validator and provider/CLI entrypoints in `src/bot/validators.py`, `src/synthesis/piper.py`, `src/cli/piper_tts.py`, `src/cli/silero_tts.py`
- [x] T007 Wire synthesis factory to accept config-selected engine and structured logging in `src/synthesis/__init__.py`
- [x] T008 [P] Auto-download missing Piper weights at startup with checksum/size validation and cache dir handling; fail startup on download error in `src/synthesis/piper.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Синтез через Piper (Priority: P1) 🎯 MVP

**Goal**: Бот озвучивает входящие посты через Piper при выборе движка.

**Independent Test**: Включить Piper в конфиге, отправить пост, получить аудио от Piper.

### Tests for User Story 1

- [ ] T009 [P] [US1] Add integration test covering Piper provider/CLI happy path in `tests/integration/test_piper_provider.py`

### Implementation for User Story 1

- [x] T010 [P] [US1] Implement `PiperSynthesis` provider with load/prefix/limit handling in `src/synthesis/piper.py`
- [x] T011 [US1] Complete Piper CLI wiring to provider and config overrides in `src/cli/piper_tts.py`
- [x] T012 [US1] Allow `TTS_ENGINE=piper` via bot entrypoint and factory usage in `src/cli/run_bot.py`
- [x] T013 [US1] Emit Piper metrics/log lines (engine, model, durations) in `src/synthesis/piper.py`

**Checkpoint**: User Story 1 is fully functional and testable independently

---

## Phase 4: User Story 2 - Переключение движка и модели (Priority: P2)

**Goal**: Администратор переключает движок и модель через конфиг без деплоя.

**Independent Test**: Изменить конфиг на другой движок/модель, перезапустить, следующий пост озвучивается новым голосом.

### Tests for User Story 2

- [ ] T014 [P] [US2] Add integration test for engine/model switching between Silero и Piper in `tests/integration/test_tts_switch.py`

### Implementation for User Story 2

- [x] T015 [P] [US2] Enforce required model per engine with clear fail-fast startup errors and logs in `src/utils/config.py`
- [x] T016 [US2] Update synthesis factory to drive provider choice from config (no manual env override) in `src/synthesis/__init__.py`
- [x] T017 [US2] Ensure bot startup applies engine/model config and logs active selection in `src/cli/run_bot.py`

**Checkpoint**: User Stories 1 AND 2 work independently and respect config switching

---

## Phase 5: User Story 3 - Непрерывность работы (Priority: P3)

**Goal**: При недоступности движка бот не падает, даёт понятное сообщение, логирует проблему.

**Independent Test**: Симулировать недоступность выбранного движка, получить дружелюбное уведомление и лог без краша.

### Tests for User Story 3

- [ ] T018 [P] [US3] Add failure-path integration test for unavailable engine response in `tests/integration/test_tts_resilience.py`

### Implementation for User Story 3

- [x] T019 [US3] Map provider exceptions to user-friendly messages with no auto-fallback in `src/bot/worker.py`
- [ ] T020 [P] [US3] Add explicit unavailability/timeout detection (no auto-switch) with clear errors in `src/synthesis/piper.py` and `src/synthesis/silero.py`
- [x] T021 [US3] Log structured failure events (engine/model/duration) to metrics/log files in `src/utils/logging.py`

**Checkpoint**: All user stories independently handle availability and messaging

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T022 [P] Update feature docs with engine/model configuration and failure modes in `specs/004-piper-tts/plan.md`
- [ ] T023 Run quickstart verification steps for Piper and note results in `specs/004-piper-tts/quickstart.md`
- [ ] T024 [P] Add synthesis performance check (p95 ≤5s for ≤1000 chars) capturing timings per engine in `tests/integration/test_tts_performance.py`

---

## Dependencies & Execution Order

- Setup → Foundational → User Stories (P1 → P2 → P3) → Polish
- User Story dependencies: US1 none; US2 depends on foundational and may reuse US1 provider artifacts but must be testable alone; US3 depends on foundational and uses providers from prior stories but validates resilience independently.

## Parallel Opportunities

- Setup: T002, T003 in parallel once dependency pin (T001) is chosen.
- Foundational: T005–T008 can run in parallel after config shape (T004).
- US1: T009 and T010 can run in parallel; T011 depends on T010; T012 depends on T007/T010; T013 after T010.
- US2: T014 can start after foundational; T015–T016 in parallel; T017 after T016.
- US3: T018 can start after providers exist; T019 after T016; T020 parallel with T019; T021 after provider error mapping.
- Polish: T022–T024 can run after stories are done; T024 can run in parallel with T022.

