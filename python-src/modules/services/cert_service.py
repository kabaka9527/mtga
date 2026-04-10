from __future__ import annotations

from collections.abc import Callable

from modules.cert.cert_checker import check_existing_ca_cert, has_existing_ca_cert
from modules.cert.cert_cleaner import (
    clear_ca_cert,
    clear_ca_cert_result,
    remove_server_cert_files_result,
)
from modules.cert.cert_generator import (
    create_default_config_files,
    ensure_server_domain_config_files,
    generate_certificates,
    generate_server_cert,
)
from modules.cert.cert_installer import install_ca_cert, install_ca_cert_result
from modules.runtime.operation_result import OperationResult
from modules.runtime.resource_manager import ResourceManager

type LogFunc = Callable[[str], None]


def generate_certificates_result(
    *,
    log_func: LogFunc,
    ca_common_name: str,
    domain: str = "api.openai.com",
) -> OperationResult:
    if generate_certificates(
        domain=domain,
        log_func=log_func,
        ca_common_name=ca_common_name,
    ):
        return OperationResult.success()
    return OperationResult.failure("生成证书失败")


def generate_server_certificate_result(
    *,
    domain: str,
    log_func: LogFunc,
) -> OperationResult:
    resource_manager = ResourceManager()
    normalized_domain = domain.strip().lower()
    if not normalized_domain:
        return OperationResult.failure("服务器证书域名为空")

    if not create_default_config_files(resource_manager, log_func=lambda _message: None):
        return OperationResult.failure("初始化证书模板失败")
    if not ensure_server_domain_config_files(
        resource_manager,
        normalized_domain,
        log_func=log_func,
    ):
        return OperationResult.failure("生成域名证书模板失败")
    if generate_server_cert(resource_manager, normalized_domain, log_func=log_func):
        return OperationResult.success(domain=normalized_domain)
    return OperationResult.failure("生成服务器证书失败")


def remove_server_certificate_result(
    *,
    domain: str,
    remove_templates: bool = False,
    log_func: LogFunc = print,
) -> OperationResult:
    return remove_server_cert_files_result(
        domain=domain,
        remove_templates=remove_templates,
        log_func=log_func,
    )


def has_existing_ca_cert_result(
    *,
    log_func: LogFunc,
    ca_common_name: str,
) -> OperationResult:
    return check_existing_ca_cert(ca_common_name, log_func=log_func)

__all__ = [
    "check_existing_ca_cert",
    "clear_ca_cert",
    "clear_ca_cert_result",
    "generate_certificates",
    "generate_certificates_result",
    "generate_server_certificate_result",
    "has_existing_ca_cert",
    "has_existing_ca_cert_result",
    "install_ca_cert",
    "install_ca_cert_result",
    "remove_server_certificate_result",
]
