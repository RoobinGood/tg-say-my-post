# Tasks: Text Preprocessing with LLM

**Input**: Design documents from `/specs/006-text-preprocessing-llm/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks grouped by user story. US3 (Stress Marks) merged into US2 (LLM) since it's part of LLM prompt. US4 (Configuration) is foundational.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US5)

---

## Phase 1: Setup

**Purpose**: Add dependencies, create config files

- [X] T001 Add dependencies (openai, tiktoken, num2words) to pyproject.toml
- [X] T002 [P] Create config/transliteration.json with abbreviations, symbols, units
- [X] T003 [P] Create prompts/transliteration.txt with system prompt for LLM

---

## Phase 2: Foundational (US4 - LLM Configuration)

**Purpose**: Core configuration that enables all other stories

**Goal**: Administrator can configure LLM API parameters via environment variables

**Independent Test**: Set LLM_API_URL and LLM_API_KEY in .env, verify config loads correctly

- [X] T004 Create LLMConfig dataclass in src/utils/config.py
- [X] T005 Add LLM environment variable parsing in src/utils/config.py (_parse_llm_config)
- [X] T006 Add LLMConfig validation (api_key required if enabled, prompt file exists)
- [X] T007 Add LLMConfig to main Config dataclass in src/utils/config.py
- [X] T008 [P] Create TextChunk and PreprocessResult dataclasses in src/bot/text_preprocess.py (top of file)
- [X] T009 [P] Create LLM exceptions (LLMError, LLMValidationError, LLMTimeoutError) in src/bot/llm_client.py

**Checkpoint**: Configuration loads with all LLM parameters from environment

---

## Phase 3: User Story 1 - Basic Text Cleanup (Priority: P1) 🎯 MVP

**Goal**: Text with emoji and missing punctuation is cleaned and formatted correctly

**Independent Test**: Send "👋 привет мир" → receive "- Привет мир."

### Implementation for US1

- [X] T010 [US1] Add _capitalize_paragraphs function in src/bot/text_preprocess.py
- [X] T011 [US1] Add _remove_urls function (regex for http/https links) in src/bot/text_preprocess.py
- [X] T012 [US1] Update preprocess_text to call _capitalize_paragraphs and _remove_urls in src/bot/text_preprocess.py
- [X] T013 [US1] Add unit tests for capitalization and URL removal in tests/unit/test_text_preprocess.py

**Checkpoint**: Basic text cleanup works with capitalization and improved punctuation

---

## Phase 4: User Story 5 - Programmatic Fallback (Priority: P3)

**Goal**: When LLM is disabled or unavailable, system performs programmatic transliteration

**Independent Test**: Set LLM_ENABLED=false, send "API стоит $100" → receive "эй пи ай стоит сто доллар"

**Note**: Moved before US2 because LLM integration depends on fallback mechanism

### Implementation for US5

- [X] T014 [P] [US5] Create TranslitConfig loader (load JSON) in src/bot/translit.py
- [X] T015 [US5] Implement _transliterate_numbers (using num2words) in src/bot/translit.py
- [X] T016 [US5] Implement _transliterate_abbreviations (from config) in src/bot/translit.py
- [X] T017 [US5] Implement _transliterate_symbols (from config) in src/bot/translit.py
- [X] T018 [US5] Implement _transliterate_latin_fallback (char-by-char) in src/bot/translit.py
- [X] T019 [US5] Implement transliterate_programmatic main function in src/bot/translit.py
- [X] T020 [US5] Implement fix_invalid_chars function in src/bot/translit.py
- [X] T021 [US5] Add unit tests for translit module in tests/unit/test_translit.py

**Checkpoint**: Programmatic transliteration works standalone (numbers, abbreviations, symbols)

---

## Phase 5: User Story 2 + 3 - LLM Transliteration (Priority: P1 + P2)

**Goal**: Text with Latin, numbers, symbols is transliterated via LLM; stress marks added for homographs

**Independent Test**: Send "API версии 2.5 стоит $100" with LLM enabled → receive "эй пи ай версии два целых пять десятых стоит сто долларов"

**Note**: US3 (Stress Marks) is part of LLM system prompt, tested together

### Implementation for US2 + US3

- [X] T022 [US2] Implement _load_system_prompt in src/bot/llm_client.py
- [X] T023 [US2] Implement _validate_response (regex check) in src/bot/llm_client.py
- [X] T024 [US2] Implement LLMClient.__init__ with OpenAI client setup and optional prompt caching in src/bot/llm_client.py
- [X] T025 [US2] Implement LLMClient.transliterate with retry logic in src/bot/llm_client.py
- [X] T026 [US2] Implement _split_into_chunks (by paragraphs, respecting min_chunk_size) in src/bot/text_preprocess.py
- [X] T027 [US2] Implement LLMClient.transliterate_chunks in src/bot/llm_client.py
- [X] T028 [US2] Update preprocess_text to integrate LLM flow in src/bot/text_preprocess.py
- [X] T029 [US2] Add fallback to programmatic transliteration on LLM error in src/bot/text_preprocess.py
- [X] T030 [US2] Add fix_invalid_chars call after LLM response in src/bot/text_preprocess.py
- [X] T031 [US2] Implement preprocess_text_with_result for detailed metrics in src/bot/text_preprocess.py
- [X] T032 [US2] Add logging for LLM calls and errors in src/bot/llm_client.py
- [X] T033 [US2] Add unit tests for llm_client in tests/unit/test_llm_client.py
- [X] T034 [US2] Add integration test with mocked LLM in tests/integration/test_llm_integration.py

**Checkpoint**: LLM transliteration works with retry, validation, and fallback

---

## Phase 6: Polish & Integration

**Purpose**: CLI tool, bot integration, documentation

- [X] T035 [P] Create CLI tool for testing preprocessing in src/cli/preprocess.py
- [X] T036 Update worker.py to pass LLMConfig to preprocess_text in src/bot/worker.py
- [X] T037 [P] Update .env.example with LLM configuration variables
- [X] T038 Run quickstart.md verification checklist
- [X] T039 [P] Update README.md with preprocessing configuration section
- [X] T040 Verify SC-003: processing 500 chars completes in <10s (manual test with CLI)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational/US4)**: Depends on Setup
- **Phase 3 (US1)**: Depends on Phase 2 (uses Config)
- **Phase 4 (US5)**: Depends on Phase 2 (uses TranslitConfig)
- **Phase 5 (US2+US3)**: Depends on Phase 4 (needs fallback)
- **Phase 6 (Polish)**: Depends on Phase 5

### User Story Dependencies

```
US4 (Config) ─────────────────┐
     │                        │
     ▼                        ▼
