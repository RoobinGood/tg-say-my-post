# Data Model: Telegram TTS Bot

## Entities

- IncomingItem  
  - Fields: message_id, chat_id, sender_name (optional), channel_title (optional), text, source_type (direct | forwarded_user | forwarded_channel), created_at.  
  - Rules: text length ≤ 2000; source_type determines audio prefix.

- AudioJob  
  - Fields: job_id, chat_id, order (incremental per chat), incoming_item_ref, status (pending | synthesizing | sent | failed), error (optional).  
  - Rules: FIFO per chat; on fail, status=failed and user получает текстовую ошибку.

- SynthResult  
  - Fields: job_id, audio_path, prefix_used (none | user:<name> | channel:<title>), duration_estimate (optional).  
  - Rules: Заглушка всегда выдаёт фиксированный mp3; prefix_used отражает добавленную фразу.

## Relationships

- AudioJob references one IncomingItem.
- SynthResult references one AudioJob.

## State Notes

- AudioJob transitions: pending → synthesizing → sent | failed.
- Requeue не требуется; при fail возвращается текстовая ошибка.


