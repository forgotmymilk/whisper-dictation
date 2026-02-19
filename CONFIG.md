# Configuration Reference

All settings are in `config.json`. Every field is optional — defaults are applied for anything missing.

---

## Hotkeys

| Field | Default | Description |
|-------|---------|-------------|
| `hotkey` | `"f15"` | Hold-to-record key |
| `pause_hotkey` | `"f14"` | Toggle pause/resume |

## Model & Device

| Field | Default | Values | Description |
|-------|---------|--------|-------------|
| `model` | `"auto"` | `tiny` `base` `small` `medium` `large-v2` `large-v3` `auto` | Model size. Larger = more accurate but slower |
| `compute_type` | `"auto"` | `float16` `int8` `auto` | Precision. `float16` for GPU, `int8` for CPU |
| `device` | `"auto"` | `cuda` `cpu` `auto` | Inference device |
| `language` | `null` | ISO code or `null` | Force language, or `null` for auto-detect |

## Text Processing

| Field | Default | Description |
|-------|---------|-------------|
| `enable_punctuation` | `true` | Auto-add punctuation (。，！？ / . , ! ?) |
| `enable_formatting` | `true` | Paragraph breaks, CJK-Latin spacing |
| `enable_capitalization` | `true` | Capitalize English sentences |
| `max_line_length` | `80` | Max chars per line when formatting is on |

## Output & Audio

| Field | Default | Description |
|-------|---------|-------------|
| `output_mode` | `"type"` | `type` / `clipboard` / `both` | Output format |
| `input_method` | `"unicode"` | `unicode` / `keyboard` / `clipboard` | `unicode` is best for games and floating windows |
| `sample_rate` | `16000` | Audio sample rate in Hz (16000 optimal for Whisper) |
| `audio_threshold` | `0.01` | Min mic level for startup test |
| `min_duration` | `0.5` | Ignore recordings shorter than this (sec) |
| `auto_minimize_console` | `true` | Minimize console after model loads |
| `sound_feedback` | `true` | Beep on record start / processing start |

## Transcription

| Field | Default | Description |
|-------|---------|-------------|
| `initial_prompt` | `null` | Vocabulary hint. Use bilingual text for mixed input |
| `beam_size` | `5` | Search width (1–10). Higher = more accurate |
| `best_of` | `5` | Candidates per beam (1–10) |
| `temperature` | `[0, 0.2, 0.4, 0.6, 0.8, 1.0]` | Sampling temp. List = automatic fallback |
| `condition_on_previous_text` | `true` | Use prior output as context |
| `repetition_penalty` | `1.1` | Penalize repeated tokens (1.0 = off) |
| `no_repeat_ngram_size` | `3` | Block repeating N-grams (0 = off) |

## Quality Thresholds

| Field | Default | Description |
|-------|---------|-------------|
| `no_speech_threshold` | `0.6` | Skip segments with high no-speech probability |
| `log_prob_threshold` | `-1.0` | Reject low-confidence output |
| `compression_ratio_threshold` | `2.4` | Reject gibberish (high compression = bad) |
| `hallucination_silence_threshold` | `1.0` | Skip silent segments that might hallucinate (sec) |

## Voice Activity Detection

| Field | Default | Description |
|-------|---------|-------------|
| `vad_filter` | `true` | Filter non-speech segments |
| `vad_parameters.threshold` | `0.5` | Speech sensitivity (lower = more sensitive) |
| `vad_parameters.min_silence_duration_ms` | `300` | Min silence to split segments |
| `vad_parameters.min_speech_duration_ms` | `250` | Min speech to keep |
| `vad_parameters.max_speech_duration_s` | `30` | Max single segment duration |

## User Profile

| Field | Default | Description |
|-------|---------|-------------|
| `user_profile.name` | `""` | Your name |
| `user_profile.primary_language` | `"auto"` | `auto` `zh` `en` `mixed` |
| `user_profile.formality` | `"casual"` | `casual` `formal` `business` |
| `user_profile.common_phrases` | `[]` | Frequently used terms |
