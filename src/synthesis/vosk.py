import json
import re
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
from pydub import AudioSegment

from src.synthesis.interface import SynthesisProvider, SynthesisResult
from src.utils.config import TTSConfig, VoskConfig
from src.utils.logging import get_logger, log_metrics, measure_ms

try:
    from vosk_tts import Model, Synth
except Exception as exc:  # noqa: BLE001
    raise ImportError("vosk-tts is required for VoskSynthesis") from exc


class VoskSynthesis(SynthesisProvider):
    def __init__(self, config: VoskConfig, tts_config: TTSConfig) -> None:
        self.config = config
        self.tts_config = tts_config
        self.log = get_logger(__name__)
        self._model: Optional[Model] = None
        self._synth: Optional[Synth] = None
        self._model_load_ms: float | None = None
        self.metrics_label = "vosk_tts"

    def _ensure_model(self) -> None:
        if self._model is not None and self._synth is not None:
            return

        start_ms = measure_ms()
        self._model = Model(model_name=self.config.model_name)
        self._synth = Synth(self._model)
        self._model_load_ms = measure_ms() - start_ms
        self.log.info(
            "vosk model loaded name=%s speaker_id=%s load_ms=%.1f",
            self.config.model_name,
            self.config.speaker_id,
            self._model_load_ms,
        )

    def _filter_unsupported_chars(self, text: str) -> str:
        """Remove characters not supported by vosk-tts phoneme dictionary.
        
        Keeps all letters, digits, whitespace, and punctuation.
        Only removes/replaces special symbols not in transliteration dictionary.
        """
        project_root = Path(__file__).resolve().parents[2]
        dict_path = project_root / "src" / "preprocessing" / "dictionaries" / "transliteration.json"

        supported_symbols: set[str] = set()
        if dict_path.exists():
            with open(dict_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                supported_symbols = set(data.get("symbols", {}).keys())

        dash_like = {"—", "–", "−", "‑", "‒", "―"}

        result = []
        for char in text:
            if char in dash_like:
                result.append("-")
                continue

            if char.isalpha() or char.isdigit() or char.isspace():
                result.append(char)
            elif char in supported_symbols:
                result.append(char)
            elif char in {"«", "»"}:
                result.append('"')
            elif char in {"„", "‚", "‹", "›"}:
                result.append("'")
            elif char in {".", ",", "!", "?", ";", ":", "-", "(", ")", "[", "]", '"', "'", "+"}:
                result.append(char)
            else:
                pass

        return "".join(result)

    def _split_into_chunks(self, text: str, max_chars: int = 400) -> list[str]:
        """Split text into chunks that fit within BERT model limit (~512 tokens).
        
        For Russian text, ~400 chars ≈ ~100-130 tokens, leaving safe margin.
        """
        if len(text) <= max_chars:
            return [text]

        sentences = re.split(r'([.!?]\s+)', text)
        chunks: list[str] = []
        current_chunk = ""

        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            separator = sentences[i + 1] if i + 1 < len(sentences) else ""

            if len(sentence) > max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                chunks.extend(self._split_long_sentence(sentence, max_chars))
                current_chunk = separator
                continue

            test_chunk = current_chunk + sentence + separator

            if len(test_chunk) > max_chars and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + separator
            else:
                current_chunk = test_chunk

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    def _split_long_sentence(self, sentence: str, max_chars: int) -> list[str]:
        """Split a very long sentence that doesn't fit in one chunk."""
        if len(sentence) <= max_chars:
            return [sentence]

        parts = re.split(r'([,;:]\s+)', sentence)
        chunks: list[str] = []
        current = ""

        for i in range(0, len(parts), 2):
            part = parts[i]
            separator = parts[i + 1] if i + 1 < len(parts) else ""

            if len(part) > max_chars:
                if current:
                    chunks.append(current.strip())
                    current = ""
                chunks.append(part[:max_chars])
                remaining = part[max_chars:]
                if remaining:
                    chunks.extend(self._split_long_sentence(remaining, max_chars))
                current = separator
            else:
                test = current + part + separator
                if len(test) > max_chars and current:
                    chunks.append(current.strip())
                    current = part + separator
                else:
                    current = test

        if current.strip():
            chunks.append(current.strip())

        return chunks if chunks else [sentence[:max_chars]]

    def synth(self, text: str, prefix: str | None, out_path: Path) -> SynthesisResult:
        if not text.strip():
            raise ValueError("empty text")
        full_text = f"{prefix}. {text}" if prefix else text
        if len(full_text) > self.tts_config.text_limit:
            raise ValueError("text too long")

        self._ensure_model()
        assert self._model is not None
        assert self._synth is not None

        start_ms = measure_ms()
        filtered_text = self._filter_unsupported_chars(full_text)
        chunks = self._split_into_chunks(filtered_text)
        audio_segments: list[np.ndarray] = []
        sample_rate: int | None = None

        try:
            for i, chunk in enumerate(chunks):
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    chunk_path = Path(tmp.name)
                try:
                    self._synth.synth(chunk, str(chunk_path), speaker_id=self.config.speaker_id)
                    if not chunk_path.exists():
                        raise OSError(f"vosk returned no audio file for chunk {i+1}")

                    audio_data, sr = sf.read(chunk_path)
                    if sample_rate is None:
                        sample_rate = sr
                    elif sample_rate != sr:
                        raise OSError(f"sample rate mismatch: {sample_rate} vs {sr}")

                    audio_segments.append(audio_data)
                finally:
                    chunk_path.unlink(missing_ok=True)

            if not audio_segments:
                raise OSError("vosk returned no audio")

            combined_audio = np.concatenate(audio_segments)
            duration_seconds = float(len(combined_audio) / sample_rate) if sample_rate else 0.0

            out_path = out_path.with_suffix(f".{self.config.audio_format}")
            out_path.parent.mkdir(parents=True, exist_ok=True)

            if self.config.audio_format == "wav":
                sf.write(out_path, combined_audio, sample_rate)
            else:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path = Path(tmp.name)
                try:
                    sf.write(tmp_path, combined_audio, sample_rate)
                    audio_seg = AudioSegment.from_wav(tmp_path)
                    audio_seg.export(out_path, format="mp3")
                finally:
                    tmp_path.unlink(missing_ok=True)  # type: ignore[arg-type]

        except Exception as exc:  # noqa: BLE001
            raise OSError(f"vosk synthesis failed: {exc}") from exc

        synth_ms = measure_ms() - start_ms
        result = SynthesisResult(
            path=out_path,
            duration_seconds=duration_seconds,
            synth_ms=synth_ms,
            model_load_ms=self._model_load_ms,
            audio_format=self.config.audio_format,
        )
        log_metrics(
            self.log,
            self.metrics_label,
            load_ms=self._model_load_ms,
            synth_ms=synth_ms,
            duration_seconds=duration_seconds,
            metrics_file=self.config.metrics_path,
        )
        return result


__all__ = ["VoskSynthesis"]

