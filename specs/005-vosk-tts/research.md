# Research: Vosk TTS Integration

## Findings

### Decision: Использовать библиотеку vosk-tts с автоматической загрузкой моделей
- **Rationale**: vosk-tts автоматически скачивает модели по имени при первом использовании. API простой: `Model(model_name=...)` + `Synth(model)` + `synth.synth(text, output_path, speaker_id=...)`.
- **Alternatives considered**: 
  - A) Ручная загрузка моделей перед запуском — отклонено (больше шагов, vosk-tts уже делает это автоматически).
  - B) Использование vosk-api (speech recognition) — отклонено (это для распознавания, не синтеза).

### Decision: Модель по умолчанию — vosk-model-tts-ru-0.9-multi
- **Rationale**: Единственная доступная русская модель в vosk-tts с поддержкой 5 голосов (speaker_id 0-4: 3 женских, 2 мужских).
- **Alternatives considered**: 
  - A) Другие языковые модели — не применимо для русского бота.
  - B) Кастомные модели — возможно через TTS_MODEL, но не требуется сейчас.

### Decision: speaker_id в диапазоне 0-4 для мультиголосовой модели
- **Rationale**: Документация vosk-tts указывает speaker_id от 0 до 4 включительно для модели vosk-model-tts-ru-0.9-multi.
- **Alternatives considered**: 
  - A) Без валидации speaker_id — отклонено (требование FR-008 на валидацию).
  - B) Динамическое определение диапазона — избыточно для одной известной модели.

### Decision: Выходной формат по умолчанию — wav, с конвертацией в mp3 при необходимости
- **Rationale**: vosk-tts генерирует wav; для mp3 используем pydub (как в существующих провайдерах).
- **Alternatives considered**: 
  - A) Только wav — отклонено (нужна совместимость с существующим конфигом audio_format).

### Decision: Реализация по паттерну PiperSynthesis
- **Rationale**: Аналогичная структура: lazy loading модели, метрики, логирование, конвертация аудио.
- **Alternatives considered**: 
  - A) Копирование паттерна Silero — отклонено (Piper ближе по архитектуре: простой model + synth API).

## API Reference

```python
from vosk_tts import Model, Synth

# Загрузка модели (автоскачивание)
model = Model(model_name="vosk-model-tts-ru-0.9-multi")
synth = Synth(model)

# Синтез речи
synth.synth("Привет мир!", "out.wav", speaker_id=2)
```

## CLI Reference

```bash
# Установка
pip install vosk-tts

# Использование встроенной CLI
vosk-tts -n vosk-model-tts-ru-0.9-multi -s 2 --input "Привет мир!" --output out.wav
```


