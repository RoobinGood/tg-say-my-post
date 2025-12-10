# Tasks: Telegram TTS Bot

**Input**: Design documents from `/specs/001-telegram-tts-bot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Include key unit/integration checks where valuable; minimal set listed.

**Organization**: Tasks grouped by user story for independent delivery.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffolding, deps, assets.

- [x] T001 Create project structure per plan (src/{bot,synthesis,audio,cli,utils}, tests/{unit,integration,contract})
- [x] T002 Add Python deps in `pyproject.toml` (python-telegram-bot, pydub, pytest) via uv
- [x] T003 Move example mp3 into `src/audio/example.mp3` (remove root copy)
- [x] T004 [P] Add stub entrypoints `src/cli/__init__.py`, `src/cli/run_bot.py`, `src/cli/synth_stub.py` shells

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared utilities, config, logging, synthesis stub.

- [x] T005 Create env config loader in `src/utils/config.py` (BOT_TOKEN, WHITELIST, DEBUG, AUDIO_STUB_PATH, LOG_LEVEL)
- [x] T006 [P] Add logging helper with timestamps/context in `src/utils/logging.py`
- [x] T007 [P] Implement in-memory per-chat queue in `src/utils/queue.py` (FIFO, status)
- [x] T008 Define synthesis interface + stub using example mp3 in `src/synthesis/interface.py` and `src/synthesis/stub.py`
- [x] T009 Wire synthesis CLI (`src/cli/synth_stub.py`) per contract, returning mp3 or error codes
- [x] T010 Scaffold bot app startup in `src/cli/run_bot.py` (token load, whitelist check hook, logging init)

**Checkpoint**: config/logging/queue/synth stub ready; bot can start and exit cleanly.

---

## Phase 3: User Story 1 - Озвучка текстового сообщения (Priority: P1) 🎯 MVP

**Goal**: Прямая текстовая отправка → голосовое без префикса, лимит 2000.
**Independent Test**: Отправить текст ≤2000 → получить голосовой ответ в том же чате; пустой/нет текста → «озвучивать нечего».

### Implementation

- [x] T011 [P] [US1] Add IncomingItem/AudioJob models in `src/bot/models.py`
- [x] T012 [P] [US1] Implement validation (пусто/лимит 2000) in `src/bot/validators.py`
- [x] T013 [US1] Implement text handler for direct messages in `src/bot/handlers.py` (enqueue, no prefix)
- [x] T014 [US1] Integrate queue consumption + synth stub + send audio reply in `src/bot/worker.py`
- [x] T015 [US1] Wire handlers into bot startup in `src/cli/run_bot.py`

### Tests

- [x] T016 [P] [US1] Unit tests for validation and queue in `tests/unit/test_validators_queue.py`
- [x] T017 [US1] Integration test direct text → mp3 reply in `tests/integration/test_direct_text.py`

**Checkpoint**: US1 independently delivers audio replies for direct text.

---

## Phase 4: User Story 2 - Озвучка пересланных постов (Priority: P2)

**Goal**: Пересланные сообщения/посты с голосовым префиксом.
**Independent Test**: Переслать сообщение пользователя и пост канала → корректные префиксы + голосовой ответ.

### Implementation

- [x] T018 [P] [US2] Extend source detection to forwarded user/channel in `src/bot/validators.py`
- [x] T019 [P] [US2] Add prefix builder in `src/bot/prefix.py` (user/channel)
- [x] T020 [US2] Update handler to apply prefixes for forwarded items in `src/bot/handlers.py`
- [x] T021 [US2] Ensure synth stub accepts optional prefix parameter in `src/synthesis/stub.py`

### Tests

- [x] T022 [P] [US2] Unit tests for prefix builder and forwarded detection in `tests/unit/test_prefix_forwarded.py`
- [x] T023 [US2] Integration test forwarded user/channel → mp3 with prefix in `tests/integration/test_forwarded.py`

**Checkpoint**: US2 independently delivers prefixed audio for forwarded items.

---

## Phase 5: User Story 3 - Прослушивание очереди постов (Priority: P3)

**Goal**: Сохранение порядка озвучек per чат.
**Independent Test**: Отправить 5 сообщений/пересылок → голосовые ответы приходят в исходном порядке; новые сообщения добавляются в конец.

### Implementation

- [x] T024 [P] [US3] Add ordered enqueue per chat with monotonic counter in `src/utils/queue.py`
- [x] T025 [US3] Ensure worker processes per-chat FIFO and serializes sends in `src/bot/worker.py`
- [x] T026 [US3] Add retry/error text path without breaking order in `src/bot/worker.py`

### Tests

- [x] T027 [P] [US3] Unit test ordering logic in `tests/unit/test_queue_ordering.py`
- [x] T028 [US3] Integration test multi-message sequence order in `tests/integration/test_sequence_order.py`

**Checkpoint**: US3 ensures ordered delivery.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, docs, validation.

- [x] T029 [P] Improve error messages/localization in `src/bot/handlers.py`
- [x] T030 [P] Add quickstart validation steps in `specs/001-telegram-tts-bot/quickstart.md`
- [x] T031 [P] Add logging coverage for key events in `src/utils/logging.py`
- [x] T032 Run full test suite `uv run pytest`

---

## Phase 7: Voice Response Alignment (Spec Update)

**Purpose**: Перевести ответы на голосовые сообщения и обновить тесты.

### Implementation

- [x] T033 [US1] Convert synthesis stub to produce voice-friendly OGG/Opus and expose path in `src/synthesis/stub.py`
- [x] T034 [US1] Send replies as voice (`send_voice`/`reply_voice`) in `src/bot/worker.py` with OGG output
- [x] T035 [US2] Ensure forwarded prefixes preserved in voice replies in `src/bot/worker.py`

### Tests

- [x] T036 [US1] Update direct text integration test to expect voice reply in `tests/integration/test_direct_text.py`
- [x] T037 [US2] Update forwarded integration test to expect voice with prefixes in `tests/integration/test_forwarded.py`
- [x] T038 [US3] Update sequence/order integration test for voice replies in `tests/integration/test_sequence_order.py`
- [x] T039 Run full test suite `uv run pytest`

**Checkpoint**: Голосовые ответы соответствуют спеке; префиксы и порядок сохранены.

---

## Phase 8: Spec Alignment (/start and voice policy)

**Purpose**: Закрыть требования FR-001 и поведение при запрете voice.

- [x] T040 Добавить/зафиксировать обработчик `/start` с инструкцией (src/bot/handlers.py)
- [x] T041 Зафиксировать текстовое уведомление при запрете voice в чате (spec + handlers)

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup → Foundational → US1 (MVP) → US2 → US3 → Polish → Voice Response Alignment.

### User Story Dependencies

- US1 independent after foundational.
- US2 builds on US1 handlers/prefix infra.
- US3 uses queue/worker from US1 and US2.

### Parallel Opportunities

- Setup tasks T001–T004: T004 parallel.
- Foundational: T006–T008 parallel.
- US1: T011/T012 parallel; T013 depends on validators/models; T014 after queue/handlers; T016 parallel tests; T017 after implementation.
- US2: T018/T019 parallel; T020 depends on them; T021 parallel; T022 parallel; T023 after implementation.
- US3: T024 parallel; T025 depends on queue; T026 after worker; T027 parallel; T028 after implementation.
- Polish: T029–T031 parallel; T032 last.
- Voice: T033/T034 parallel; T035 after worker voice; T036–T038 update tests parallel after code; T039 last.

### Implementation Strategy

- MVP: complete Phases 1–3; validate direct text flow.
- Incremental: add US2 prefixed forwards; then US3 ordering; finish with polish.
- Voice alignment: apply Phase 7 to switch на голосовые ответы; rerun tests (T039).


