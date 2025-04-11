#!/usr/bin/env python3
"""
Model Configuration Module for the AI App Store Build Environment

This module provides functionality for configuring and managing language models
and other AI model settings for the app development environment.
"""

import enum
import uuid
import logging
import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelType(enum.Enum):
    """Enum representing the available model types"""
    LANGUAGE_MODEL = "language_model"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    COMPUTER_VISION = "computer_vision"
    SPEECH_RECOGNITION = "speech_recognition"
    RECOMMENDATION = "recommendation"
    FORECASTING = "forecasting"


class ModelProvider(enum.Enum):
    """Enum representing the available model providers"""
    OPEN_AI = "openai"
    ANTHROPIC = "anthropic"
    HUGGING_FACE = "huggingface"
    INTERNAL = "internal"
    CUSTOM = "custom"


class ModelConfiguration:
    """Class representing a model configuration"""
    
    def __init__(self, name: str, model_type: ModelType, provider: ModelProvider):
        self.id = str(uuid.uuid4())
        self.name = name
        self.model_type = model_type
        self.provider = provider
        self.parameters = {}
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def set_parameter(self, key: str, value: Any) -> None:
        """Set a parameter for the model configuration"""
        self.parameters[key] = value
        self.updated_at = datetime.datetime.utcnow()
        
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Set multiple parameters for the model configuration"""
        self.parameters.update(params)
        self.updated_at = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "model_type": self.model_type.value,
            "provider": self.provider.value,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class LanguageModelConfiguration(ModelConfiguration):
    """Specialized class for language model configurations"""
    
    def __init__(self, name: str, provider: ModelProvider):
        super().__init__(name, ModelType.LANGUAGE_MODEL, provider)
        
        # Set default parameters
        self.set_parameters({
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        })
        
    def set_model_name(self, model_name: str) -> None:
        """Set the specific model name/version to use"""
        self.set_parameter("model_name", model_name)
        
    def set_max_tokens(self, max_tokens: int) -> None:
        """Set the maximum number of tokens to generate"""
        self.set_parameter("max_tokens", max_tokens)
        
    def set_temperature(self, temperature: float) -> None:
        """Set the temperature for sampling"""
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        self.set_parameter("temperature", temperature)
        
    def set_top_p(self, top_p: float) -> None:
        """Set the nucleus sampling parameter"""
        if not 0.0 <= top_p <= 1.0:
            raise ValueError("Top P must be between 0.0 and 1.0")
        self.set_parameter("top_p", top_p)
        
    def set_stop_sequences(self, stop_sequences: List[str]) -> None:
        """Set the stop sequences for generation"""
        self.set_parameter("stop_sequences", stop_sequences)


class ClassificationModelConfiguration(ModelConfiguration):
    """Specialized class for classification model configurations"""
    
    def __init__(self, name: str, provider: ModelProvider):
        super().__init__(name, ModelType.CLASSIFICATION, provider)
        
        # Set default parameters
        self.set_parameters({
            "classes": [],
            "threshold": 0.5,
            "multi_label": False
        })
        
    def set_classes(self, classes: List[str]) -> None:
        """Set the classification classes"""
        self.set_parameter("classes", classes)
        
    def set_threshold(self, threshold: float) -> None:
        """Set the classification threshold"""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        self.set_parameter("threshold", threshold)
        
    def set_multi_label(self, multi_label: bool) -> None:
        """Set whether this is a multi-label classification"""
        self.set_parameter("multi_label", multi_label)


class ModelConfigurationManager:
    """Class for managing model configurations"""
    
    def __init__(self):
        self.configurations: Dict[str, ModelConfiguration] = {}
        
        # Initialize with some default configurations
        self._create_default_configurations()
        
    def _create_default_configurations(self) -> None:
        """Create default model configurations"""
        # OpenAI GPT-4
        gpt4 = LanguageModelConfiguration("GPT-4", ModelProvider.OPEN_AI)
        gpt4.set_model_name("gpt-4")
        self.configurations[gpt4.id] = gpt4
        
        # OpenAI GPT-3.5 Turbo
        gpt35 = LanguageModelConfiguration("GPT-3.5 Turbo", ModelProvider.OPEN_AI)
        gpt35.set_model_name("gpt-3.5-turbo")
        gpt35.set_max_tokens(4096)
        self.configurations[gpt35.id] = gpt35
        
        # Anthropic Claude
        claude = LanguageModelConfiguration("Claude", ModelProvider.ANTHROPIC)
        claude.set_model_name("claude-2")
        claude.set_max_tokens(8192)
        self.configurations[claude.id] = claude
        
        # Hugging Face BERT
        bert = ClassificationModelConfiguration("BERT Classifier", ModelProvider.HUGGING_FACE)
        bert.set_model_name("bert-base-uncased")
        bert.set_classes(["positive", "negative", "neutral"])
        self.configurations[bert.id] = bert
        
    def create_language_model_config(self, name: str, provider: ModelProvider) -> LanguageModelConfiguration:
        """Create a new language model configuration"""
        config = LanguageModelConfiguration(name, provider)
        self.configurations[config.id] = config
        return config
        
    def create_classification_model_config(self, name: str, provider: ModelProvider) -> ClassificationModelConfiguration:
        """Create a new classification model configuration"""
        config = ClassificationModelConfiguration(name, provider)
        self.configurations[config.id] = config
        return config
        
    def get_configuration(self, config_id: str) -> Optional[ModelConfiguration]:
        """Get a configuration by ID"""
        return self.configurations.get(config_id)
        
    def list_configurations(self, model_type: Optional[ModelType] = None, 
                            provider: Optional[ModelProvider] = None) -> List[Dict[str, Any]]:
        """List configurations, optionally filtered by type and/or provider"""
        results = []
        
        for config in self.configurations.values():
            if (model_type is None or config.model_type == model_type) and \
               (provider is None or config.provider == provider):
                results.append(config.to_dict())
                
        return results
        
    def update_configuration(self, config_id: str, parameters: Dict[str, Any]) -> bool:
        """Update a configuration's parameters"""
        if config_id not in self.configurations:
            return False
            
        config = self.configurations[config_id]
        config.set_parameters(parameters)
        return True
        
    def delete_configuration(self, config_id: str) -> bool:
        """Delete a configuration"""
        if config_id not in self.configurations:
            return False
            
        del self.configurations[config_id]
        return True


# Example usage
if __name__ == "__main__":
    # Create model configuration manager
    manager = ModelConfigurationManager()
    
    # List all configurations
    all_configs = manager.list_configurations()
    print(f"Found {len(all_configs)} configurations:")
    for config in all_configs:
        print(f"- {config['name']} ({config['model_type']})")
    
    # Create a new language model configuration
    llama = manager.create_language_model_config("LLaMA 2", ModelProvider.HUGGING_FACE)
    llama.set_model_name("meta-llama/Llama-2-70b-chat-hf")
    llama.set_max_tokens(4096)
    llama.set_temperature(0.8)
    
    # Update an existing configuration
    gpt4_configs = manager.list_configurations(provider=ModelProvider.OPEN_AI)
    if gpt4_configs:
        gpt4_id = gpt4_configs[0]["id"]
        manager.update_configuration(gpt4_id, {"temperature": 0.9, "max_tokens": 8192})
        
        # Get the updated configuration
        updated_config = manager.get_configuration(gpt4_id)
        if updated_config:
            print(f"Updated {updated_config.name} configuration:")
            print(f"- Temperature: {updated_config.parameters['temperature']}")
            print(f"- Max Tokens: {updated_config.parameters['max_tokens']}")