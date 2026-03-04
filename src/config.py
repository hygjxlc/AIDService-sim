"""Application Configuration"""
import os
from dataclasses import dataclass, field
from typing import Optional
import yaml


@dataclass
class AuthConfig:
    api_key: str = "11111111"


@dataclass
class InternalConfig:
    callback_token: str = "aid_internal_callback_token_2024"


@dataclass
class DatabaseConfig:
    path: str = "./data/aid_service.db"
    backup_path: str = "./backups/"


@dataclass
class StorageConfig:
    base_path: str = "./data/aid/"


@dataclass
class AlgorithmConfig:
    base_url: str = "http://localhost:9000"
    timeout_sec: int = 30
    mock_mode: bool = True


@dataclass
class LoggingConfig:
    level: str = "INFO"
    path: str = "./logs/"
    retention_days: int = 30


@dataclass
class AppConfig:
    auth: AuthConfig = field(default_factory=AuthConfig)
    internal: InternalConfig = field(default_factory=InternalConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    algorithm: AlgorithmConfig = field(default_factory=AlgorithmConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


def load_config(config_path: str = "app_config.yaml") -> AppConfig:
    """Load configuration from YAML file"""
    config = AppConfig()
    
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        
        # Parse auth config
        if "auth" in data:
            config.auth = AuthConfig(**data["auth"])
        
        # Parse internal config
        if "internal" in data:
            config.internal = InternalConfig(**data["internal"])
        
        # Parse database config
        if "database" in data:
            config.database = DatabaseConfig(**data["database"])
        
        # Parse storage config
        if "storage" in data:
            config.storage = StorageConfig(**data["storage"])
        
        # Parse algorithm config
        if "algorithm" in data:
            config.algorithm = AlgorithmConfig(**data["algorithm"])
        
        # Parse logging config
        if "logging" in data:
            config.logging = LoggingConfig(**data["logging"])
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(config.database.path) or ".", exist_ok=True)
    os.makedirs(config.database.backup_path, exist_ok=True)
    os.makedirs(config.storage.base_path, exist_ok=True)
    os.makedirs(config.logging.path, exist_ok=True)
    
    return config


# Global settings instance
settings: AppConfig = None


def get_settings() -> AppConfig:
    """Get application settings (lazy load)"""
    global settings
    if settings is None:
        settings = load_config()
    return settings
