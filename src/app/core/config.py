from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_parse_none_str="None",
        env_ignore_empty=False,  # Changed to False to catch empty values
    )

    app_name: str = "tro-backend"
    app_version: str = "0.1.0"
    host: str = "0.0.0.0"

    debug: bool = Field(alias="DEBUG")
    environment: Literal["development", "qa", "production"] = Field(alias="ENVIRONMENT")
    port: int = Field(alias="PORT")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_environments: list[str] = ["development", "qa", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}, got '{v}'")
        return v

    @property
    def cors_origins(self) -> list[str]:
        return ["*"]

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


# Settings will read from .env file and environment variables
# Type checker shows error but Pydantic Settings handles this at runtime
settings = Settings()  # type: ignore[call-arg]
