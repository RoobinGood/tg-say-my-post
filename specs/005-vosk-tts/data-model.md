# Data Model: Vosk TTS Integration

## Entities

### VoskConfig

Конфигурация модуля Vosk TTS.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| model_name | str | yes | - | Имя модели vosk-tts (e.g. `vosk-model-tts-ru-0.9-multi`) |
| speaker_id | int | no | 0 | ID голоса (0-4 для русской модели) |
| audio_format | str | no | wav | Формат выходного аудио (wav, mp3) |
| cache_dir | Path | no | system default | Директория кеша моделей |
| metrics_path | Path | no | None | Путь к файлу метрик |

**Validation rules**:
- `model_name` не может быть пустым
- `speaker_id` должен быть в диапазоне 0-4 для известных моделей
- `audio_format` только wav или mp3

### TTSEngine (расширение)

```python
class TTSEngine(str, Enum):
    SILERO = "silero"
    PIPER = "piper"
    VOSK = "vosk"    # new
    STUB = "stub"
```

### VoskSynthesis

Класс синтеза речи.

| Attribute | Type | Description |
|-----------|------|-------------|
| config | VoskConfig | Конфигурация |
| _model | Model | None | Lazy-loaded модель vosk-tts |
| _synth | Synth | None | Lazy-loaded синтезатор |
| _model_load_ms | float | None | Время загрузки модели |

**Methods**:
- `synth(text: str, prefix: str | None, out_path: Path) -> SynthesisResult`

## Relationships

```
Config
├── tts: TTSConfig (engine=vosk)
├── silero: SileroConfig
├── piper: PiperConfig
└── vosk: VoskConfig (new)
```

## State Transitions

```
VoskSynthesis states:
[Initialized] --ensure_model()--> [Model Loaded] --synth()--> [Synthesizing]
```


