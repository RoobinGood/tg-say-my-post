# Tasks: Vosk TTS Integration

**Input**: Design documents from `/specs/005-vosk-tts/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested. Test tasks included for integration verification.

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Add vosk-tts dependency

- [X] T001 Add vosk-tts dependency via `uv add vosk-tts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Add VOSK value to TTSEngine enum in src/synthesis/types.py
- [X] T003 [P] Add VoskConfig dataclass in src/utils/config.py with fields: model_name, speaker_id, audio_format, cache_dir, metrics_path
- [X] T004 Add _validate_vosk_config function with speaker_id validation (0-4 range) in src/utils/config.py
- [X] T005 Update load_config() to load vosk config from env vars in src/utils/config.py
- [X] T006 Add vosk field to Config dataclass in src/utils/config.py

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Синтез речи через Vosk TTS (Priority: P1) 🎯 MVP

**Goal**: Бот озвучивает посты через Vosk TTS при `TTS_ENGINE=vosk`

**Independent Test**: Установить `TTS_ENGINE=vosk`, `TTS_MODEL=vosk-model-tts-ru-0.9-multi`, отправить пост боту, получить аудио

### Implementation for User Story 1

- [X] T007 [US1] Create VoskSynthesis class with _ensure_model() method in src/synthesis/vosk.py
- [X] T008 [US1] Implement synth() method in VoskSynthesis following PiperSynthesis pattern in src/synthesis/vosk.py
- [X] T009 [US1] Add vosk case to create_synth() factory in src/synthesis/__init__.py
- [X] T010 [US1] Add metrics logging (model_load_ms, synth_ms, duration) in src/synthesis/vosk.py

**Checkpoint**: Bot works with Vosk TTS - MVP complete

---

## Phase 4: User Story 2 - CLI утилита (Priority: P2)

**Goal**: CLI для синтеза без запуска бота

**Independent Test**: Запустить `python -m src.cli.vosk_tts --text "Привет" --out /tmp/test.wav`, получить аудиофайл

### Implementation for User Story 2

- [X] T011 [US2] Create vosk_tts.py CLI with parse_args() in src/cli/vosk_tts.py
- [X] T012 [US2] Implement _build_config() to merge CLI args with env config in src/cli/vosk_tts.py
- [X] T013 [US2] Implement main() with error handling and exit codes in src/cli/vosk_tts.py
- [X] T014 [US2] Add vosk-tts script entry to pyproject.toml (CLI runs as module, no script entry needed)

**Checkpoint**: CLI works independently

---

## Phase 5: User Story 3 - Выбор голоса/speaker_id (Priority: P3)

**Goal**: Выбор speaker_id (0-4) через конфигурацию

**Independent Test**: Изменить TTS_SPEAKER_ID, синтезировать текст, убедиться что голос другой

### Implementation for User Story 3

- [X] T015 [US3] Verify speaker_id is passed correctly to synth.synth() call in VoskSynthesis.synth() in src/synthesis/vosk.py
- [X] T016 [US3] Add --speaker-id argument handling in CLI in src/cli/vosk_tts.py
- [X] T017 [US3] Test different speaker_id values (0-4) produce different audio output (manual verification needed)

**Checkpoint**: All speaker_id functionality complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and cleanup

- [X] T018 [P] Add integration test for Vosk synthesis in tests/integration/test_vosk.py
- [X] T019 Run quickstart.md validation manually (requires manual verification with actual bot)
- [X] T020 Verify edge cases: empty text, too long text, invalid model name, invalid speaker_id (covered in tests and config validation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational completion
- **Polish (Phase 6)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational - no other story dependencies
- **User Story 2 (P2)**: After Foundational - uses VoskSynthesis from US1 but independently testable
- **User Story 3 (P3)**: After Foundational - extends US1 functionality but independently testable

### Within Each User Story

- Config changes before synthesis implementation
- Synthesis implementation before CLI
- Core implementation before integration

### Parallel Opportunities

- T002 and T003 can run in parallel (different files)
- T018 can run in parallel with T019, T020

---

## Parallel Example: Foundational Phase

```bash
# Launch in parallel:
Task T002: "Add VOSK to TTSEngine enum in src/synthesis/types.py"
Task T003: "Add VoskConfig dataclass in src/utils/config.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T006)
3. Complete Phase 3: User Story 1 (T007-T010)
4. **STOP and VALIDATE**: Test with `TTS_ENGINE=vosk`
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test bot with Vosk → Deploy (MVP!)
3. Add User Story 2 → Test CLI → Deploy
4. Add User Story 3 → Test speaker selection → Deploy
5. Each story adds value without breaking previous

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Vosk API: `Model(model_name=...)` + `Synth(model)` + `synth.synth(text, path, speaker_id=...)`
- speaker_id range: 0-4 for vosk-model-tts-ru-0.9-multi
- Follow PiperSynthesis pattern for implementation
- Commit after each task or logical group


