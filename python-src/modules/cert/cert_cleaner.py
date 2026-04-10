"""
证书清理模块
提供跨平台的 CA 证书删除能力，避免在 GUI 中直接嵌入平台脚本。
"""

from __future__ import annotations

import os
from collections.abc import Callable

from modules.cert.ca_store import clear_ca_cert_store
from modules.runtime.operation_result import OperationResult
from modules.runtime.resource_manager import ResourceManager

type LogFunc = Callable[[str], None]


def clear_ca_cert_result(ca_common_name: str, log_func: LogFunc = print) -> OperationResult:
    """返回清理结果。"""
    return clear_ca_cert_store(ca_common_name, log_func=log_func)


def clear_ca_cert(ca_common_name: str, log_func: LogFunc = print) -> bool:
    """根据平台清除系统信任存储中的 CA 证书。"""
    return clear_ca_cert_result(ca_common_name, log_func=log_func).ok


def remove_server_cert_files_result(
    *,
    domain: str,
    remove_templates: bool = False,
    log_func: LogFunc = print,
) -> OperationResult:
    """删除指定域名的服务器证书相关文件。"""
    normalized_domain = domain.strip().lower()
    if not normalized_domain:
        return OperationResult.failure("服务器证书域名为空")

    resource_manager = ResourceManager()
    candidate_paths = [
        resource_manager.get_cert_file(normalized_domain),
        resource_manager.get_key_file(normalized_domain),
        os.path.join(resource_manager.ca_path, f"{normalized_domain}.csr"),
    ]
    if remove_templates:
        candidate_paths.extend(
            [
                resource_manager.get_config_file(f"{normalized_domain}.cnf"),
                resource_manager.get_config_file(f"{normalized_domain}.subj"),
            ]
        )

    removed_files: list[str] = []
    missing_files: list[str] = []
    failed_files: list[str] = []
    for path in candidate_paths:
        if not os.path.exists(path):
            missing_files.append(path)
            continue
        try:
            os.remove(path)
            removed_files.append(path)
        except Exception as exc:  # noqa: BLE001
            failed_files.append(f"{path}: {exc}")

    if removed_files:
        log_func(f"已清理域名证书文件 ({normalized_domain}): {len(removed_files)} 个")
    if failed_files:
        for failure in failed_files:
            log_func(f"删除证书文件失败: {failure}")
        return OperationResult.failure(
            "删除服务器证书文件失败",
            removed_files=removed_files,
            missing_files=missing_files,
            failed_files=failed_files,
        )
    return OperationResult.success(
        removed_files=removed_files,
        missing_files=missing_files,
    )


__all__ = [
    "clear_ca_cert",
    "clear_ca_cert_result",
    "remove_server_cert_files_result",
]
