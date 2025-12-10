# Data Model: Piper TTS support

## Entities

### TTSConfig
- Fields: `engine` (silero|piper), `model` (string, required per engine), `text_limit` (int >0), `cache_dir` (path), `checksum` (optional, for weights), `download_url` (optional if weights автодоводятся), `timeout` (ms, optional).
- Rules: engine/model must be validated at startup; missing model blocks startup; text_limit enforced before synthesis; cache_dir must exist or быть создана; checksum/size проверяются перед загрузкой модели.

### VoiceProfile
- Fields: `engine`, `model`, `language`, `voice_name` (optional), `sampling_rate` (int, optional), `expected_latency_ms` (optional note), `requires_download` (bool).
- Rules: модель должна соответствовать выбранному движку; language должен быть совместим с ботом (русский приоритет); используется для выбора файла весов/конфига Piper.

### WeightCache
- Fields: `path`, `engine`, `model`, `checksum`, `size_bytes`, `last_verified_at`.
- Rules: при старте проверять checksum/size; при расхождении — блокировать старт с понятной ошибкой; скачивание пишет обновлённые метаданные.

## Relationships
- `TTSConfig.model` → `VoiceProfile.model` (1:1 selected profile).
- `VoiceProfile` → `WeightCache` (1:1 per model stored locally).

## Lifecycle
1. Startup: validate TTSConfig, ensure cache_dir; verify or download weights per VoiceProfile; populate WeightCache metadata.
2. Run: for каждый запрос проверять text_limit, затем вызывать движок с выбранной моделью.
3. Failure: если движок недоступен/веса повреждены — запрос отклоняется, логируется, авто-фолбэк не включается.

