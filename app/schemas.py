from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_alias: str | None = None
    expires_at: datetime | None = None
    redirect_status_code: int = 302

    @field_validator("custom_alias")
    @classmethod
    def validate_custom_alias(cls, value: str | None):
        if value is None:
            return value
        value = value.strip()
        if not value:
            return None
        if len(value) > 16:
            raise ValueError("custom_alias must be 16 characters or fewer")
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if any(ch not in allowed for ch in value):
            raise ValueError("custom_alias can only contain letters, numbers, '-' and '_'")
        return value

    @field_validator("redirect_status_code")
    @classmethod
    def validate_redirect_status_code(cls, value: int):
        if value not in (301, 302, 307, 308):
            raise ValueError("redirect_status_code must be one of 301, 302, 307, 308")
        return value


class LinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    short_code: str
    short_url: str
    long_url: str
    created_at: datetime
    expires_at: datetime | None = None
    is_custom: bool
    redirect_status_code: int


class LinkStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    long_url: str
    created_at: datetime
    expires_at: datetime | None = None
    click_count: int
    redirect_status_code: int
