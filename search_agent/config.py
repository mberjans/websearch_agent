"""Configuration management for the web search agent system.

This module provides centralized configuration management using Pydantic BaseSettings
to load settings from environment variables and .env files.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
import warnings


class Settings(BaseSettings):
    """
    Centralized application configuration.
    Settings are loaded from environment variables or a .env file.
    """
    
    # API Keys and Secrets
    BRAVE_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    # Google Custom Search Engine
    GOOGLE_CSE_ID: Optional[str] = None
    
    # Evaluator Database
    EVALUATION_DB_PATH: str = "evaluation_log.db"
    
    # LLM Configuration
    LLM_EVALUATOR_MODEL: str = "gpt-4o-mini"
    LLM_SYNTHESIZER_MODEL: str = "gpt-4o-mini"
    
    # OpenRouter Configuration
    USE_OPENROUTER: bool = True
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_REFERER: str = "https://websearch-agent.example.com"
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'  # Ignore extra fields from .env file
    )


# Instantiate a single settings object for the entire application
settings = Settings()


class SearchConfig(BaseModel):
    """Configuration for search-related parameters."""
    provider: str = Field(default="all", description="Search provider(s) to use")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum search results")
    max_urls: int = Field(default=3, ge=1, le=20, description="Maximum URLs to extract")
    timeout: int = Field(default=30, ge=1, le=300, description="Timeout for operations (seconds)")
    cache: bool = Field(default=True, description="Enable caching of search results")
    force_refresh: bool = Field(default=False, description="Force refresh of cached results")


class LLMConfig(BaseModel):
    """Configuration for LLM-related parameters."""
    provider: str = Field(default="openrouter", description="LLM API provider to use")
    model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature parameter for LLM")
    max_tokens: int = Field(default=1024, ge=1, le=8192, description="Maximum tokens for LLM response")
    evaluation: bool = Field(default=True, description="Enable answer quality evaluation")


class OutputConfig(BaseModel):
    """Configuration for output-related parameters."""
    directory: str = Field(default="./output", description="Directory to save results")
    file: str = Field(default="answer_result", description="Base name for output files")
    path: Optional[str] = Field(default=None, description="Absolute path for output file")
    project_name: str = Field(default="default_project", description="Project name for organizing results")


class AdvancedConfig(BaseModel):
    """Configuration for advanced options."""
    proxy: Optional[str] = Field(default=None, description="Proxy URL for web requests")
    user_agent: Optional[str] = Field(default=None, description="Custom user agent for web requests")
    retry_count: int = Field(default=3, ge=0, le=10, description="Number of retries for failed operations")
    extract_images: bool = Field(default=False, description="Extract and include images in results")
    save_html: bool = Field(default=False, description="Save raw HTML of extracted pages")
    debug: bool = Field(default=False, description="Enable debug mode")


class Configuration(BaseModel):
    """
    Main configuration class for the web search agent.
    
    This class centralizes all configuration parameters and provides methods
    to load configuration from various sources.
    """
    query: str = Field(..., description="The user's query to answer")
    search: SearchConfig = Field(default_factory=SearchConfig, description="Search configuration")
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM configuration")
    output: OutputConfig = Field(default_factory=OutputConfig, description="Output configuration")
    advanced: AdvancedConfig = Field(default_factory=AdvancedConfig, description="Advanced configuration")
    
    @classmethod
    def from_env(cls, query: str) -> "Configuration":
        """
        Create configuration from environment variables.
        
        Args:
            query: The user's query
            
        Returns:
            Configuration instance loaded from environment variables
        """
        warnings.warn(
            "Loading configuration from environment variables is deprecated and will be removed in a future version. Please use configuration files or CLI arguments instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return cls(
            query=query,
            search=SearchConfig(
                provider=os.getenv("SEARCH_PROVIDER", "all"),
                max_results=int(os.getenv("MAX_SEARCH_RESULTS", "10")),
                max_urls=int(os.getenv("MAX_URLS_TO_EXTRACT", "3")),
                timeout=int(os.getenv("SEARCH_TIMEOUT", "30")),
                cache=os.getenv("USE_CACHE", "true").lower() == "true",
                force_refresh=os.getenv("FORCE_REFRESH", "false").lower() == "true"
            ),
            llm=LLMConfig(
                provider=os.getenv("LLM_PROVIDER", "openrouter"),
                model=os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
                evaluation=os.getenv("PERFORM_EVALUATION", "true").lower() == "true"
            ),
            output=OutputConfig(
                directory=os.getenv("OUTPUT_DIRECTORY", "./output"),
                file=os.getenv("OUTPUT_FILE", "answer_result"),
                path=os.getenv("OUTPUT_PATH"),
                project_name=os.getenv("PROJECT_NAME", "default_project")
            ),
            advanced=AdvancedConfig(
                proxy=os.getenv("HTTP_PROXY"),
                user_agent=os.getenv("USER_AGENT"),
                retry_count=int(os.getenv("RETRY_COUNT", "3")),
                extract_images=os.getenv("EXTRACT_IMAGES", "false").lower() == "true",
                save_html=os.getenv("SAVE_HTML", "false").lower() == "true",
                debug=os.getenv("DEBUG", "false").lower() == "true"
            )
        )
    
    @classmethod
    def from_file(cls, config_path: str, query: Optional[str] = None) -> "Configuration":
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the configuration file
            query: Optional query to override the one in the config file
            
        Returns:
            Configuration instance loaded from the file
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            PermissionError: If the file cannot be read due to permissions
            yaml.YAMLError: If the YAML file is malformed
            ValueError: If the configuration data is invalid
            OSError: For other file system errors
        """
        try:
            config_path_obj = Path(config_path)
            
            # Check if file exists
            if not config_path_obj.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
            # Check if it's a file (not a directory)
            if not config_path_obj.is_file():
                raise ValueError(f"Path is not a file: {config_path}")
            
            # Check if file is readable
            if not os.access(config_path_obj, os.R_OK):
                raise PermissionError(f"Cannot read configuration file due to permissions: {config_path}")
            
            # Try to open and read the file
            try:
                with open(config_path_obj, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
            except UnicodeDecodeError as e:
                raise ValueError(f"Configuration file contains invalid UTF-8 encoding: {config_path}") from e
            except PermissionError as e:
                raise PermissionError(f"Cannot read configuration file due to permissions: {config_path}") from e
            except OSError as e:
                raise OSError(f"Error reading configuration file {config_path}: {e}") from e
            
            if config_data is None:
                config_data = {}
            
            # Filter out None values to use defaults instead
            filtered_data = {}
            for key, value in config_data.items():
                if value is not None:
                    filtered_data[key] = value
            
            # If query is provided, override the one in the config file
            if query:
                filtered_data["query"] = query
            elif "query" not in filtered_data:
                # If no query in file and none provided, use empty string
                filtered_data["query"] = ""
                
            return cls(**filtered_data)
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file {config_path}: {e}")
        except (FileNotFoundError, PermissionError, OSError, ValueError) as e:
            # Re-raise these specific exceptions as-is
            raise
        except Exception as e:
            raise ValueError(f"Unexpected error loading configuration from {config_path}: {e}")
    
    def to_env_vars(self) -> Dict[str, str]:
        """
        Convert configuration to environment variables.
        
        Returns:
            Dictionary of environment variable names and values
        """
        env_vars = {
            "SEARCH_PROVIDER": self.search.provider,
            "MAX_SEARCH_RESULTS": str(self.search.max_results),
            "MAX_URLS_TO_EXTRACT": str(self.search.max_urls),
            "SEARCH_TIMEOUT": str(self.search.timeout),
            "USE_CACHE": str(self.search.cache).lower(),
            "FORCE_REFRESH": str(self.search.force_refresh).lower(),
            
            "LLM_PROVIDER": self.llm.provider,
            "DEFAULT_LLM_MODEL": self.llm.model,
            "LLM_TEMPERATURE": str(self.llm.temperature),
            "LLM_MAX_TOKENS": str(self.llm.max_tokens),
            "PERFORM_EVALUATION": str(self.llm.evaluation).lower(),
            
            "OUTPUT_DIRECTORY": self.output.directory,
            "OUTPUT_FILE": self.output.file,
            "PROJECT_NAME": self.output.project_name
        }
        
        if self.output.path:
            env_vars["OUTPUT_PATH"] = self.output.path
            
        if self.advanced.proxy:
            env_vars["HTTP_PROXY"] = self.advanced.proxy
            env_vars["HTTPS_PROXY"] = self.advanced.proxy
            
        if self.advanced.user_agent:
            env_vars["USER_AGENT"] = self.advanced.user_agent
            
        env_vars["RETRY_COUNT"] = str(self.advanced.retry_count)
        env_vars["EXTRACT_IMAGES"] = str(self.advanced.extract_images).lower()
        env_vars["SAVE_HTML"] = str(self.advanced.save_html).lower()
        env_vars["DEBUG"] = str(self.advanced.debug).lower()
        
        return env_vars
    
    def set_env_vars(self) -> None:
        """
        Set environment variables based on configuration.
        """
        env_vars = self.to_env_vars()
        for key, value in env_vars.items():
            os.environ[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return self.model_dump()
    
    def to_yaml(self) -> str:
        """
        Convert configuration to YAML string.
        
        Returns:
            YAML string representation of the configuration
        """
        return yaml.dump(self.to_dict(), default_flow_style=False)
    
    def save(self, file_path: str) -> None:
        """
        Save configuration to a YAML file.
        
        Args:
            file_path: Path where to save the configuration
        """
        with open(file_path, 'w') as f:
            f.write(self.to_yaml())
    
    @classmethod
    def merge_configurations(cls, *configs: "Configuration") -> "Configuration":
        """
        Merge multiple configurations with priority order.
        
        Later configurations in the list have higher priority and will override
        earlier configurations. This allows for a clear precedence order:
        1. Default configuration (lowest priority)
        2. Configuration file
        3. Environment variables
        4. Command-line arguments (highest priority)
        
        Args:
            *configs: Configuration objects to merge
            
        Returns:
            Merged configuration object
            
        Raises:
            ValueError: If no configurations provided
        """
        if not configs:
            raise ValueError("At least one configuration must be provided for merging")
        
        if len(configs) == 1:
            # Return a new instance to avoid modifying the original
            return cls(**configs[0].to_dict())
        
        # Start with the first configuration
        merged_dict = configs[0].to_dict()
        
        # Merge subsequent configurations (higher priority)
        for config in configs[1:]:
            merged_dict = cls._deep_merge(merged_dict, config.to_dict())
        
        return cls(**merged_dict)
    
    @staticmethod
    def _deep_merge(base_dict: Dict[str, Any], override_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries, with override_dict taking precedence.
        
        Args:
            base_dict: Base dictionary
            override_dict: Override dictionary (higher priority)
            
        Returns:
            Merged dictionary
        """
        result = base_dict.copy()
        
        for key, value in override_dict.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = Configuration._deep_merge(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                # For lists, we could either extend or replace
                # Here we choose to replace for simplicity, but this could be configurable
                result[key] = value
            elif key in result and isinstance(result[key], set) and isinstance(value, set):
                # For sets, we could either union or replace
                # Here we choose to replace for simplicity
                result[key] = value
            else:
                # Override with new value for all other types
                result[key] = value
        
        return result