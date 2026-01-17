from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    GROQ_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
