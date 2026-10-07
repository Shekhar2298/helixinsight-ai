from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./helix.db"
    s3_endpoint_url: str | None = None
    s3_bucket: str = "helixinsight"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "us-east-1"
    ensembl_base_url: str = "https://rest.ensembl.org"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
