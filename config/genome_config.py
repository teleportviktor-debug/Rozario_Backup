"""
Configuration & Environment Settings for Genome Architecture.
Zero Trust, Google Workspace API, Gemini API, n8n Integration.
"""
import os
from pydantic import BaseModel, Field

class GenomeConfig(BaseModel):
    # Security & Tokens
    N8N_WEBHOOK_TOKEN: str = Field(default_factory=lambda: os.getenv("N8N_WEBHOOK_TOKEN", "ntn_genome_secret_token_default"))
    GEMINI_API_KEY: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    
    # Model Configurations
    PRIMARY_MODEL: str = Field(default="gemini-2.5-flash")
    FALLBACK_MODEL: str = Field(default="gemini-2.0-flash-lite")
    RACING_TIMEOUT_SECONDS: float = Field(default=8.0)
    
    # Visual Theme Palette
    COLOR_OBSIDIAN: str = "#0a0a0c"
    COLOR_NEON_CYAN: str = "#00f0ff"
    COLOR_KLIMT_GOLD: str = "#d4af37"
    COLOR_STEEL_MUTED: str = "#8a8f98"
    COLOR_DARK_SURFACE: str = "#121216"

settings = GenomeConfig()
