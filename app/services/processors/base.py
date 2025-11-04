"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Base processor interface for pipeline processing.
"""

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Optional
from app.schemas import RawArticle, SelectedArticle, ProcessedArticle

# Type variables for generic processor
TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class Processor(ABC, Generic[TInput, TOutput]):
    """Abstract base class for pipeline processors."""
    
    def __init__(self, name: str):
        """
        Initialize processor.
        
        Args:
            name: Name of the processor for logging and identification
        """
        self.name = name
        self.enabled = True
    
    @abstractmethod
    async def process(self, input_data: TInput) -> TOutput:
        """
        Process input data and return output.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed output data
            
        Raises:
            ProcessingError: If processing fails
        """
        pass
    
    def enable(self) -> None:
        """Enable the processor."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the processor."""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if processor is enabled."""
        return self.enabled


class ProcessingError(Exception):
    """Exception raised when processing fails."""
    
    def __init__(self, message: str, processor_name: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.processor_name = processor_name
        self.original_error = original_error

