"""
Aurelia Cognitive OS V3 - Phase 10: User-Specific Models
=======================================================
Builds and maintains user-specific models for personalization.

User-specific models allow Aurelia to adapt to individual users'
preferences, patterns, and characteristics for more personalized interactions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class ModelType(Enum):
    """Types of user-specific models."""
    PREFERENCE = "preference"
    BEHAVIOR = "behavior"
    COMMUNICATION = "communication"
    LEARNING = "learning"


@dataclass
class UserFeature:
    """
    A feature in a user-specific model.
    
    Represents a characteristic or pattern of the user.
    """
    name: str
    value: Any
    confidence: float  # 0-1 scale
    last_updated: datetime
    access_count: int


@dataclass
class UserModel:
    """
    A user-specific model.
    
    Contains features and patterns specific to a user.
    """
    user_id: str
    model_type: ModelType
    features: Dict[str, UserFeature]
    created_at: datetime
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class UserModelManager:
    """
    Builds and maintains user-specific models for personalization.
    
    The user model manager:
    - Extracts features from user interactions
    - Builds and updates user models
    - Personalizes responses based on user models
    - Tracks model accuracy and effectiveness
    """
    
    def __init__(self):
        self.user_models: Dict[str, Dict[ModelType, UserModel]] = {}
        self.model_counter = 0
    
    def create_user_model(
        self,
        user_id: str,
        model_type: ModelType,
        initial_features: Optional[Dict[str, Any]] = None
    ) -> UserModel:
        """Create a new user model."""
        if user_id not in self.user_models:
            self.user_models[user_id] = {}
        
        # Convert initial features to UserFeature objects
        features = {}
        if initial_features:
            for name, value in initial_features.items():
                features[name] = UserFeature(
                    name=name,
                    value=value,
                    confidence=0.5,  # Initial confidence
                    last_updated=datetime.now(),
                    access_count=0
                )
        
        model = UserModel(
            user_id=user_id,
            model_type=model_type,
            features=features,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.user_models[user_id][model_type] = model
        return model
    
    def update_feature(
        self,
        user_id: str,
        model_type: ModelType,
        feature_name: str,
        feature_value: Any,
        confidence_increment: float = 0.1
    ):
        """Update a feature in a user model."""
        model = self.get_user_model(user_id, model_type)
        if not model:
            model = self.create_user_model(user_id, model_type)
        
        if feature_name in model.features:
            # Update existing feature
            feature = model.features[feature_name]
            feature.value = feature_value
            feature.confidence = min(1.0, feature.confidence + confidence_increment)
            feature.last_updated = datetime.now()
            feature.access_count += 1
        else:
            # Add new feature
            model.features[feature_name] = UserFeature(
                name=feature_name,
                value=feature_value,
                confidence=0.5,
                last_updated=datetime.now(),
                access_count=1
            )
        
        model.last_updated = datetime.now()
    
    def get_feature(
        self,
        user_id: str,
        model_type: ModelType,
        feature_name: str
    ) -> Optional[UserFeature]:
        """Get a specific feature from a user model."""
        model = self.get_user_model(user_id, model_type)
        if not model:
            return None
        
        return model.features.get(feature_name)
    
    def get_user_model(self, user_id: str, model_type: ModelType) -> Optional[UserModel]:
        """Get a user model."""
        if user_id not in self.user_models:
            return None
        
        return self.user_models[user_id].get(model_type)
    
    def get_high_confidence_features(
        self,
        user_id: str,
        model_type: ModelType,
        min_confidence: float = 0.7
    ) -> List[UserFeature]:
        """Get features with confidence above a threshold."""
        model = self.get_user_model(user_id, model_type)
        if not model:
            return []
        
        return [f for f in model.features.values() if f.confidence >= min_confidence]
    
    def personalize_response(
        self,
        user_id: str,
        base_response: str
    ) -> str:
        """
        Personalize a response based on user models.
        
        Adapts the response based on user preferences and communication style.
        """
        # Get communication model
        comm_model = self.get_user_model(user_id, ModelType.COMMUNICATION)
        
        if not comm_model:
            return base_response
        
        # Get high-confidence features
        features = self.get_high_confidence_features(user_id, ModelType.COMMUNICATION)
        
        # Apply personalization based on features
        personalized = base_response
        
        for feature in features:
            if feature.name == "style" and feature.value == "concise":
                # Make response more concise
                personalized = self._make_concise(personalized)
            elif feature.name == "style" and feature.value == "detailed":
                # Ensure response is detailed
                personalized = self._ensure_detailed(personalized)
            elif feature.name == "formality" and feature.value == "formal":
                # Make response more formal
                personalized = self._make_formal(personalized)
            elif feature.name == "formality" and feature.value == "casual":
                # Make response more casual
                personalized = self._make_casual(personalized)
        
        return personalized
    
    def _make_concise(self, text: str) -> str:
        """Make text more concise (simplified)."""
        # In full system, would use NLP techniques
        # For now, return as-is
        return text
    
    def _ensure_detailed(self, text: str) -> str:
        """Ensure text is detailed (simplified)."""
        # In full system, would add more detail
        # For now, return as-is
        return text
    
    def _make_formal(self, text: str) -> str:
        """Make text more formal (simplified)."""
        # In full system, would use formal language patterns
        # For now, return as-is
        return text
    
    def _make_casual(self, text: str) -> str:
        """Make text more casual (simplified)."""
        # In full system, would use casual language patterns
        # For now, return as-is
        return text
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the user model manager state."""
        total_models = sum(len(models) for models in self.user_models.values())
        
        return {
            "total_users": len(self.user_models),
            "total_models": total_models,
            "by_type": {
                mt.value: sum(1 for models in self.user_models.values() if mt in models)
                for mt in ModelType
            }
        }