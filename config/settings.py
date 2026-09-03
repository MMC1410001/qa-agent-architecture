"""Central configuration management using Pydantic Settings."""

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    url: str = Field(
        default="postgresql://localhost:5432/qaos_db",  # credentials come from DATABASE_URL
        alias="DATABASE_URL",
    )
    echo: bool = Field(default=False, alias="DATABASE_ECHO")
    pool_size: int = Field(default=20, alias="DATABASE_POOL_SIZE")
    pool_recycle: int = Field(default=3600, alias="DATABASE_POOL_RECYCLE")
    max_overflow: int = Field(default=10, alias="DATABASE_MAX_OVERFLOW")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class RedisSettings(BaseSettings):
    """Redis configuration."""

    url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    pool_size: int = Field(default=10, alias="REDIS_POOL_SIZE")
    pool_timeout: int = Field(default=5, alias="REDIS_POOL_TIMEOUT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class LLMSettings(BaseSettings):
    """LLM provider configuration."""

    provider: str = Field(default="claude", alias="LLM_PROVIDER")
    model: str = Field(default="claude-sonnet-5", alias="LLM_MODEL")
    api_key: Optional[str] = Field(default=None, alias="LLM_API_KEY")
    temperature: float = Field(default=0.7, alias="LLM_TEMPERATURE")
    max_tokens: int = Field(default=4096, alias="LLM_MAX_TOKENS")
    timeout: int = Field(default=60, alias="LLM_TIMEOUT")

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate LLM provider."""
        valid_providers = ["claude", "openai", "local"]
        if v not in valid_providers:
            raise ValueError(f"Invalid LLM provider. Must be one of {valid_providers}")
        return v.lower()

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class AgentSettings(BaseSettings):
    """Agent configuration."""

    timeout: int = Field(default=300, alias="AGENT_TIMEOUT")
    retry_attempts: int = Field(default=3, alias="AGENT_RETRY_ATTEMPTS")
    retry_delay: int = Field(default=5, alias="AGENT_RETRY_DELAY")
    parallel_execution: bool = Field(default=True, alias="AGENT_PARALLEL_EXECUTION")
    max_concurrent: int = Field(default=5, alias="MAX_CONCURRENT_AGENTS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class TestExecutionSettings(BaseSettings):
    """Test execution configuration."""

    timeout: int = Field(default=600, alias="TEST_EXECUTION_TIMEOUT")
    browser_type: str = Field(default="chromium", alias="TEST_BROWSER_TYPE")
    headless: bool = Field(default=True, alias="TEST_HEADLESS")
    slow_mo: int = Field(default=0, alias="TEST_SLOW_MO")
    screenshot_on_failure: bool = Field(default=True, alias="TEST_SCREENSHOT_ON_FAILURE")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class JiraSettings(BaseSettings):
    """JIRA integration configuration."""

    url: Optional[str] = Field(default=None, alias="JIRA_URL")
    username: Optional[str] = Field(default=None, alias="JIRA_USERNAME")
    api_token: Optional[str] = Field(default=None, alias="JIRA_API_TOKEN")
    enabled: bool = Field(default=False)

    @field_validator("enabled", mode="before")
    @classmethod
    def validate_enabled(cls, v, info):
        """Validate JIRA is enabled only if credentials are provided."""
        if v is None:
            # Check if all required fields have values
            data = info.data
            return bool(data.get("url") and data.get("username") and data.get("api_token"))
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GitHubSettings(BaseSettings):
    """GitHub integration configuration."""

    token: Optional[str] = Field(default=None, alias="GITHUB_TOKEN")
    owner: Optional[str] = Field(default=None, alias="GITHUB_OWNER")
    repo: Optional[str] = Field(default=None, alias="GITHUB_REPO")
    enabled: bool = Field(default=False)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class SlackSettings(BaseSettings):
    """Slack integration configuration."""

    webhook_url: Optional[str] = Field(default=None, alias="SLACK_WEBHOOK_URL")
    enabled: bool = Field(default=False, alias="SLACK_ENABLED")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class IntegrationSettings(BaseSettings):
    """Integration configuration."""

    jira: JiraSettings = JiraSettings()
    github: GitHubSettings = GitHubSettings()
    slack: SlackSettings = SlackSettings()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class FeatureFlags(BaseSettings):
    """Feature flags configuration."""

    enable_regression_analysis: bool = Field(
        default=True, alias="FEATURE_ENABLE_REGRESSION_ANALYSIS"
    )
    enable_quality_insights: bool = Field(
        default=True, alias="FEATURE_ENABLE_QUALITY_INSIGHTS"
    )
    enable_bug_investigation: bool = Field(
        default=True, alias="FEATURE_ENABLE_BUG_INVESTIGATION"
    )
    enable_jira_integration: bool = Field(
        default=False, alias="FEATURE_ENABLE_JIRA_INTEGRATION"
    )
    enable_github_integration: bool = Field(
        default=False, alias="FEATURE_ENABLE_GITHUB_INTEGRATION"
    )
    enable_slack_notifications: bool = Field(
        default=False, alias="FEATURE_ENABLE_SLACK_NOTIFICATIONS"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(BaseSettings):
    """Main application settings."""

    # API Configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_log_level: str = Field(default="INFO", alias="API_LOG_LEVEL")
    debug: bool = Field(default=False)

    # Environment
    environment: str = Field(default="development")
    version: str = Field(default="1.0.0")

    # Sub-configurations
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    llm: LLMSettings = LLMSettings()
    agents: AgentSettings = AgentSettings()
    test_execution: TestExecutionSettings = TestExecutionSettings()
    integrations: IntegrationSettings = IntegrationSettings()
    features: FeatureFlags = FeatureFlags()

    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, alias="JWT_EXPIRATION_HOURS")

    # Performance Tuning
    request_timeout: int = Field(default=30, alias="REQUEST_TIMEOUT")
    connection_timeout: int = Field(default=10, alias="CONNECTION_TIMEOUT")
    batch_size: int = Field(default=100, alias="BATCH_SIZE")
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")

    # Quality Gates
    min_test_coverage: float = Field(default=80, alias="MIN_TEST_COVERAGE")
    min_test_pass_rate: float = Field(default=95, alias="MIN_TEST_PASS_RATE")
    max_defect_density: float = Field(default=5, alias="MAX_DEFECT_DENSITY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """Get database URL."""
        return self.database.url

    @property
    def redis_url(self) -> str:
        """Get Redis URL."""
        return self.redis.url

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"


# Create global settings instance
settings = Settings()
