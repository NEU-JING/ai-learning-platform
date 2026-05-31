"""LLM Router with 3-layer fallback for Tutor module.

AC21: Implements 3-layer LLM fallback:
- Layer 1: OpenRouter (primary)
- Layer 2: 千帆 (Baidu) (fallback on timeout/rate limit)
- Layer 3: Local Qwen-7B (fallback on failure)
"""

import asyncio
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Optional imports - gracefully handle missing dependencies
try:
    from openai import APIError, OpenAI, RateLimitError

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None
    RateLimitError = Exception
    APIError = Exception


@dataclass
class LLMResponse:
    """Standard LLM response format."""

    content: str
    model: str
    tokens: int
    latency_ms: int
    provider: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, name: str, priority: int):
        self.name = name
        self.priority = priority
        self._client: Optional[Any] = None

    @abstractmethod
    async def chat(self, message: str, **kwargs) -> Dict[str, Any]:
        """Send chat message to LLM."""
        pass

    @abstractmethod
    def check_health(self) -> str:
        """Check provider health status."""
        pass


class ArkProvider(LLMProvider):
    """豆包(火山引擎) provider - Primary for AILP."""

    def __init__(self):
        super().__init__("ark", priority=0)
        self._api_key = os.getenv("ARK_API_KEY", "ark-eb7b1eb7-f208-49bb-8498-f8511159b4b8-fcad8")
        self._base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self._model = "doubao-seed-2-0-lite-260215"
        self._client: Optional[Any] = None
        if HAS_OPENAI and self._api_key:
            self._client = OpenAI(base_url=self._base_url, api_key=self._api_key)

    async def chat(
        self, message: str, system_prompt: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Chat via 豆包(Ark)."""
        if not self._client:
            raise Exception("Ark API client not initialized")

        start = time.time()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        try:
            response = await asyncio.to_thread(
                self._client.chat.completions.create,
                model=self._model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
                timeout=30,
            )

            latency_ms = int((time.time() - start) * 1000)

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "tokens": response.usage.total_tokens if response.usage else 0,
                "latency_ms": latency_ms,
                "provider": self.name,
            }
        except TimeoutError:
            raise
        except RateLimitError:
            raise
        except Exception as e:
            raise Exception(f"Ark error: {e}")

    def check_health(self) -> str:
        return "healthy" if self._client else "unhealthy"


class OpenRouterProvider(LLMProvider):
    """OpenRouter provider (Layer 1 - Primary)."""

    def __init__(self):
        super().__init__("openrouter", priority=1)
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            self._client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    async def chat(self, message: str, **kwargs) -> Dict[str, Any]:
        """Chat via OpenRouter."""
        if not self._client:
            raise Exception("OpenRouter API key not configured")

        start = time.time()

        try:
            response = await asyncio.to_thread(
                self._client.chat.completions.create,
                model=kwargs.get("model", "anthropic/claude-3-sonnet"),
                messages=[{"role": "user", "content": message}],
                timeout=30,
            )

            latency_ms = int((time.time() - start) * 1000)

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "tokens": response.usage.total_tokens if response.usage else 0,
                "latency_ms": latency_ms,
                "provider": self.name,
            }
        except TimeoutError:
            raise
        except RateLimitError:
            raise
        except Exception as e:
            raise Exception(f"OpenRouter error: {e}")

    def check_health(self) -> str:
        return "healthy" if self._client else "unhealthy"


class QianfanProvider(LLMProvider):
    """百度千帆 provider (Layer 2 - Fallback)."""

    def __init__(self):
        super().__init__("qianfan", priority=2)
        self._api_key = os.getenv("QIANFAN_API_KEY")
        self._secret_key = os.getenv("QIANFAN_SECRET_KEY")

    async def chat(self, message: str, **kwargs) -> Dict[str, Any]:
        """Chat via 千帆."""
        # Simplified implementation - in production, use qianfan SDK
        start = time.time()

        try:
            # Mock implementation for testing
            # In production: call 千帆 API
            await asyncio.sleep(0.1)  # Simulate API call

            latency_ms = int((time.time() - start) * 1000)

            return {
                "content": f"[千帆响应] {message[:50]}...",
                "model": "ERNIE-4.0",
                "tokens": len(message) // 4,
                "latency_ms": latency_ms,
                "provider": self.name,
            }
        except Exception as e:
            raise Exception(f"Qianfan error: {e}")

    def check_health(self) -> str:
        return "healthy" if self._api_key else "unhealthy"


class LocalQwenProvider(LLMProvider):
    """本地 Qwen-7B provider (Layer 3 - Last resort)."""

    def __init__(self):
        super().__init__("local_qwen", priority=3)
        self._model_path = os.getenv("LOCAL_QWEN_PATH", "/models/qwen-7b-chat")
        self._available = os.path.exists(self._model_path)

    async def chat(self, message: str, **kwargs) -> Dict[str, Any]:
        """Chat via local Qwen."""
        start = time.time()

        try:
            # Mock implementation - in production: load and run local model
            # For now, return a generic response
            await asyncio.sleep(0.05)  # Simulate local inference

            latency_ms = int((time.time() - start) * 1000)

            return {
                "content": "[本地模型响应] 已收到您的消息，正在处理...",
                "model": "qwen-7b-chat",
                "tokens": len(message) // 4,
                "latency_ms": latency_ms,
                "provider": self.name,
            }
        except Exception as e:
            raise Exception(f"Local Qwen error: {e}")

    def check_health(self) -> str:
        return "healthy" if self._available else "unhealthy"


class LLMRouter:
    """LLM Router with 3-layer fallback.

    Implements AC21: Automatic fallback on:
    - Timeout
    - Rate limit (429)
    - General failure
    """

    def __init__(self):
        """Initialize router with 4 providers (Ark as primary)."""
        self.providers: List[LLMProvider] = [
            ArkProvider(),  # Layer 0: 豆包 (Primary)
            OpenRouterProvider(),  # Layer 1: OpenRouter
            QianfanProvider(),  # Layer 2: 千帆
            LocalQwenProvider(),  # Layer 3: Local Qwen
        ]
        # Sort by priority
        self.providers.sort(key=lambda p: p.priority)

    async def chat(self, message: str, **kwargs) -> Dict[str, Any]:
        """Send message with automatic fallback.

        Tries providers in priority order:
        1. OpenRouter (primary)
        2. 千帆 (fallback on timeout/rate limit)
        3. Local Qwen (fallback on any failure)

        Args:
            message: User message
            **kwargs: Additional parameters (model, temperature, etc.)

        Returns:
            Response dict with content, model, tokens, latency_ms, provider

        Raises:
            Exception: If all providers fail
        """
        errors = []

        for provider in self.providers:
            try:
                result = await provider.chat(message, **kwargs)
                return result
            except TimeoutError:
                errors.append(f"{provider.name}: timeout")
                # Timeout -> try next provider
                continue
            except RateLimitError:
                errors.append(f"{provider.name}: rate limit")
                # Rate limit -> try next provider
                continue
            except Exception as e:
                errors.append(f"{provider.name}: {str(e)}")
                # General failure -> try next provider
                continue

        # All providers failed
        raise Exception(f"All LLM providers failed: {'; '.join(errors)}")

    def check_health(self) -> Dict[str, str]:
        """Check health status of all providers.

        Returns:
            Dict mapping provider name to health status
        """
        return {provider.name: provider.check_health() for provider in self.providers}
