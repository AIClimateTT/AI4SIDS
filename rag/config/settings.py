"""
Configuration settings for AI4SIDS
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_optional=True,
        extra="allow",
        env_ignore_empty=False,
    )

    # LLM Configuration
    NVIDIA_API_KEY: Optional[str] = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = ""
    LLM_TEMPERATURE: float = 0.1

    # External OpenAI-compatible LLM (e.g. a colleague's OpenWebUI instance)
    OPENAI_API_BASE_URL: Optional[str] = ""
    OPENAI_API_KEY: Optional[str] = ""

    # Computed after init — which LLM backend to use
    # Priority: OPENAI_API_BASE_URL > NVIDIA_API_KEY > Ollama (fallback)
    USE_OLLAMA: bool = True
    LLM_BACKEND: str = "ollama"

    # LangSmith (Optional Monitoring)
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = ""
    LANGCHAIN_PROJECT: str = "ai4sids"

    # Data Backend API URL (the separate backend service that serves live/simulated data)
    DATA_BACKEND_URL: str = "http://localhost:8080"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @model_validator(mode="after")
    def _resolve_computed_fields(self) -> "Settings":
        """Derive LLM_BACKEND and LLM_MODEL from the actual env values.

        Priority order:
        1. OPENAI_API_BASE_URL set  → use external OpenAI-compatible endpoint
        2. NVIDIA_API_KEY set       → use NVIDIA NIM
        3. Neither set              → use local Ollama
        """
        if self.OPENAI_API_BASE_URL:
            self.LLM_BACKEND = "openai"
            self.USE_OLLAMA = False
            if not self.LLM_MODEL:
                self.LLM_MODEL = "ai4sids-climate-assistant"
        elif self.NVIDIA_API_KEY:
            self.LLM_BACKEND = "nvidia"
            self.USE_OLLAMA = False
            if not self.LLM_MODEL:
                self.LLM_MODEL = "meta/llama-3.1-70b-instruct"
        else:
            self.LLM_BACKEND = "ollama"
            self.USE_OLLAMA = True
            if not self.LLM_MODEL:
                self.LLM_MODEL = "llama3.2"
        return self

    # --- Paths (not from env, derived at runtime) ---

    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def DATA_DIR(self) -> Path:
        d = self.BASE_DIR / "data"
        d.mkdir(exist_ok=True)
        return d

    @property
    def LOGS_DIR(self) -> Path:
        d = self.BASE_DIR / "logs"
        d.mkdir(exist_ok=True)
        return d

    def get_llm(self):
        """Get configured LLM instance based on LLM_BACKEND."""
        if self.LLM_BACKEND == "openai":
            from langchain_openai import ChatOpenAI
            print(f"Using OpenAI-compatible endpoint: {self.OPENAI_API_BASE_URL}")
            print(f"Model: {self.LLM_MODEL}")
            return ChatOpenAI(
                model=self.LLM_MODEL,
                base_url=self.OPENAI_API_BASE_URL,
                api_key=self.OPENAI_API_KEY or "not-needed",
                temperature=self.LLM_TEMPERATURE,
            )
        elif self.LLM_BACKEND == "nvidia":
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
            print(f"Using NVIDIA NIM with model: {self.LLM_MODEL}")
            return ChatNVIDIA(
                model=self.LLM_MODEL,
                api_key=self.NVIDIA_API_KEY,
                temperature=self.LLM_TEMPERATURE,
            )
        else:
            from langchain_ollama import ChatOllama
            print(f"Using Ollama with model: {self.LLM_MODEL}")
            return ChatOllama(
                model=self.LLM_MODEL,
                base_url=self.OLLAMA_BASE_URL,
                temperature=self.LLM_TEMPERATURE,
            )

    def print_config(self):
        """Print the loaded configuration summary."""
        backend_labels = {
            "openai": f"OpenAI-compatible ({self.OPENAI_API_BASE_URL})",
            "nvidia": "NVIDIA NIM (Cloud)",
            "ollama": "Ollama (Local)",
        }
        print(f"""
{'='*60}
AI4SIDS Configuration Loaded
{'='*60}
LLM Backend: {backend_labels.get(self.LLM_BACKEND, self.LLM_BACKEND)}
Model: {self.LLM_MODEL}
Data Backend: {self.DATA_BACKEND_URL}
Data Directory: {self.DATA_DIR}
Logs Directory: {self.LOGS_DIR}
LangSmith Tracing: {'Enabled' if self.LANGCHAIN_TRACING_V2 else 'Disabled'}
{'='*60}
""")


# Singleton instance
settings = Settings()
settings.print_config()
