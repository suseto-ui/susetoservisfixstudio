try:
    from google import genai
except ImportError:
    genai = None

from config import DEFAULT_MODEL

class AIDiagnosticEngine:
    """
    Automated diagnostic helper utilizing Google GenAI SDK.
    Parses complex error dumps from ADB, Fastboot, or low-level EDL interfaces.
    """
    def __init__(self) -> None:
        # Client initializes using GEMINI_API_KEY env var
        if genai is not None:
            try:
                self.client = genai.Client()
            except Exception:
                self.client = None
        else:
            self.client = None

    def analyze_log(self, log_text: str) -> str:
        """Analyze servicing logs with Gemini model and return steps to resolve."""
        if not log_text.strip():
            return "Log je prázdný, není co analyzovat."

        prompt = (
            "Jsi servisní technik mobilních telefonů. Analyzuj tento chybový log "
            "z ADB/Fastboot/EDL/BROM a doporuč krok za krokem řešení:\n\n" + log_text
        )

        try:
            response = self.client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt
            )
            return response.text or "Odpověď od modelu je prázdná."
        except Exception as e:
            return f"AI Diagnostika selhala: {str(e)}"
