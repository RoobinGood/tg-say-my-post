# Contracts: Vosk TTS

## CLI Contract: vosk_tts.py

### Synopsis

```bash
python -m src.cli.vosk_tts --text TEXT --out PATH [OPTIONS]
python -m src.cli.vosk_tts --text-file FILE --out PATH [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--text TEXT` | yes* | Текст для синтеза |
| `--text-file FILE` | yes* | Файл с текстом |
| `--out PATH` | yes | Путь выходного файла |
| `--model NAME` | no | Имя модели vosk-tts |
| `--speaker-id N` | no | ID голоса (0-4) |
| `--format FORMAT` | no | wav или mp3 |
| `--config PATH` | no | Путь к .env файлу |
| `--prefix TEXT` | no | Префикс для озвучки |

*одно из --text или --text-file обязательно

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Invalid input (empty text, too long) |
| 3 | File not found |
| 4 | OS/IO error |

### Example

```bash
python -m src.cli.vosk_tts \
  --text "Привет, мир!" \
  --out /tmp/test.wav \
  --model vosk-model-tts-ru-0.9-multi \
  --speaker-id 2
```

## Synthesis Contract: VoskSynthesis

### Interface

```python
class VoskSynthesis(SynthesisProvider):
    def __init__(self, config: VoskConfig, tts_config: TTSConfig) -> None: ...
    
    def synth(
        self,
        text: str,
        prefix: str | None,
        out_path: Path
    ) -> SynthesisResult: ...
```

### SynthesisResult

```python
@dataclass(frozen=True)
class SynthesisResult:
    path: Path              # Путь к аудиофайлу
    duration_seconds: float # Длительность аудио
    synth_ms: float         # Время синтеза
    model_load_ms: float | None  # Время загрузки модели
    audio_format: str | None     # wav или mp3
```

### Errors

| Error | When |
|-------|------|
| `ValueError("empty text")` | Пустой входной текст |
| `ValueError("text too long")` | Текст превышает лимит |
| `ValueError("invalid speaker_id")` | speaker_id вне диапазона |
| `OSError` | Ошибка синтеза или записи файла |

## Configuration Contract

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TTS_ENGINE` | yes | - | `vosk` для включения Vosk |
| `TTS_MODEL` | yes | - | Имя модели (e.g. `vosk-model-tts-ru-0.9-multi`) |
| `TTS_SPEAKER_ID` | no | 0 | ID голоса |
| `TTS_AUDIO_FORMAT` | no | wav | wav или mp3 |
| `TTS_TEXT_LIMIT` | no | 1000 | Макс. длина текста |
| `TTS_CACHE_DIR` | no | system | Директория кеша |
| `TTS_METRICS_FILE` | no | None | Путь к метрикам |