US1 (Cleanup)            US5 (Fallback)
                              │
                              ▼
                    US2+US3 (LLM Transliteration)
```

- **US1**: Independent after foundational
- **US5**: Independent after foundational
- **US2+US3**: Depends on US5 (for fallback mechanism)

### Parallel Opportunities

```bash
# Phase 1 - all parallel:
T002: config/transliteration.json
T003: prompts/transliteration.txt

# Phase 2 - parallel models:
T008: TextChunk, PreprocessResult models
T009: LLM exceptions

# Phase 4 (US5) - parallel start:
T014: TranslitConfig loader

# Phase 6 - parallel polish:
T035: CLI tool
T037: .env.example
T039: README.md
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phase 1 + Phase 2
2. Complete Phase 3 (US1 - Basic Cleanup)
3. **STOP**: Test basic cleanup works
4. Deploy if ready

### Programmatic Fallback (US1 + US5)

1. Complete Phases 1-3 (MVP)
2. Complete Phase 4 (US5 - Programmatic Fallback)
3. **STOP**: Test programmatic transliteration without LLM
4. Deploy if LLM not ready yet

### Full Feature (All Stories)

1. Complete Phases 1-5
2. Complete Phase 6 (Polish)
3. Test all scenarios from spec.md
4. Deploy

---

## Summary

| Phase | Story | Tasks | Parallel |
|-------|-------|-------|----------|
| 1 Setup | - | 3 | 2 |
| 2 Foundational | US4 | 6 | 2 |
| 3 | US1 | 4 | 0 |
| 4 | US5 | 8 | 1 |
| 5 | US2+US3 | 13 | 0 |
| 6 Polish | - | 6 | 3 |
| **Total** | | **40** | **8** |

