from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    DATABASE_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    # POSTGRES_HOST: str
    POSTGRES_HOSTNAME: str

    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str

    CLIENT_ORIGIN: str

    VERIFICATION_SECRET: str

    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: EmailStr

    SECRET_WORD: str
    EXTERNAL_API_URL: str
    M3U8_DOMAIN: str
    SERVER_RTMP_LINK: str
    SECRET_KEY_STREAM: str
    SRS_TOKEN: str
    SRS_API: str

    class Config:
        env_file = './.env'


settings = Settings()
