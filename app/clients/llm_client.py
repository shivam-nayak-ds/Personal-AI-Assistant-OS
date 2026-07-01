"""
Multi-Provider LLM Client for Hermes AI OS

Providers:
  - Groq      → ultra-fast chat (Llama 3.1 70b/8b)
  - OpenRouter → Claude for critique, GPT-4o for escalation
  - Gemini     → free embeddings + fallback LLM
  - OpenAI     → TTS voice (optional)

Routing strategy:
  Chat (general)  → Groq 70b  (fast, cheap)
  Self-Critique   → Claude via OpenRouter (best reasoning)
  Embeddings      → Gemini embedding-001 (free)
  Escalation      → GPT-4o via OpenRouter (low volume)
  Fallback        → Gemini 1.5 Flash (free)
"""

import json
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
import httpx

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────
# GROQ CLIENT
# ─────────────────────────────────────────

class GroqClient:
    """
    Groq — ultra-fast Llama 3.1 inference.
    Used for: chat, reasoning, Whisper STT.
    Speed: ~500 tokens/sec (10× faster than OpenAI).
    """

    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — Groq disabled")
            self._client = None
            return
        # Groq is OpenAI-compatible, use AsyncOpenAI with custom base_url
        self._client = AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        logger.info("✅ Groq client initialized")

    @property
    def available(self) -> bool:
        return self._client is not None

    async def chat(
        self,
        messages: List[Dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        if not self._client:
            raise RuntimeError("Groq not configured")

        chosen_model = model or settings.GROQ_MODEL_SMART
        response = await self._client.chat.completions.create(
            model=chosen_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        tokens_in = response.usage.prompt_tokens
        tokens_out = response.usage.completion_tokens
        logger.info(f"Groq {chosen_model}: {tokens_in}→{tokens_out} tokens")
        return response.choices[0].message.content

    async def chat_fast(self, messages: List[Dict], **kwargs) -> str:
        """Use the small/fast model for simple tasks"""
        return await self.chat(messages, model=settings.GROQ_MODEL_FAST, **kwargs)


# ─────────────────────────────────────────
# OPENROUTER CLIENT
# ─────────────────────────────────────────

class OpenRouterClient:
    """
    OpenRouter — single API for Claude, GPT-4o, and 50+ models.
    Used for: self-critique (Claude), escalation (GPT-4o).
    """

    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY not set — OpenRouter disabled")
            self._client = None
            return
        self._client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )
        logger.info("✅ OpenRouter client initialized")

    @property
    def available(self) -> bool:
        return self._client is not None

    async def chat(
        self,
        messages: List[Dict],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        if not self._client:
            raise RuntimeError("OpenRouter not configured")

        chosen_model = model or settings.OPENROUTER_MODEL_CRITIQUE
        response = await self._client.chat.completions.create(
            model=chosen_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers={
                "HTTP-Referer": "https://hermes-ai.app",
                "X-Title": "Hermes AI OS",
            },
        )
        logger.info(f"OpenRouter {chosen_model}: response received")
        return response.choices[0].message.content

    async def critique(self, messages: List[Dict], **kwargs) -> str:
        """Use Claude for self-critique — best reasoning"""
        return await self.chat(messages, model=settings.OPENROUTER_MODEL_CRITIQUE, **kwargs)

    async def escalate(self, messages: List[Dict], **kwargs) -> str:
        """Use GPT-4o for escalation — highest quality"""
        return await self.chat(messages, model=settings.OPENROUTER_MODEL_COMPLEX, temperature=0.2, **kwargs)


# ─────────────────────────────────────────
# GEMINI CLIENT
# ─────────────────────────────────────────

class GeminiClient:
    """
    Google Gemini — free embeddings + fallback LLM.
    Used for: embeddings (768-dim), confidence scoring, fallback chat.
    """

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set — Gemini disabled")
            self._genai = None
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._genai = genai
            self._model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info("✅ Gemini client initialized")
        except ImportError:
            logger.error("google-generativeai not installed. Run: pip install google-generativeai")
            self._genai = None

    @property
    def available(self) -> bool:
        return self._genai is not None

    async def embed(self, text: str) -> List[float]:
        """Generate 768-dim embedding vector for text"""
        if not self._genai:
            raise RuntimeError("Gemini not configured")
        result = self._genai.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]

    async def embed_query(self, text: str) -> List[float]:
        """Embed a search query (different task_type for better recall)"""
        if not self._genai:
            raise RuntimeError("Gemini not configured")
        result = self._genai.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_query",
        )
        return result["embedding"]

    async def chat(self, prompt: str, temperature: float = 0.7) -> str:
        """Fallback chat using Gemini 1.5 Flash (free)"""
        if not self._genai:
            raise RuntimeError("Gemini not configured")
        response = self._model.generate_content(
            prompt,
            generation_config=self._genai.GenerationConfig(temperature=temperature),
        )
        logger.info(f"Gemini {settings.GEMINI_MODEL}: response received")
        return response.text


# ─────────────────────────────────────────
# UNIFIED LLM CLIENT
# ─────────────────────────────────────────

class LLMClient:
    """
    Unified multi-provider LLM client.

    Routing:
      chat()      → Groq (fast) → Gemini (fallback)
      critique()  → OpenRouter Claude
      embed()     → Gemini embedding-001
      escalate()  → OpenRouter GPT-4o

    Usage:
      llm = LLMClient()
      text = await llm.chat("What is Redis?")
      vector = await llm.embed("Redis is a cache")
      critique = await llm.critique(draft="...", question="...")
    """

    def __init__(self):
        self.groq = GroqClient()
        self.openrouter = OpenRouterClient()
        self.gemini = GeminiClient()

        available = []
        if self.groq.available: available.append("Groq")
        if self.openrouter.available: available.append("OpenRouter")
        if self.gemini.available: available.append("Gemini")

        if not available:
            logger.error("❌ No LLM providers configured! Add API keys to .env")
        else:
            logger.info(f"✅ LLM providers ready: {', '.join(available)}")

    # ─── CHAT ───────────────────────────────────

    async def chat(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List[Dict]] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        General chat — uses Groq for speed.
        Falls back to Gemini if Groq fails.
        """
        msgs = self._build_messages(prompt, messages, system)

        # Try Groq first (fast + cheap)
        if self.groq.available:
            try:
                return await self.groq.chat(msgs, temperature=temperature, max_tokens=max_tokens)
            except Exception as e:
                logger.warning(f"Groq failed: {e} — falling back to Gemini")

        # Fallback to Gemini
        if self.gemini.available:
            full_prompt = self._messages_to_prompt(msgs)
            return await self.gemini.chat(full_prompt, temperature=temperature)

        raise RuntimeError("No LLM available. Set GROQ_API_KEY or GEMINI_API_KEY in .env")

    async def chat_fast(self, prompt: str, system: Optional[str] = None) -> str:
        """Quick response using Groq small model"""
        msgs = self._build_messages(prompt, None, system)
        if self.groq.available:
            return await self.groq.chat_fast(msgs)
        return await self.chat(prompt=prompt, system=system)

    # ─── CRITIQUE (Claude) ───────────────────────

    async def critique(self, messages: List[Dict]) -> str:
        """
        Self-critique using Claude — best at finding errors.
        Falls back to Groq smart model.
        """
        if self.openrouter.available:
            try:
                return await self.openrouter.critique(messages)
            except Exception as e:
                logger.warning(f"OpenRouter critique failed: {e}")

        # Fallback
        if self.groq.available:
            return await self.groq.chat(messages, model=settings.GROQ_MODEL_SMART, temperature=0.2)

        raise RuntimeError("No critique provider available")

    # ─── ESCALATION (GPT-4o) ─────────────────────

    async def escalate(self, messages: List[Dict]) -> str:
        """
        Escalation path — use strongest model when confidence is low.
        """
        if self.openrouter.available:
            try:
                return await self.openrouter.escalate(messages)
            except Exception as e:
                logger.warning(f"Escalation failed: {e}")

        # Fall through to Groq smart
        if self.groq.available:
            return await self.groq.chat(messages, model=settings.GROQ_MODEL_SMART, temperature=0.1)

        raise RuntimeError("No escalation provider available")

    # ─── EMBEDDINGS (Gemini) ─────────────────────

    async def embed(self, text: str) -> List[float]:
        """Generate embedding vector — Gemini (free, 768-dim)"""
        if self.gemini.available:
            return await self.gemini.embed(text)
        raise RuntimeError("No embedding provider. Set GEMINI_API_KEY in .env")

    async def embed_query(self, text: str) -> List[float]:
        """Embed a search query"""
        if self.gemini.available:
            return await self.gemini.embed_query(text)
        raise RuntimeError("No embedding provider. Set GEMINI_API_KEY in .env")

    # ─── STRUCTURED OUTPUT ──────────────────────

    async def chat_json(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Chat and parse response as JSON.
        Adds JSON instruction to prompt automatically.
        """
        json_system = (system or "") + "\nRespond with valid JSON only. No markdown, no explanation."
        raw = await self.chat(prompt=prompt, system=json_system, temperature=0.1, **kwargs)

        # Strip markdown code blocks if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        return json.loads(raw.strip())

    # ─── UTILITIES ──────────────────────────────

    def _build_messages(
        self,
        prompt: Optional[str],
        messages: Optional[List[Dict]],
        system: Optional[str],
    ) -> List[Dict]:
        if messages:
            msgs = messages.copy()
        elif prompt:
            msgs = [{"role": "user", "content": prompt}]
        else:
            raise ValueError("Either prompt or messages required")

        if system:
            msgs = [{"role": "system", "content": system}] + msgs

        return msgs

    def _messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert message list to single prompt string (for Gemini)"""
        parts = []
        for m in messages:
            role = m["role"].upper()
            parts.append(f"{role}: {m['content']}")
        return "\n\n".join(parts)

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate: 4 chars ≈ 1 token"""
        return len(text) // 4

    @property
    def status(self) -> Dict[str, bool]:
        return {
            "groq": self.groq.available,
            "openrouter": self.openrouter.available,
            "gemini": self.gemini.available,
        }


# ─────────────────────────────────────────
# Singleton
# ─────────────────────────────────────────

_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create singleton LLM client"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
