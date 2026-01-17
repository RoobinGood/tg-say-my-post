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

## Text preprocessing
Enabled with `PREPROCESSING_ENABLED=true`. It prepares text for speech synthesis:
- leading emoji is replaced with a dash, other emojis are removed
- the first lowercase letter at the start is uppercased
- if the line ends with a letter or digit, a period is appended

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
