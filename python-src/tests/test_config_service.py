from __future__ import annotations

import unittest

from modules.services.config_service import (
    DEFAULT_HOSTS_DOMAIN,
    LEGACY_GROUP_MAPPED_MODEL_ID_WARNING,
    _collect_config_warnings,
    _normalize_config_group,
    is_valid_hosts_domain,
    normalize_hosts_domain,
)


class ConfigGroupNormalizationTests(unittest.TestCase):
    def test_normalize_config_group_strips_legacy_fields(self) -> None:
        normalized = _normalize_config_group(
            {
                "name": "legacy",
                "provider": "openai_chat_completion",
                "api_url": "https://api.openai.com",
                "model_id": "gpt-4o-mini",
                "api_key": "test-key",
                "mapped_model_id": "legacy-mapped",
                "target_model_id": "legacy-target",
            }
        )

        self.assertIsNotNone(normalized)
        assert normalized is not None
        self.assertNotIn("mapped_model_id", normalized)
        self.assertNotIn("target_model_id", normalized)
        self.assertEqual(normalized["model_id"], "gpt-4o-mini")
        self.assertEqual(normalized["provider"], "openai_chat_completion")

    def test_normalize_config_group_keeps_supported_fields(self) -> None:
        normalized = _normalize_config_group(
            {
                "name": "group-1",
                "provider": "gemini",
                "api_url": "https://provider.example.com",
                "model_id": "gemini-2.5-pro",
                "api_key": "test-key",
                "middle_route": "/v1beta",
                "model_discovery_strategy": "gemini_native_bearer",
                "prompt_cache_enabled": False,
            }
        )

        self.assertEqual(
            normalized,
            {
                "name": "group-1",
                "provider": "gemini",
                "api_url": "https://provider.example.com",
                "model_id": "gemini-2.5-pro",
                "api_key": "test-key",
                "middle_route": "/v1beta",
                "model_discovery_strategy": "gemini_native_bearer",
                "prompt_cache_enabled": False,
            },
        )

    def test_normalize_config_group_defaults_prompt_cache_enabled_to_false(self) -> None:
        normalized = _normalize_config_group(
            {
                "provider": "openai_chat_completion",
                "api_url": "https://api.openai.com",
                "model_id": "gpt-4o-mini",
                "api_key": "test-key",
            }
        )

        self.assertIsNotNone(normalized)
        assert normalized is not None
        self.assertFalse(normalized["prompt_cache_enabled"])

    def test_collect_config_warnings_reports_legacy_group_mapped_model_id(self) -> None:
        warnings = _collect_config_warnings(
            {
                "config_groups": [
                    {
                        "provider": "openai_chat_completion",
                        "api_url": "https://api.openai.com",
                        "model_id": "gpt-4o-mini",
                        "mapped_model_id": "legacy-group-model",
                        "api_key": "test-key",
                    }
                ],
                "current_config_index": 0,
            }
        )

        self.assertEqual(warnings, [LEGACY_GROUP_MAPPED_MODEL_ID_WARNING])

    def test_collect_config_warnings_is_empty_for_current_schema(self) -> None:
        warnings = _collect_config_warnings(
            {
                "config_groups": [
                    {
                        "provider": "openai_chat_completion",
                        "api_url": "https://api.openai.com",
                        "model_id": "gpt-4o-mini",
                        "api_key": "test-key",
                    }
                ],
                "mapped_model_id": "gpt-5",
                "current_config_index": 0,
            }
        )

        self.assertEqual(warnings, [])

    def test_normalize_hosts_domain_uses_default_for_empty_value(self) -> None:
        self.assertEqual(normalize_hosts_domain(""), DEFAULT_HOSTS_DOMAIN)

    def test_normalize_hosts_domain_extracts_hostname_from_url(self) -> None:
        self.assertEqual(
            normalize_hosts_domain("https://api.example.com:443/v1/chat/completions"),
            "api.example.com",
        )

    def test_hosts_domain_validation_accepts_standard_domain(self) -> None:
        self.assertTrue(is_valid_hosts_domain("api.openai.com"))

    def test_hosts_domain_validation_rejects_invalid_domain(self) -> None:
        self.assertFalse(is_valid_hosts_domain("api openai com"))


if __name__ == "__main__":
    unittest.main()
