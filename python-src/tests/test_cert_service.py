from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from modules.services import cert_service


class CertServiceTests(unittest.TestCase):
    def test_generate_server_certificate_result_success(self) -> None:
        resource_manager = MagicMock()
        logs: list[str] = []

        with (
            patch(
                "modules.services.cert_service.ResourceManager",
                return_value=resource_manager,
            ),
            patch(
                "modules.services.cert_service.create_default_config_files",
                return_value=True,
            ) as create_defaults,
            patch(
                "modules.services.cert_service.ensure_server_domain_config_files",
                return_value=True,
            ) as ensure_domain_templates,
            patch(
                "modules.services.cert_service.generate_server_cert",
                return_value=True,
            ) as generate_server_cert,
        ):
            result = cert_service.generate_server_certificate_result(
                domain="custom.example.com",
                log_func=logs.append,
            )

        self.assertTrue(result.ok)
        create_defaults.assert_called_once()
        ensure_domain_templates.assert_called_once_with(
            resource_manager,
            "custom.example.com",
            log_func=logs.append,
        )
        generate_server_cert.assert_called_once_with(
            resource_manager,
            "custom.example.com",
            log_func=logs.append,
        )

    def test_remove_server_certificate_result_delegates_to_cleaner(self) -> None:
        logs: list[str] = []
        with patch(
            "modules.services.cert_service.remove_server_cert_files_result",
            return_value=cert_service.OperationResult.success(),
        ) as remove_files:
            result = cert_service.remove_server_certificate_result(
                domain="custom.example.com",
                remove_templates=True,
                log_func=logs.append,
            )

        self.assertTrue(result.ok)
        remove_files.assert_called_once_with(
            domain="custom.example.com",
            remove_templates=True,
            log_func=logs.append,
        )


if __name__ == "__main__":
    unittest.main()
