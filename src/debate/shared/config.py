"""Config module."""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""
    pass

@dataclass
class RateLimitConfig:
    requests_per_minute: int
    requests_per_hour: int
    concurrent_max: int
    retry_after_seconds: int
    max_retries: int
    queue_max_depth: int

@dataclass
class LoggingConfig:
    version: str
    log_level: str
    log_dir: str
    max_files: int
    max_lines_per_file: int
    format: str

class ConfigManager:
    def __init__(self, config_dir: str = "config/"):
        self.config_dir = Path(config_dir)
        self._setup_config: dict[str, Any] = {}
        self._rate_limits: dict[str, Any] = {}
        self._logging_config: dict[str, Any] = {}
        self._load_configs()

    def _load_json(self, filename: str) -> dict[str, Any]:
        file_path = self.config_dir / filename
        if not file_path.exists():
            raise ConfigurationError(f"Configuration file {filename} not found in {self.config_dir}")
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Error parsing {filename}: {e}") from e

    def _load_configs(self):
        self._setup_config = self._load_json("setup.json")
        self._rate_limits = self._load_json("rate_limits.json")
        self._logging_config = self._load_json("logging_config.json")

        # Validate versions — log WARNING on mismatch (backwards compatible)
        import logging
        _log = logging.getLogger(__name__)
        if self._setup_config.get("version") != "1.00":
            _log.warning(
                "Version mismatch in setup.json: expected '1.00', "
                "got '%s'. Proceeding with backwards compatibility.",
                self._setup_config.get("version"),
            )
        if self._rate_limits.get("rate_limits", {}).get("version") != "1.00":
            _log.warning(
                "Version mismatch in rate_limits.json: expected '1.00', "
                "got '%s'. Proceeding with backwards compatibility.",
                self._rate_limits.get("rate_limits", {}).get("version"),
            )
        if self._logging_config.get("version") != "1.00":
            _log.warning(
                "Version mismatch in logging_config.json: expected '1.00', "
                "got '%s'. Proceeding with backwards compatibility.",
                self._logging_config.get("version"),
            )

        # Validate required setup keys
        required_setup_keys = ["model", "max_rounds", "timeout_seconds"]
        for key in required_setup_keys:
            if key not in self._setup_config:
                raise ConfigurationError(f"Missing required key '{key}' in setup.json")

    def get(self, key: str, default: Any = None) -> Any:
        return self._setup_config.get(key, default)

    def get_rate_limit_config(self) -> RateLimitConfig:
        try:
            default_svc = self._rate_limits["rate_limits"]["services"]["default"]
            return RateLimitConfig(
                requests_per_minute=default_svc["requests_per_minute"],
                requests_per_hour=default_svc["requests_per_hour"],
                concurrent_max=default_svc["concurrent_max"],
                retry_after_seconds=default_svc["retry_after_seconds"],
                max_retries=default_svc["max_retries"],
                queue_max_depth=default_svc["queue_max_depth"]
            )
        except KeyError as e:
            raise ConfigurationError(f"Missing rate limit configuration key: {e}") from e

    def get_logging_config(self) -> LoggingConfig:
        try:
            return LoggingConfig(
                version=self._logging_config["version"],
                log_level=self._logging_config["log_level"],
                log_dir=self._logging_config["log_dir"],
                max_files=self._logging_config["max_files"],
                max_lines_per_file=self._logging_config["max_lines_per_file"],
                format=self._logging_config["format"]
            )
        except KeyError as e:
            raise ConfigurationError(f"Missing logging configuration key: {e}") from e
