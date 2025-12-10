# Data Model: Silero TTS module

## Entities

- TextInput  
  - Fields: text, language, voice, source (cli|bot), requested_format, requested_sample_rate.  
  - Rules: длина ≤ 1000 символов (первая версия); язык/голос должны быть поддержаны конфигом.

- SynthesisConfig  
  - Fields: voice_id, language, sample_rate, format (wav|mp3), output_dir, device (cpu|cuda), log_level, model_path/cache_dir.  
  - Rules: заполняется из файла с переопределением через env; валидация формата/пути/устройства.

- SynthesisJob  
  - Fields: job_id, text_input_ref, config_snapshot, status (pending|running|failed|done), error_message (optional), started_at, finished_at.  
  - Rules: детерминированная генерация при одинаковом тексте/конфиге/версии модели; при ошибке статус=failed.

- SynthesisResult  
  - Fields: job_id, audio_path, audio_format, audio_duration, model_name, voice_used.  
  - Rules: audio_path указывает на локальный файл, который можно отдать ботом или вернуть в CLI.

- MetricsRecord  
  - Fields: job_id, model_load_ms (optional, для cold start), synthesis_ms, audio_duration, timestamp.  
  - Rules: логируется в stdout/файл; хранение персистентно не требуется.

## Relationships

- SynthesisJob ссылается на TextInput и SynthesisConfig (snapshot).  
- SynthesisResult и MetricsRecord ссылаются на SynthesisJob.

## State Notes

- SynthesisJob: pending → running → done | failed.  
- При cold start может фиксироваться модельная загрузка один раз; повторно не прибавляется.

