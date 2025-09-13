"""Tools and schemas for exam generation."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ExamQuestion(BaseModel):
    """Schema for a single exam question."""
    question_id: int = Field(description="Unique identifier for the question")
    question_type: str = Field(description="Type of question: multiple_choice, short_answer, essay, true_false")
    question_text: str = Field(description="The actual question text")
    options: Optional[List[str]] = Field(default=None, description="Options for multiple choice questions")
    correct_answer: Optional[str] = Field(default=None, description="Correct answer for the question")
    points: int = Field(description="Points awarded for correct answer")
    explanation: Optional[str] = Field(default=None, description="Explanation of the correct answer")


class ExamQuestionList(BaseModel):
    """Schema for a list of exam questions."""
    questions: List[ExamQuestion] = Field(description="List of generated exam questions")


class ExamMetadata(BaseModel):
    """Schema for exam metadata."""
    title: str = Field(description="Title of the exam")
    instructions: str = Field(description="General instructions for taking the exam")
    total_points: int = Field(description="Total points possible on the exam")
    time_limit: Optional[str] = Field(default=None, description="Suggested time limit for the exam")


class ResearchTopicList(BaseModel):
    """Schema for research topics related to the knowledge area."""
    topics: List[str] = Field(description="List of specific research topics to gather information about")


class ExamGenerationRequest(BaseModel):
    """Schema for exam generation request."""
    knowledge_topic: str = Field(description="The main knowledge topic for the exam")
    difficulty_level: str = Field(description="Difficulty level: easy, medium, or hard")
    question_count: int = Field(description="Number of questions to generate")
    question_types: List[str] = Field(description="Types of questions to include")