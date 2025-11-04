"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Processor module for decoupled pipeline processing.
"""

from app.services.processors.base import Processor
from app.services.processors.selection import SelectionProcessor
from app.services.processors.summarization import SummarizationProcessor
from app.services.processors.storage import StorageProcessor

__all__ = [
    "Processor",
    "SelectionProcessor",
    "SummarizationProcessor",
    "StorageProcessor",
]

