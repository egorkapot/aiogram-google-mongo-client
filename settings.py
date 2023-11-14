from pydantic import Field, SecretStr, field_validator, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from exceptions.exceptions import MissingEnvironmentVariableException
from typing import Any, Union
from google_access_share_bot.utils.utils import singleton
from enum import Enum


class Tables(Enum):
    """
    Class to store all tables to retrieve their info later.
    To access the value of table you should access its value like Tables[TABLE_NAME]
    """
    WEB_CONTENT = "web_content"
    WEB_AI_CONTENT = "web_ai_content"
    SEO_CONTENT = "seo_content"
    BACKUP = "backup"


@singleton
class Settings(BaseSettings):
    """
    Class to store all settings for this app. All property must be
    hashable, so that the settings class itself stay hashable and can
    be easily cached

    To retrieve secret values use get_secret_value() function
    """
    tier: str = Field("development", env="TIER")
    production_bot_token: SecretStr = Field(..., env="PRODUCTION_BOT_TOKEN")
    development_bot_token: SecretStr = Field(..., env="DEVELOPMENT_BOT_TOKEN")
    author_chat_id: str = Field(..., env="AUTHOR_CHAT_ID")
    guide_link: str = Field(None, env="GUIDE_LINK")
    web_content_table_link: str = Field(None, env="WEB_CONTENT_TABLE_LINK")
    web_ai_content_table_link: str = Field(None, env="WEB_AI_CONTENT_TABLE_LINK")
    seo_content_table_link: str = Field(None, env="SEO_CONTENT_TABLE_LINK")
    backup_table_link: str = Field(None, env="BACKUP_TABLE_LINK")
    mongo_host: str = Field("localhost", env="MONGO_HOST")
    mongo_port: int = Field(27017, env="MONGO_PORT")
    validation_schema_path: str = Field(None, env="VALIDATION_SCHEMA_PATH")
    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        env_file_encoding="utf-8",
        frozen=True
    )

    def get_bot_token(self):
        if self.tier == "production":
            return self.production_bot_token
        elif self.tier == "development":
            return self.development_bot_token
        else:
            raise MissingEnvironmentVariableException(
                f"Invalid environment type {self.env_type}"
            )

    @staticmethod
    def get_table_link(table: str) -> str:
        """
        Returns link for specified table

        :param table: Table name to receive link
        :return:
        """
        table_links = {
            Tables.WEB_CONTENT: Settings().web_content_table_link,
            Tables.WEB_AI_CONTENT: Settings().web_ai_content_table_link,
            Tables.SEO_CONTENT: Settings().seo_content_table_link,
            Tables.BACKUP: Settings().backup_table_link
        }
        table_type = Tables[table.upper()]
        return table_links.get(table_type)


settings = Settings()
