import requests
import json
import time

from ai_presets import AI_PERSONAS, AI_STYLES, AI_TRANSLATIONS

class AIPolish:
    def __init__(self, config):
        self.config = config

    def polish_text(self, text):
        """
        Send text to LLM for polishing based on configured mode.
        Returns the polished text, or None if failed/disabled.
        """
        # 1. Check if enabled
        if not self.config.get("ai_polish_enabled", False):
            return text

        api_key = self.config.get("ai_api_key", "").strip()
        if not api_key:
            print("⚠️  AI Polish enabled but no API Key provided.")
            return text

        # 2. Get the active prompt builder pieces
        base_url = self.config.get("ai_base_url", "https://api.openai.com/v1").rstrip("/")
        model = self.config.get("ai_model", "gpt-4o-mini")
        
        # Load user's custom dictionaries from config
        custom_personas = self.config.get("ai_custom_personas", {})
        custom_styles = self.config.get("ai_custom_styles", {})
        custom_translations = self.config.get("ai_custom_translations", {})
        
        # Merge built-in presets with user customs
        all_personas = {**AI_PERSONAS, **custom_personas}
        all_styles = {**AI_STYLES, **custom_styles}
        all_translations = {**AI_TRANSLATIONS, **custom_translations}

        # Check Active Profile logic
        active_profile_name = self.config.get("ai_active_profile", "")
        saved_profiles = self.config.get("ai_saved_profiles", {})

        if active_profile_name and active_profile_name in saved_profiles:
            profile = saved_profiles[active_profile_name]
            p_key = profile.get("persona", "None")
            s_key = profile.get("style", "None")
            t_key = profile.get("translation", "None")
        else:
            # Fallback to direct singular selections if no profile is active 
            # (or for backward compatibility / manual GUI mode)
            p_key = self.config.get("ai_persona", "None")
            s_key = self.config.get("ai_style", "None")
            t_key = self.config.get("ai_translation", "None")

        # Fetch the actual descriptive strings based on keys
        persona_str = all_personas.get(p_key, "")
        style_str = all_styles.get(s_key, "")
        trans_str = all_translations.get(t_key, "")

        # 3. Build the System Prompt
        system_prompt_parts = ["Fix grammar, spelling, and phrasing in the following text."]
        
        if persona_str:
            system_prompt_parts.append(f"[PERSONA]\n{persona_str}")
            
        if style_str:
            system_prompt_parts.append(f"[STYLE]\n{style_str}")
            
        if trans_str:
            system_prompt_parts.append(f"[TRANSLATION TARGET]\n{trans_str}")
        else:
            # If Translation is "None" / empty, enforce Language Preservation
            language_directive = (
                "[LANGUAGE PRESERVATION]\n"
                "CRITICAL: You MUST preserve the exact language(s) of the original text. "
                "If it is English, output English. If it is Chinese, output Chinese. "
                "If it is a mix of both (code-switching, e.g. Chinese with English technical terms), "
                "you MUST maintain that exact bilingual structure. NEVER automatically translate between languages unless explicitly instructed."
            )
            system_prompt_parts.append(language_directive)
            
        system_prompt_parts.append("Output only the refined text. Do not add conversational intro/outro or quotes.")
        
        system_prompt = "\n\n".join(system_prompt_parts)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.7
        }

        # 3. Call API
        try:
            print(f"🤖 AI Polishing ({model})...", end=" ")
            start_t = time.time()
            
            is_anthropic = "api.anthropic.com" in base_url
            
            if is_anthropic:
                anthropic_url = f"{base_url}/messages"
                anthropic_headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
                anthropic_payload = {
                    "model": model,
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": text}
                    ],
                    "temperature": 0.7
                }
                response = requests.post(
                    anthropic_url,
                    headers=anthropic_headers,
                    json=anthropic_payload,
                    timeout=10
                )
                response.raise_for_status()
                result = response.json()
                polished = result["content"][0]["text"].strip()
            else:
                response = requests.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=10  # 10s timeout
                )
                response.raise_for_status()
                
                result = response.json()
                polished = result["choices"][0]["message"]["content"].strip()
            
            duration = time.time() - start_t
            print(f"✓ Done ({duration:.1f}s)")
            return polished

        except Exception as e:
            print(f"\n❌ AI Polish failed: {e}")
            return text  # Fallback to original text
