from typing import Annotated

from fastapi import Depends

from src.app.core.config import Settings, settings


def get_settings() -> Settings:
    return settings


SettingsDep = Annotated[Settings, Depends(get_settings)]
