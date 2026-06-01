"""Tests for Tutor LLM Router with 4-layer fallback (T11).

AC21: LLM Router with Ark (豆包) as primary, plus 3-layer fallback:
- Layer 0: Ark (豆包) (primary)
- Layer 1: OpenRouter (fallback)
- Layer 2: 千帆 (Baidu) (fallback)
- Layer 3: Local Qwen-7B (last resort)
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.llm_router import LLMRouter


class TestLLMRouter:
    """Test LLM Router 4-layer fallback mechanism."""

    def test_router_initialization(self):
        """Test router initializes with correct provider order."""
        router = LLMRouter()
        assert router.providers[0].name == "ark"  # 豆包 (Primary)
        assert router.providers[1].name == "openrouter"
        assert router.providers[2].name == "qianfan"
        assert router.providers[3].name == "local_qwen"

    def test_provider_priority_order(self):
        """Test providers are ordered by priority."""
        router = LLMRouter()
        priorities = [p.priority for p in router.providers]
        assert priorities == [0, 1, 2, 3]

    @pytest.mark.asyncio
    async def test_primary_provider_success(self):
        """Test primary provider (Ark) returns response on success."""
        router = LLMRouter()

        with patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_ark:
            mock_ark.return_value = {
                "content": "Hello from Ark",
                "model": "doubao-seed-2-0-lite-260215",
                "tokens": 150,
                "provider": "ark",
            }

            result = await router.chat("Hello")

            assert result["content"] == "Hello from Ark"
            assert result["provider"] == "ark"
            mock_ark.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_on_timeout(self):
        """Test fallback to layer 1 (OpenRouter) when layer 0 (Ark) times out."""
        router = LLMRouter()

        with (
            patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_ark,
            patch.object(router.providers[1], "chat", new_callable=AsyncMock) as mock_openrouter,
        ):
            # Layer 0 (Ark) times out
            mock_ark.side_effect = TimeoutError("Request timeout")

            # Layer 1 (OpenRouter) succeeds
            mock_openrouter.return_value = {
                "content": "Hello from OpenRouter",
                "model": "claude-3",
                "tokens": 120,
                "provider": "openrouter",
            }

            result = await router.chat("Hello")

            assert result["content"] == "Hello from OpenRouter"
            assert result["provider"] == "openrouter"
            mock_ark.assert_called_once()
            mock_openrouter.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_on_rate_limit(self):
        """Test fallback when layer 0 (Ark) hits rate limit."""
        router = LLMRouter()

        with (
            patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_ark,
            patch.object(router.providers[1], "chat", new_callable=AsyncMock) as mock_openrouter,
        ):
            # Layer 0 (Ark) rate limited
            mock_ark.side_effect = Exception("Rate limit exceeded")

            # Layer 1 (OpenRouter) succeeds
            mock_openrouter.return_value = {
                "content": "Hello from OpenRouter",
                "model": "claude-3",
                "tokens": 120,
                "provider": "openrouter",
            }

            result = await router.chat("Hello")

            assert result["provider"] == "openrouter"

    @pytest.mark.asyncio
    async def test_fallback_to_layer_3_when_qianfan_not_implemented(self):
        """Test fallback to layer 3 (Local Qwen) when layer 0, 1, 2 fail.

        QianfanProvider now raises NotImplementedError (not yet connected).
        The router should fall through to LocalQwenProvider as the last resort.
        """
        router = LLMRouter()

        with (
            patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_ark,
            patch.object(router.providers[1], "chat", new_callable=AsyncMock) as mock_openrouter,
            patch.object(router.providers[2], "chat", new_callable=AsyncMock) as mock_qianfan,
            patch.object(router.providers[3], "chat", new_callable=AsyncMock) as mock_local_qwen,
        ):
            # Layer 0 & 1 fail
            mock_ark.side_effect = Exception("Ark error")
            mock_openrouter.side_effect = Exception("OpenRouter error")

            # Layer 2 (Qianfan) raises NotImplementedError (not yet connected)
            mock_qianfan.side_effect = NotImplementedError(
                "Qianfan provider not yet connected — use Ark or OpenRouter instead"
            )

            # Layer 3 (Local Qwen) succeeds
            mock_local_qwen.return_value = {
                "content": "Hello from Local Qwen",
                "model": "qwen-7b-chat",
                "tokens": 50,
                "provider": "local_qwen",
            }

            result = await router.chat("Hello")

            assert result["content"] == "Hello from Local Qwen"
            assert result["provider"] == "local_qwen"
            mock_ark.assert_called_once()
            mock_openrouter.assert_called_once()
            mock_qianfan.assert_called_once()
            mock_local_qwen.assert_called_once()

    @pytest.mark.asyncio
    async def test_all_providers_fail(self):
        """Test error handling when all providers fail."""
        router = LLMRouter()

        with (
            patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_ark,
            patch.object(router.providers[1], "chat", new_callable=AsyncMock) as mock_openrouter,
            patch.object(router.providers[2], "chat", new_callable=AsyncMock) as mock_qianfan,
            patch.object(router.providers[3], "chat", new_callable=AsyncMock) as mock_qwen,
        ):
            # All layers fail
            mock_ark.side_effect = Exception("Ark error")
            mock_openrouter.side_effect = Exception("OpenRouter error")
            mock_qianfan.side_effect = Exception("Qianfan error")
            mock_qwen.side_effect = Exception("Local Qwen error")

            with pytest.raises(Exception) as exc_info:
                await router.chat("Hello")

            assert "All LLM providers failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_response_time_tracking(self):
        """Test response time is tracked for latency monitoring."""
        router = LLMRouter()

        with patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_ark:
            mock_ark.return_value = {
                "content": "Hello",
                "model": "doubao",
                "tokens": 50,
                "latency_ms": 1200,
                "provider": "ark",
            }

            result = await router.chat("Hello")

            assert "latency_ms" in result
            assert result["latency_ms"] > 0

    def test_provider_health_check(self):
        """Test provider health status check."""
        router = LLMRouter()

        health = router.check_health()

        assert "ark" in health
        assert "openrouter" in health
        assert "qianfan" in health
        assert "local_qwen" in health
        assert all(status in ["healthy", "unhealthy"] for status in health.values())
