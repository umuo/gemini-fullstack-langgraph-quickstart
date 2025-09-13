"""State definitions for the exam generation agent."""

from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class ExamGenerationState(TypedDict):
    """State for exam generation process."""
    messages: Annotated[List[BaseMessage], add_messages]
    education_level: str  # "primary", "middle", "high"
    subject: str  # subject identifier
    knowledge_topic: str
    difficulty_level: str  # "easy", "medium", "hard"
    question_count: int
    question_types: List[str]  # ["multiple_choice", "short_answer", "essay", "true_false", "fill_blank", "calculation", "analysis", "application"]
    research_content: List[str]
    generated_questions: List[Dict[str, Any]]
    exam_title: str
    exam_instructions: str
    study_notes: Optional[Dict[str, Any]]  # 添加学习笔记
    pdf_content: Optional[str]
    pdf_path: Optional[str]
    notes_path: Optional[str]  # 添加笔记PDF路径


class QuestionGenerationState(TypedDict):
    """State for individual question generation."""
    topic: str
    difficulty: str
    question_type: str
    research_content: str
    question_id: int


class ExamCompilationState(TypedDict):
    """State for exam compilation and PDF generation."""
    exam_title: str
    exam_instructions: str
    questions: List[Dict[str, Any]]
    difficulty_level: str
    pdf_path: str