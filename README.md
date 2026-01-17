# tg-say-my-post

Telegram bot that converts incoming messages to voice replies.

## Features
- Supports plain text messages
- Supports forwarded posts from channels with a prefixed line
- Supports forwarded messages from users with a prefixed line
- Access control by allowed user IDs
- Pluggable TTS providers

## Setup
1. Copy `.env.example` to `.env` and fill in your values.
2. Install dependencies:
   - `npm ci`

## Run locally
- Development: `npm run dev`
- Production build: `npm run build`
- Start: `npm start`

## Configuration
All settings are provided via environment variables:
- `BOT_TOKEN`
- `ALLOWED_USER_IDS`
- `PREPROCESSING_ENABLED` (default: `false`)
- `TTS_PROVIDER` (`mock` or `salute`)

SaluteSpeech settings (used when `TTS_PROVIDER=salute`):
- `SALUTE_AUTH_KEY`
- `SALUTE_SCOPE` (default: `SALUTE_SPEECH_PERS`)
- `SALUTE_TOKEN_URL` (default: `https://ngw.devices.sberbank.ru:9443/api/v2/oauth`)
- `SALUTE_SYNTH_URL` (default: `https://smartspeech.sber.ru/rest/v1/text:synthesize`)
- `SALUTE_VOICE` (default: `Nec_24000`)
- `SALUTE_FORMAT` (default: `wav16`)
- `SALUTE_USE_SSML` (default: `false`)
- `SALUTE_TMP_DIR` (default: `tmp`)
- `SALUTE_TIMEOUT_MS` (default: `30000`)
- `SALUTE_TOKEN_REFRESH_MARGIN_MS` (default: `60000`)

## Docker
Build and run:
- `docker build -t tg-say-my-post .`
- `docker run --env-file .env tg-say-my-post`
# Telegram TTS Bot

Stub implementation for Telegram text-to-speech bot with queueing and synthesis placeholder.


## bot

```sh
uv run python -m src.cli.run_bot
```

### Configuration

#### Bot timeouts

- `BOT_READ_TIMEOUT` (по умолчанию: `120`) — таймаут чтения ответа от Telegram API в секундах
- `BOT_WRITE_TIMEOUT` (по умолчанию: `300`) — таймаут записи данных в Telegram API в секундах (важно для больших аудиофайлов, рекомендуется 300+ для файлов >5 МБ)
- `BOT_CONNECT_TIMEOUT` (по умолчанию: `30`) — таймаут установки соединения с Telegram API в секундах
- `BOT_POOL_TIMEOUT` (по умолчанию: `30`) — таймаут ожидания свободного соединения из пула в секундах (частая причина `TimedOut` при отправке voice/файлов)

Пример:

```sh
BOT_READ_TIMEOUT=300
BOT_WRITE_TIMEOUT=300
BOT_CONNECT_TIMEOUT=300
BOT_POOL_TIMEOUT=300
```

## Text preprocessing

Optional programmatic preprocessing (enable via config):
- Capitalizes the first letter if it is lowercase
- Adds a trailing dot if the line ends with a letter/digit and has no dot
- Replaces a leading emoji with a dash, then removes all emoji

### Configuration
- `PREPROCESSING_ENABLED` (default: `false`)

