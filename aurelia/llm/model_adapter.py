"""
Aurelia Cognitive OS V3 - Phase 7: Model Adapter
================================================
Adapts different LLM models for use in the cognitive system.

The model adapter provides a unified interface for different LLM
models (Ollama, local models, etc.) for semantic reasoning.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
import requests
import json


class ModelProvider(Enum):
    """Types of model providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class ModelCapability(Enum):
    """Capabilities of models."""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    REASONING = "reasoning"


@dataclass
class ModelConfig:
    """Configuration for a model."""
    provider: ModelProvider
    model_name: str
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    capabilities: List[ModelCapability] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelResponse:
    """Response from a model."""
    content: str
    model_name: str
    tokens_used: int
    finish_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ModelAdapter:
    """
    Adapts different LLM models for use in the cognitive system.
    
    The model adapter:
    - Provides unified interface for different model providers
    - Handles API calls to Ollama and other providers
    - Manages model configuration
    - Handles errors and retries
    """
    
    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.default_model: Optional[str] = None
    
    def register_model(self, model_id: str, config: ModelConfig):
        """Register a model configuration."""
        self.models[model_id] = config
        if self.default_model is None:
            self.default_model = model_id
    
    def set_default_model(self, model_id: str):
        """Set the default model to use."""
        if model_id in self.models:
            self.default_model = model_id
        else:
            raise ValueError(f"Model {model_id} not registered")
    
    def get_model(self, model_id: Optional[str] = None) -> ModelConfig:
        """Get a model configuration."""
        model_id = model_id or self.default_model
        if not model_id:
            raise ValueError("No model specified and no default model set")
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not registered")
        return self.models[model_id]
    
    def generate_completion(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> ModelResponse:
        """Generate a completion using the specified model."""
        config = self.get_model(model_id)
        
        if config.provider == ModelProvider.OLLAMA:
            return self._ollama_completion(config, prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Provider {config.provider} not yet implemented")
    
    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> ModelResponse:
        """Generate a chat completion using the specified model."""
        config = self.get_model(model_id)
        
        if config.provider == ModelProvider.OLLAMA:
            return self._ollama_chat_completion(config, messages, temperature, max_tokens)
        else:
            raise ValueError(f"Provider {config.provider} not yet implemented")
    
    def _ollama_completion(
        self,
        config: ModelConfig,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> ModelResponse:
        """Generate completion using Ollama API."""
        endpoint = config.api_endpoint or "http://localhost:11434/api/generate"
        
        payload = {
            "model": config.model_name,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature or config.temperature,
            "num_predict": max_tokens or config.max_tokens
        }
        
        try:
            response = requests.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            return ModelResponse(
                content=data.get("response", ""),
                model_name=config.model_name,
                tokens_used=data.get("eval_count", 0) + data.get("prompt_eval_count", 0),
                finish_reason=data.get("done_reason", "stop"),
                metadata={"raw_response": data}
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Ollama API error: {e}")
    
    def _ollama_chat_completion(
        self,
        config: ModelConfig,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> ModelResponse:
        """Generate chat completion using Ollama API."""
        endpoint = config.api_endpoint or "http://localhost:11434/api/chat"
        
        payload = {
            "model": config.model_name,
            "messages": messages,
            "stream": False,
            "temperature": temperature or config.temperature,
            "num_predict": max_tokens or config.max_tokens
        }
        
        try:
            response = requests.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            return ModelResponse(
                content=data.get("message", {}).get("content", ""),
                model_name=config.model_name,
                tokens_used=data.get("eval_count", 0) + data.get("prompt_eval_count", 0),
                finish_reason=data.get("done_reason", "stop"),
                metadata={"raw_response": data}
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Ollama API error: {e}")
    
    def list_ollama_models(self, api_endpoint: str = "http://localhost:11434") -> List[str]:
        """List available models from Ollama."""
        try:
            response = requests.get(f"{api_endpoint}/api/tags", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            models = [model.get("name", "") for model in data.get("models", [])]
            return models
        except requests.RequestException as e:
            print(f"Could not list Ollama models: {e}")
            return []
    
    def initialize_default_ollama_models(self):
        """Initialize default Ollama models."""
        # Try to connect to Ollama and register available models
        available_models = self.list_ollama_models()
        
        if available_models:
            print(f"Found {len(available_models)} Ollama models: {available_models}")
            
            # Register the first available model as default
            for model_name in available_models:
                model_id = model_name.replace(":", "_")
                self.register_model(
                    model_id,
                    ModelConfig(
                        provider=ModelProvider.OLLAMA,
                        model_name=model_name,
                        api_endpoint="http://localhost:11434",
                        capabilities=[ModelCapability.CHAT, ModelCapability.COMPLETION]
                    )
                )
                
                # Set first one as default
                if self.default_model is None:
                    self.set_default_model(model_id)
        else:
            print("No Ollama models found. Please ensure Ollama is running and has models installed.")
            # Register a placeholder for manual configuration
            self.register_model(
                "default_ollama",
                ModelConfig(
                    provider=ModelProvider.OLLAMA,
                    model_name="llama2",  # Common default
                    api_endpoint="http://localhost:11434",
                    capabilities=[ModelCapability.CHAT, ModelCapability.COMPLETION]
                )
            )
            self.set_default_model("default_ollama")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the model adapter state."""
        return {
            "total_models": len(self.models),
            "by_provider": {provider.value: len([m for m in self.models.values() if m.provider == provider]) for provider in ModelProvider},
            "default_model": self.default_model,
            "available_ollama_models": self.list_ollama_models()
        }