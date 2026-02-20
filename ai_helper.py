import requests
import json
import time

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

        # 2. Prepare Request
        base_url = self.config.get("ai_base_url", "https://api.openai.com/v1").rstrip("/")
        model = self.config.get("ai_model", "gpt-4o-mini")
        prompt_template = self.config.get("ai_prompt_template", "Fix grammar and polish user input.")
        
        system_prompt = f"{prompt_template}\nOutput only the refined text. Do not add intro/outro."
        
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
