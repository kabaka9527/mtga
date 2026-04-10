from __future__ import annotations

from functools import lru_cache
from typing import Any, Literal

from pydantic import BaseModel
from pytauri import Commands

from modules.runtime.operation_result import OperationResult
from modules.runtime.resource_manager import ResourceManager
from modules.services.config_service import (
    ConfigStore,
    is_valid_hosts_domain,
    normalize_hosts_domain,
)
from modules.services.hosts_service import (
    backup_hosts_file_result,
    modify_hosts_file_result,
    open_hosts_file_result,
    remove_hosts_entry_result,
    restore_hosts_file_result,
)

from .common import build_result_payload, collect_logs, register_command


class HostsModifyPayload(BaseModel):
    mode: Literal["add", "backup", "restore", "remove"]
    domain: str | None = None
    ip: list[str] | str | None = None


@lru_cache(maxsize=1)
def _get_config_store() -> ConfigStore:
    resource_manager = ResourceManager()
    return ConfigStore(resource_manager.get_user_config_file())


def _resolve_hosts_domain(
    *,
    domain: str | None,
    log_func: Any,
) -> tuple[str | None, OperationResult | None]:
    raw_domain: Any = _get_config_store().load_hosts_domain() if domain is None else domain
    normalized_domain = normalize_hosts_domain(raw_domain)
    if not is_valid_hosts_domain(normalized_domain):
        return (
            None,
            OperationResult.failure(
                "hosts 域名格式无效，请输入合法域名（示例：api.openai.com）"
            ),
        )
    log_func(f"hosts 目标域名: {normalized_domain}")
    return normalized_domain, None


def register_hosts_commands(commands: Commands) -> None:
    @register_command(commands)
    async def hosts_modify(body: HostsModifyPayload) -> dict[str, Any]:
        logs, log_func = collect_logs()
        mode = body.mode
        ip = body.ip

        domain_value: str | None = None
        if mode in {"add", "remove"}:
            domain_value, error_result = _resolve_hosts_domain(
                domain=body.domain,
                log_func=log_func,
            )
            if error_result is not None:
                return build_result_payload(error_result, logs, "hosts 操作失败")

        if mode == "add":
            result = modify_hosts_file_result(
                domain=domain_value or "",
                action="add",
                ip=ip,
                log_func=log_func,
            )
            return build_result_payload(result, logs, "hosts 修改完成")
        if mode == "remove":
            result = remove_hosts_entry_result(
                domain=domain_value or "",
                ip=ip,
                log_func=log_func,
            )
            return build_result_payload(result, logs, "hosts 删除完成")
        if mode == "backup":
            result = backup_hosts_file_result(log_func=log_func)
            return build_result_payload(result, logs, "hosts 备份完成")
        if mode == "restore":
            result = restore_hosts_file_result(log_func=log_func)
            return build_result_payload(result, logs, "hosts 还原完成")

        return {
            "ok": False,
            "message": f"不支持的 hosts 操作: {mode}",
            "code": None,
            "details": {},
            "logs": logs,
        }

    @register_command(commands)
    async def hosts_open() -> dict[str, Any]:
        logs, log_func = collect_logs()
        result = open_hosts_file_result(log_func=log_func)
        return build_result_payload(result, logs, "hosts 打开完成")

    _ = (hosts_modify, hosts_open)
