#!/usr/bin/env python3
"""
Chat Interface Module for AI App Store Workspaces

This module provides functionality for general chat within workspaces,
supporting various models, modalities, and integration with apps.
"""

import enum
import uuid
import logging
import datetime
import json
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(enum.Enum):
    """Enum representing the types of chat messages"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    CODE = "code"
    SYSTEM = "system"
    CUSTOM = "custom"


class ModelProvider(enum.Enum):
    """Enum representing the available model providers"""
    OPEN_AI = "openai"
    ANTHROPIC = "anthropic"
    INTERNAL = "internal"
    CUSTOM = "custom"


class Model:
    """Represents a language model that can be used in chat"""
    
    def __init__(self, name: str, provider: ModelProvider, 
                capabilities: List[str], parameters: Dict[str, Any] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.provider = provider
        self.capabilities = capabilities
        self.parameters = parameters or {}
        self.created_at = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider.value,
            "capabilities": self.capabilities,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat()
        }


class Message:
    """Represents a chat message"""
    
    def __init__(self, message_type: MessageType, content: Any, sender: str):
        self.id = str(uuid.uuid4())
        self.message_type = message_type
        self.content = content
        self.sender = sender
        self.timestamp = datetime.datetime.utcnow()
        self.metadata = {}
        
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the message"""
        self.metadata[key] = value
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        content_repr = self.content
        if self.message_type == MessageType.IMAGE:
            # For images, use a reference instead of raw data
            content_repr = {"image_reference": "image_data_not_included"}
            
        return {
            "id": self.id,
            "message_type": self.message_type.value,
            "content": content_repr,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class Chat:
    """Represents a chat session"""
    
    def __init__(self, title: str, created_by: str):
        self.id = str(uuid.uuid4())
        self.title = title
        self.created_by = created_by
        self.messages: List[Message] = []
        self.participants: List[str] = [created_by]
        self.model: Optional[Model] = None
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.metadata = {}
        
    def add_message(self, message: Message) -> None:
        """Add a message to the chat"""
        self.messages.append(message)
        
        # Add sender to participants if not already there
        if message.sender not in self.participants:
            self.participants.append(message.sender)
            
        self.updated_at = datetime.datetime.utcnow()
        
    def set_model(self, model: Model) -> None:
        """Set the model for this chat"""
        self.model = model
        self.updated_at = datetime.datetime.utcnow()
        
    def add_participant(self, participant_id: str) -> None:
        """Add a participant to the chat"""
        if participant_id not in self.participants:
            self.participants.append(participant_id)
            self.updated_at = datetime.datetime.utcnow()
            
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the chat"""
        self.metadata[key] = value
        self.updated_at = datetime.datetime.utcnow()
        
    def get_messages(self, limit: Optional[int] = None, 
                    message_type: Optional[MessageType] = None) -> List[Message]:
        """Get messages from the chat, optionally filtered"""
        if message_type:
            filtered = [m for m in self.messages if m.message_type == message_type]
        else:
            filtered = self.messages
            
        if limit:
            return filtered[-limit:]
        return filtered
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "title": self.title,
            "created_by": self.created_by,
            "participants": self.participants,
            "model": self.model.to_dict() if self.model else None,
            "message_count": len(self.messages),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }


class Modality:
    """Represents a modality handler for different types of content"""
    
    def __init__(self, name: str, supported_types: List[MessageType]):
        self.name = name
        self.supported_types = supported_types
        
    def can_handle(self, message_type: MessageType) -> bool:
        """Check if this modality can handle a message type"""
        return message_type in self.supported_types
        
    def process_input(self, content: Any, message_type: MessageType) -> Any:
        """Process input content for this modality"""
        raise NotImplementedError("Subclasses must implement process_input()")
        
    def generate_output(self, content: Any, message_type: MessageType) -> Any:
        """Generate output content for this modality"""
        raise NotImplementedError("Subclasses must implement generate_output()")


class TextModality(Modality):
    """Handles text content"""
    
    def __init__(self):
        super().__init__("Text", [MessageType.TEXT])
        
    def process_input(self, content: str, message_type: MessageType) -> str:
        """Process text input"""
        if message_type != MessageType.TEXT:
            raise ValueError(f"Unsupported message type: {message_type}")
            
        # Just return the text as is for this example
        return content
        
    def generate_output(self, content: str, message_type: MessageType) -> str:
        """Generate text output"""
        if message_type != MessageType.TEXT:
            raise ValueError(f"Unsupported message type: {message_type}")
            
        # Just return the text as is for this example
        return content


class ImageModality(Modality):
    """Handles image content"""
    
    def __init__(self):
        super().__init__("Image", [MessageType.IMAGE])
        
    def process_input(self, content: Any, message_type: MessageType) -> Dict[str, Any]:
        """Process image input"""
        if message_type != MessageType.IMAGE:
            raise ValueError(f"Unsupported message type: {message_type}")
            
        # In a real implementation, this would process the image
        # For this example, we'll just return some metadata
        return {
            "image_processed": True,
            "format": "jpeg",
            "dimensions": "800x600"
        }
        
    def generate_output(self, content: Dict[str, Any], message_type: MessageType) -> Dict[str, Any]:
        """Generate image output"""
        if message_type != MessageType.IMAGE:
            raise ValueError(f"Unsupported message type: {message_type}")
            
        # In a real implementation, this would generate an image
        # For this example, we'll just return some metadata
        return {
            "image_generated": True,
            "format": content.get("format", "png"),
            "dimensions": content.get("dimensions", "512x512")
        }


class CodeModality(Modality):
    """Handles code content"""
    
    def __init__(self):
        super().__init__("Code", [MessageType.CODE])
        
    def process_input(self, content: Dict[str, Any], message_type: MessageType) -> Dict[str, Any]:
        """Process code input"""
        if message_type != MessageType.CODE:
            raise ValueError(f"Unsupported message type: {message_type}")
            
        # Expected content: {"code": "...", "language": "..."}
        if not isinstance(content, dict) or "code" not in content:
            raise ValueError("Invalid code content format")
            
        # In a real implementation, this might validate or preprocess the code
        return content
        
    def generate_output(self, content: Dict[str, Any], message_type: MessageType) -> Dict[str, Any]:
        """Generate code output"""
        if message_type != MessageType.CODE:
            raise ValueError(f"Unsupported message type: {message_type}")
            
        # In a real implementation, this might format or highlight the code
        return content


class VoiceModality(Modality):
    """Handles voice content with TTS and STT"""
    
    def __init__(self):
        super().__init__("Voice", [MessageType.AUDIO, MessageType.TEXT])
        
    def process_input(self, content: Any, message_type: MessageType) -> Dict[str, Any]:
        """Process voice input (STT)"""
        if message_type == MessageType.AUDIO:
            # In a real implementation, this would convert audio to text
            # For this example, we'll simulate it
            return {
                "original_audio": "audio_reference",
                "transcription": "This is a simulated transcription of audio input",
                "confidence": 0.95
            }
        elif message_type == MessageType.TEXT:
            # Just pass through text
            return {"text": content}
        else:
            raise ValueError(f"Unsupported message type: {message_type}")
            
    def generate_output(self, content: Dict[str, Any], message_type: MessageType) -> Dict[str, Any]:
        """Generate voice output (TTS)"""
        if message_type == MessageType.TEXT:
            # In a real implementation, this would convert text to audio
            # For this example, we'll simulate it
            text = content if isinstance(content, str) else content.get("text", "")
            return {
                "text": text,
                "audio_generated": True,
                "duration_seconds": len(text) / 15  # Rough estimate
            }
        else:
            raise ValueError(f"Unsupported message type for TTS: {message_type}")


class ModelAdapter:
    """Adapter for interfacing with different language models"""
    
    def __init__(self, model: Model):
        self.model = model
        
    def prepare_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Prepare messages for the model in the appropriate format"""
        prepared = []
        
        for message in messages:
            # Convert message type to role for the model
            role = "user"
            if message.sender == "assistant":
                role = "assistant"
            elif message.sender == "system":
                role = "system"
                
            prepared.append({
                "role": role,
                "content": message.content,
                "message_type": message.message_type.value
            })
            
        return prepared
        
    def generate_response(self, prepared_messages: List[Dict[str, Any]],
                         parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a response from the model"""
        # Merge model parameters with request-specific parameters
        merged_params = {**self.model.parameters}
        if parameters:
            merged_params.update(parameters)
            
        # In a real implementation, this would call the appropriate API
        # For this example, we'll simulate a response
        logger.info(f"Generating response with {self.model.name} ({self.model.provider.value})")
        
        # Get the last message for context
        last_message = prepared_messages[-1]
        
        # Simulate different responses based on provider
        if self.model.provider == ModelProvider.OPEN_AI:
            response = f"OpenAI model response to: {last_message['content']}"
        elif self.model.provider == ModelProvider.ANTHROPIC:
            response = f"Anthropic model response to: {last_message['content']}"
        else:
            response = f"Generic model response to: {last_message['content']}"
            
        return {
            "content": response,
            "message_type": "text",
            "model": self.model.name,
            "usage": {
                "prompt_tokens": sum(len(m["content"].split()) for m in prepared_messages if isinstance(m["content"], str)),
                "completion_tokens": len(response.split()),
                "total_tokens": sum(len(m["content"].split()) for m in prepared_messages if isinstance(m["content"], str)) + len(response.split())
            }
        }


class ChatManager:
    """Main class for managing chat sessions"""
    
    def __init__(self):
        self.chats: Dict[str, Chat] = {}
        self.models: Dict[str, Model] = {}
        self.modalities: Dict[str, Modality] = {}
        
        # Initialize default models and modalities
        self._initialize_defaults()
        
    def _initialize_defaults(self) -> None:
        """Initialize default models and modalities"""
        # Create default models
        gpt4 = Model(
            "GPT-4",
            ModelProvider.OPEN_AI,
            ["text", "code", "image-understanding"],
            {"temperature": 0.7, "max_tokens": 2000}
        )
        self.models[gpt4.id] = gpt4
        
        claude = Model(
            "Claude",
            ModelProvider.ANTHROPIC,
            ["text", "code", "image-understanding"],
            {"temperature": 0.5, "max_tokens": 4000}
        )
        self.models[claude.id] = claude
        
        # Create default modalities
        text_modality = TextModality()
        self.modalities[text_modality.name] = text_modality
        
        image_modality = ImageModality()
        self.modalities[image_modality.name] = image_modality
        
        code_modality = CodeModality()
        self.modalities[code_modality.name] = code_modality
        
        voice_modality = VoiceModality()
        self.modalities[voice_modality.name] = voice_modality
        
    def create_chat(self, title: str, created_by: str, model_id: Optional[str] = None) -> str:
        """Create a new chat session"""
        chat = Chat(title, created_by)
        
        if model_id and model_id in self.models:
            chat.set_model(self.models[model_id])
            
        self.chats[chat.id] = chat
        return chat.id
        
    def get_chat(self, chat_id: str) -> Optional[Chat]:
        """Get a chat by ID"""
        return self.chats.get(chat_id)
        
    def list_chats(self, created_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """List chats, optionally filtered by creator"""
        result = []
        
        for chat in self.chats.values():
            if created_by and chat.created_by != created_by:
                continue
                
            result.append(chat.to_dict())
            
        return result
        
    def add_message(self, chat_id: str, message_type: MessageType, 
                  content: Any, sender: str) -> Optional[str]:
        """Add a message to a chat"""
        chat = self.chats.get(chat_id)
        if not chat:
            return None
            
        message = Message(message_type, content, sender)
        
        # Process the message with the appropriate modality if available
        for modality in self.modalities.values():
            if modality.can_handle(message_type):
                try:
                    processed_content = modality.process_input(content, message_type)
                    message.content = processed_content
                    message.add_metadata("processed_by", modality.name)
                    break
                except Exception as e:
                    logger.error(f"Error processing message with {modality.name}: {str(e)}")
                    
        chat.add_message(message)
        return message.id
        
    def generate_response(self, chat_id: str, parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate a response from the model in a chat"""
        chat = self.chats.get(chat_id)
        if not chat or not chat.model:
            return None
            
        # Create model adapter
        adapter = ModelAdapter(chat.model)
        
        # Prepare messages
        prepared_messages = adapter.prepare_messages(chat.messages)
        
        # Generate response
        response = adapter.generate_response(prepared_messages, parameters)
        
        # Add response to chat
        message_type = MessageType(response["message_type"])
        message_id = self.add_message(
            chat_id,
            message_type,
            response["content"],
            "assistant"
        )
        
        return message_id
        
    def get_messages(self, chat_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get messages from a chat"""
        chat = self.chats.get(chat_id)
        if not chat:
            return []
            
        messages = chat.get_messages(limit)
        return [m.to_dict() for m in messages]
        
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        return [model.to_dict() for model in self.models.values()]
        
    def register_model(self, name: str, provider: ModelProvider, 
                      capabilities: List[str], parameters: Dict[str, Any] = None) -> str:
        """Register a new model"""
        model = Model(name, provider, capabilities, parameters)
        self.models[model.id] = model
        return model.id
        
    def set_chat_model(self, chat_id: str, model_id: str) -> bool:
        """Set the model for a chat"""
        chat = self.chats.get(chat_id)
        model = self.models.get(model_id)
        
        if not chat or not model:
            return False
            
        chat.set_model(model)
        return True
        
    def register_modality(self, modality: Modality) -> None:
        """Register a new modality handler"""
        self.modalities[modality.name] = modality
        
    def text_to_speech(self, text: str) -> Dict[str, Any]:
        """Convert text to speech using the voice modality"""
        voice_modality = self.modalities.get("Voice")
        if not voice_modality:
            return {"error": "Voice modality not available"}
            
        try:
            return voice_modality.generate_output({"text": text}, MessageType.TEXT)
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}")
            return {"error": str(e)}
            
    def speech_to_text(self, audio_content: Any) -> Dict[str, Any]:
        """Convert speech to text using the voice modality"""
        voice_modality = self.modalities.get("Voice")
        if not voice_modality:
            return {"error": "Voice modality not available"}
            
        try:
            return voice_modality.process_input(audio_content, MessageType.AUDIO)
        except Exception as e:
            logger.error(f"Error in speech-to-text: {str(e)}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    # Create chat manager
    manager = ChatManager()
    
    # List available models
    models = manager.list_models()
    print(f"Available models ({len(models)}):")
    for model in models:
        print(f"- {model['name']} ({model['provider']})")
        
    # Create a chat using Claude
    claude_model_id = None
    for model in models:
        if model["name"] == "Claude":
            claude_model_id = model["id"]
            break
            
    user_id = "user-123"
    chat_id = manager.create_chat("AI Discussion", user_id, claude_model_id)
    print(f"\nCreated chat: {chat_id}")
    
    # Add a message to the chat
    message_id = manager.add_message(
        chat_id,
        MessageType.TEXT,
        "What are the key benefits of AI in home lending?",
        user_id
    )
    print(f"Added message: {message_id}")
    
    # Generate a response
    response_id = manager.generate_response(chat_id)
    print(f"Generated response: {response_id}")
    
    # Get chat messages
    messages = manager.get_messages(chat_id)
    print("\nChat messages:")
    for msg in messages:
        print(f"[{msg['sender']}] {msg['content']}")
        
    # Test voice features
    print("\nTesting voice features:")
    tts_result = manager.text_to_speech("Welcome to the AI App Store")
    print(f"Text-to-speech result: {tts_result}")
    
    # Simulate STT
    audio_content = "simulated_audio_data"
    stt_result = manager.speech_to_text(audio_content)
    print(f"Speech-to-text result: {stt_result}")
    
    # Add a code message
    code_msg_id = manager.add_message(
        chat_id,
        MessageType.CODE,
        {
            "code": "def calculate_loan(principal, rate, years):\n    monthly_rate = rate / 100 / 12\n    months = years * 12\n    return principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)",
            "language": "python"
        },
        user_id
    )
    print(f"\nAdded code message: {code_msg_id}")
    
    # Test switching models
    gpt4_model_id = None
    for model in models:
        if model["name"] == "GPT-4":
            gpt4_model_id = model["id"]
            break
            
    if gpt4_model_id:
        success = manager.set_chat_model(chat_id, gpt4_model_id)
        print(f"\nSwitched to GPT-4: {success}")
        
        # Generate another response
        response_id = manager.generate_response(chat_id)
        print(f"Generated response with GPT-4: {response_id}")
        
        # Get the latest messages
        latest_messages = manager.get_messages(chat_id, limit=2)
        print("\nLatest messages:")
        for msg in latest_messages:
            print(f"[{msg['sender']}] {msg['content']}")