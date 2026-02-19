# Configuration Reference

All settings are in `config.json`. Every field is optional — defaults are used for anything missing.

## Hotkeys

| Field | Default | Values | Description |
|-------|---------|--------|-------------|
| `hotkey` | `"f15"` | Any key name | Hold-to-record key |
| `pause_hotkey` | `"f14"` | Any key name | Toggle pause/resume |

## Model & Device

| Field | Default | Values | Description |
|-------|---------|--------|-------------|
| `model` | `"auto"` | `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`, `auto` | Whisper model size. `auto` detects from GPU VRAM |
| `compute_type` | `"auto"` | `float16`, `int8`, `auto` | Quantization. `float16` for GPU, `int8` for CPU |
| `device` | `"auto"` | `cuda`, `cpu`, `auto` | `auto` detects GPU availability |
| `language` | `null` | `null`, `"zh"`, `"en"`, etc. | Force language. `null` = auto-detect per utterance |

## Text Processing

| Field | Default | Values | Description |
|-------|---------|--------|-------------|
| `enable_punctuation` | `true` | `true`/`false` | Auto-add Chinese/English punctuation |
| `enable_formatting` | `true` | `true`/`false` | Layout formatting (paragraph breaks, line length) |
| `enable_capitalization` | `true` | `true`/`false` | Auto-capitalize English sentences |
| `max_line_length` | `80` | Integer | Max characters per line when formatting is on |

## Output

| Field | Default | Values | Description |
|-------|---------|--------|-------------|
| `output_mode` | `"type"` | `type`, `clipboard`, `both` | `type` = simulate keyboard. `clipboard` = copy only. `both` = both |

## Audio

| Field | Default | Values | Description |
|-------|---------|--------|-------------|
| `audio_threshold` | `0.01` | 0.0–1.0 | Minimum mic level to consider "working" in test |
| `min_duration` | `0.5` | Seconds | Ignore recordings shorter than this |

## Transcription (Advanced)

| Field | Default | Values | Description |
|-------|---------|--------|-------------|
| `initial_prompt` | `null` | String or `null` | Hint to Whisper for vocabulary/style. Use bilingual text for mixed input |
| `beam_size` | auto | 1–10 | Search width. Higher = more accurate but slower. Auto: 5 for large, 3 for others |
| `best_of` | auto | 1–10 | Candidates per beam. Auto: 5 for large, 3 for others |
| `condition_on_previous_text` | `true` | `true`/`false` | Use prior output as context. Helps coherence, may cause repetition |

## Voice Activity Detection (VAD)

| Field | Default | Values | Description |
|-------|---------|--------|-------------|
| `vad_filter` | `true` | `true`/`false` | Filter out non-speech segments |
| `vad_parameters.threshold` | `0.5` | 0.0–1.0 | Speech detection sensitivity. Lower = more sensitive |
| `vad_parameters.min_silence_duration_ms` | `300` | ms | Minimum silence to split segments |
| `vad_parameters.min_speech_duration_ms` | `250` | ms | Minimum speech duration to keep |
| `vad_parameters.max_speech_duration_s` | `30` | seconds | Maximum single speech segment |

## User Profile

| Field | Default | Values | Description |
|-------|---------|--------|-------------|
| `user_profile.name` | `""` | String | Your name (for future personalization) |
| `user_profile.primary_language` | `"auto"` | `auto`, `zh`, `en`, `mixed` | Preferred language hint |
| `user_profile.formality` | `"casual"` | `casual`, `formal`, `business` | Text style preference |
| `user_profile.common_phrases` | `[]` | String array | Frequently used terms for improved accuracy |
