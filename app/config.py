from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-5-mini"

    meta_access_token: str
    meta_phone_number_id: str
    meta_verify_token: str

    owner_phone_number: str
    database_url: str = "sqlite:///./alexos.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
