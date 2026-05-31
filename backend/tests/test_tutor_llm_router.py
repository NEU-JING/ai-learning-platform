"""Tests for Tutor LLM Router with 3-layer fallback (T11).

AC21: LLM Router 三级降级
- Layer 1: OpenRouter (primary)
- Layer 2: 千帆 (Baidu) (fallback on timeout/rate limit)
- Layer 3: Local Qwen-7B (fallback on failure)
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.llm_router import LLMRouter


class TestLLMRouter:
    """Test LLM Router 3-layer fallback mechanism."""

    def test_router_initialization(self):
        """Test router initializes with correct provider order."""
        router = LLMRouter()
        assert router.providers[0].name == "openrouter"
        assert router.providers[1].name == "qianfan"
        assert router.providers[2].name == "local_qwen"

    def test_provider_priority_order(self):
        """Test providers are ordered by priority."""
        router = LLMRouter()
        priorities = [p.priority for p in router.providers]
        assert priorities == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_primary_provider_success(self):
        """Test primary provider (OpenRouter) returns response on success."""
        router = LLMRouter()

        with patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_openrouter:
            mock_openrouter.return_value = {
                "content": "Hello from OpenRouter",
                "model": "anthropic/claude-3-sonnet",
                "tokens": 150,
            }

            result = await router.chat("Hello")

            assert result["content"] == "Hello from OpenRouter"
            assert result["provider"] == "openrouter"
            mock_openrouter.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_on_timeout(self):
        """Test fallback to layer 2 (千帆) when layer 1 times out."""
        router = LLMRouter()

        with (
            patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_openrouter,
            patch.object(router.providers[1], "chat", new_callable=AsyncMock) as mock_qianfan,
        ):

            # Layer 1 times out
            mock_openrouter.side_effect = TimeoutError("Request timeout")

            # Layer 2 succeeds
            mock_qianfan.return_value = {
                "content": "Hello from Qianfan",
                "model": "ERNIE-4.0",
                "tokens": 120,
            }

            result = await router.chat("Hello")

            assert result["content"] == "Hello from Qianfan"
            assert result["provider"] == "qianfan"
            mock_openrouter.assert_called_once()
            mock_qianfan.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_on_rate_limit(self):
        """Test fallback when layer 1 hits rate limit."""
        router = LLMRouter()

        with (
            patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_openrouter,
            patch.object(router.providers[1], "chat", new_callable=AsyncMock) as mock_qianfan,
        ):

            # Layer 1 rate limited
            mock_openrouter.side_effect = Exception("Rate limit exceeded")  # Use generic Exception

            # Layer 2 succeeds
            mock_qianfan.return_value = {
                "content": "Hello from Qianfan",
                "model": "ERNIE-4.0",
                "tokens": 120,
            }

            result = await router.chat("Hello")

            assert result["provider"] == "qianfan"

    @pytest.mark.asyncio
    async def test_fallback_to_layer_3_on_failure(self):
        """Test fallback to layer 3 (Local Qwen) when both layer 1 & 2 fail."""
        router = LLMRouter()

        with (
            patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_openrouter,
            patch.object(router.providers[1], "chat", new_callable=AsyncMock) as mock_qianfan,
            patch.object(router.providers[2], "chat", new_callable=AsyncMock) as mock_qwen,
        ):

            # Layer 1 & 2 fail
            mock_openrouter.side_effect = Exception("OpenRouter error")
            mock_qianfan.side_effect = Exception("Qianfan error")

            # Layer 3 succeeds
            mock_qwen.return_value = {
                "content": "Hello from Local Qwen",
                "model": "qwen-7b-chat",
                "tokens": 100,
            }

            result = await router.chat("Hello")

            assert result["content"] == "Hello from Local Qwen"
            assert result["provider"] == "local_qwen"
            mock_openrouter.assert_called_once()
            mock_qianfan.assert_called_once()
            mock_qwen.assert_called_once()

    @pytest.mark.asyncio
    async def test_all_providers_fail(self):
        """Test error handling when all providers fail."""
        router = LLMRouter()

        with (
            patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_openrouter,
            patch.object(router.providers[1], "chat", new_callable=AsyncMock) as mock_qianfan,
            patch.object(router.providers[2], "chat", new_callable=AsyncMock) as mock_qwen,
        ):

            # All layers fail
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

        with patch.object(router.providers[0], "chat", new_callable=AsyncMock) as mock_openrouter:
            mock_openrouter.return_value = {
                "content": "Hello",
                "model": "claude-3",
                "tokens": 50,
                "latency_ms": 1200,
            }

            result = await router.chat("Hello")

            assert "latency_ms" in result
            assert result["latency_ms"] > 0

    def test_provider_health_check(self):
        """Test provider health status check."""
        router = LLMRouter()

        health = router.check_health()

        assert "openrouter" in health
        assert "qianfan" in health
        assert "local_qwen" in health
        assert all(status in ["healthy", "unhealthy"] for status in health.values())
