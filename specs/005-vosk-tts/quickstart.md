# Quickstart: Vosk TTS

## 1. Установка зависимости

```bash
uv add vosk-tts
```

## 2. Настройка окружения

Добавить в `.env`:

```bash
TTS_ENGINE=vosk
TTS_MODEL=vosk-model-tts-ru-0.9-multi
TTS_SPEAKER_ID=2
TTS_AUDIO_FORMAT=wav
```

## 3. Тест через CLI

```bash
python -m src.cli.vosk_tts \
  --text "Привет, это тест Vosk TTS!" \
  --out /tmp/vosk_test.wav \
  --speaker-id 2

# Прослушать
aplay /tmp/vosk_test.wav
```

## 4. Выбор голоса

Модель `vosk-model-tts-ru-0.9-multi` поддерживает 5 голосов:

| speaker_id | Описание |
|------------|----------|
| 0 | Женский голос 1 |
| 1 | Женский голос 2 |
| 2 | Мужской голос 1 |
| 3 | Женский голос 3 |
| 4 | Мужской голос 2 |

## 5. Запуск бота с Vosk

```bash
# Убедиться что .env настроен
TTS_ENGINE=vosk

# Запустить бота
python -m src.cli.run_bot
```

## 6. Проверка

1. Отправить текстовое сообщение боту
2. Получить голосовое сообщение в ответ
3. Убедиться что голос соответствует выбранному speaker_id


