"""LangGraph implementation for exam generation."""

import os
import asyncio
from typing import List, Dict, Any
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableConfig

from agent.exam_state import ExamGenerationState, QuestionGenerationState
from agent.exam_tools_and_schemas import (
    ResearchTopicList, 
    ExamQuestionList, 
    ExamMetadata,
    ExamGenerationRequest
)
from agent.notes_schemas import StudyNotes
from agent.notes_prompts import notes_generator_instructions
from agent.notes_pdf_generator import StudyNotesPDFGenerator
from agent.exam_prompts import (
    research_topic_generator_instructions,
    knowledge_researcher_instructions,
    question_generator_instructions,
    exam_compiler_instructions
)
from agent.prompts import get_current_date
from agent.configuration import Configuration
from agent.pdf_generator import ExamPDFGenerator


def generate_research_topics(state: ExamGenerationState, config: RunnableConfig) -> Dict[str, Any]:
    """Generate research topics for the knowledge area."""
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatOpenAI(
        model=configurable.query_generator_model,
        temperature=0.7,
        max_retries=2,
        api_key=configurable.openai_api_key,
        base_url=configurable.openai_base_url,
    )
    
    structured_llm = llm.with_structured_output(ResearchTopicList)
    
    # Determine number of topics based on question count
    num_topics = min(max(3, state["question_count"] // 3), 8)
    
    # 获取学段和学科描述
    education_descriptions = {
        "primary": "小学(1-6年级)",
        "middle": "初中(7-9年级)", 
        "high": "高中(10-12年级)"
    }
    
    subject_descriptions = {
        "chinese": "语文", "math": "数学", "english": "英语",
        "physics": "物理", "chemistry": "化学", "biology": "生物",
        "history": "历史", "geography": "地理", "politics": "政治/道德与法治",
        "science": "科学", "moral": "道德与法治", "art": "美术",
        "music": "音乐", "pe": "体育", "technology": "信息技术"
    }
    
    formatted_prompt = research_topic_generator_instructions.format(
        current_date=get_current_date(),
        education_level=state["education_level"],
        education_level_desc=education_descriptions.get(state["education_level"], state["education_level"]),
        subject=state["subject"],
        subject_desc=subject_descriptions.get(state["subject"], state["subject"]),
        knowledge_topic=state["knowledge_topic"],
        difficulty_level=state["difficulty_level"],
        question_count=state["question_count"],
        num_topics=num_topics
    )
    
    result = structured_llm.invoke(formatted_prompt)
    return {"research_topics": result.topics}


def continue_to_research(state: ExamGenerationState):
    """Send research topics to parallel research nodes."""
    research_topics = state.get("research_topics", [])
    if not research_topics:
        # If no research topics generated, create a default one
        research_topics = [state["knowledge_topic"]]
    
    return [
        Send("research_knowledge", {
            "research_topic": topic,
            "main_topic": state["knowledge_topic"],
            "difficulty_level": state["difficulty_level"],
            "id": idx
        })
        for idx, topic in enumerate(research_topics)
    ]


def research_knowledge(state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
    """Research knowledge for a specific topic."""
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatOpenAI(
        model=configurable.query_generator_model,
        temperature=0.3,
        max_retries=2,
        api_key=configurable.openai_api_key,
        base_url=configurable.openai_base_url,
    )
    
    formatted_prompt = knowledge_researcher_instructions.format(
        current_date=get_current_date(),
        education_level=state.get("education_level", "middle"),
        subject=state.get("subject", "math"),
        research_topic=state["research_topic"],
        main_topic=state["main_topic"],
        difficulty_level=state["difficulty_level"]
    )
    
    response = llm.invoke(formatted_prompt)
    
    return {
        "research_content": [response.content]
    }


def generate_questions(state: ExamGenerationState, config: RunnableConfig) -> Dict[str, Any]:
    """Generate exam questions based on research content."""
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatOpenAI(
        model=configurable.answer_model,
        temperature=0.5,
        max_retries=2,
        api_key=configurable.openai_api_key,
        base_url=configurable.openai_base_url,
    )
    
    structured_llm = llm.with_structured_output(ExamQuestionList)
    
    # Combine all research content
    combined_research = "\n\n---\n\n".join(state.get("research_content", []))
    
    formatted_prompt = question_generator_instructions.format(
        current_date=get_current_date(),
        knowledge_topic=state["knowledge_topic"],
        difficulty_level=state["difficulty_level"],
        question_types=", ".join(state["question_types"]),
        question_count=state["question_count"],
        research_content=combined_research
    )
    
    result = structured_llm.invoke(formatted_prompt)
    
    # Convert questions to dict format
    questions = []
    for q in result.questions:
        question_dict = {
            "question_id": q.question_id,
            "question_type": q.question_type,
            "question_text": q.question_text,
            "points": q.points
        }
        if q.options:
            question_dict["options"] = q.options
        if q.correct_answer:
            question_dict["correct_answer"] = q.correct_answer
        if q.explanation:
            question_dict["explanation"] = q.explanation
        questions.append(question_dict)
    
    return {"generated_questions": questions}


def compile_exam_metadata(state: ExamGenerationState, config: RunnableConfig) -> Dict[str, Any]:
    """Generate exam title and instructions."""
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatOpenAI(
        model=configurable.answer_model,
        temperature=0.3,
        max_retries=2,
        api_key=configurable.openai_api_key,
        base_url=configurable.openai_base_url,
    )
    
    structured_llm = llm.with_structured_output(ExamMetadata)
    
    formatted_prompt = exam_compiler_instructions.format(
        current_date=get_current_date(),
        knowledge_topic=state["knowledge_topic"],
        difficulty_level=state["difficulty_level"],
        question_count=len(state.get("generated_questions", [])),
        question_types=", ".join(state["question_types"])
    )
    
    result = structured_llm.invoke(formatted_prompt)
    
    return {
        "exam_title": result.title,
        "exam_instructions": result.instructions
    }


def generate_study_notes(state: ExamGenerationState, config: RunnableConfig) -> Dict[str, Any]:
    """Generate study notes based on research content."""
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatOpenAI(
        model=configurable.answer_model,
        temperature=0.3,
        max_retries=2,
        api_key=configurable.openai_api_key,
        base_url=configurable.openai_base_url,
    )
    
    structured_llm = llm.with_structured_output(StudyNotes)
    
    # 获取学段和学科描述
    education_descriptions = {
        "primary": "小学(1-6年级)",
        "middle": "初中(7-9年级)", 
        "high": "高中(10-12年级)"
    }
    
    subject_descriptions = {
        "chinese": "语文", "math": "数学", "english": "英语",
        "physics": "物理", "chemistry": "化学", "biology": "生物",
        "history": "历史", "geography": "地理", "politics": "政治/道德与法治",
        "science": "科学", "moral": "道德与法治", "art": "美术",
        "music": "音乐", "pe": "体育", "technology": "信息技术"
    }
    
    # Combine all research content
    combined_research = "\n\n---\n\n".join(state.get("research_content", []))
    
    formatted_prompt = notes_generator_instructions.format(
        current_date=get_current_date(),
        education_level=state["education_level"],
        education_level_desc=education_descriptions.get(state["education_level"], state["education_level"]),
        subject=state["subject"],
        subject_desc=subject_descriptions.get(state["subject"], state["subject"]),
        knowledge_topic=state["knowledge_topic"],
        difficulty_level=state["difficulty_level"],
        research_content=combined_research
    )
    
    result = structured_llm.invoke(formatted_prompt)
    
    # Convert to dict format
    notes_data = {
        "topic_overview": result.topic_overview,
        "learning_objectives": result.learning_objectives,
        "knowledge_points": [kp.dict() for kp in result.knowledge_points],
        "study_tips": [tip.dict() for tip in result.study_tips],
        "extended_knowledge": [ek.dict() for ek in result.extended_knowledge],
        "summary": result.summary,
        "knowledge_structure": result.knowledge_structure,
        "practice_recommendations": [pr.dict() for pr in result.practice_recommendations],
        "learning_resources": [lr.dict() for lr in result.learning_resources],
        "faqs": [faq.dict() for faq in result.faqs],
        "self_assessment": result.self_assessment
    }
    
    return {"study_notes": notes_data}


async def generate_pdf(state: ExamGenerationState, config: RunnableConfig) -> Dict[str, Any]:
    """Generate PDF files for exam and study notes."""
    
    def _create_pdfs():
        """Synchronous PDF creation function to run in thread."""
        # Create output directory
        output_dir = "generated_exams"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate safe filename
        def create_safe_filename(topic: str, max_length: int = 50) -> str:
            """Create a safe filename from topic string."""
            # Remove special characters and keep only alphanumeric, spaces, hyphens, underscores
            safe_chars = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_', '.')).strip()
            
            # Replace multiple spaces with single space
            safe_chars = ' '.join(safe_chars.split())
            
            # Replace spaces with underscores
            safe_chars = safe_chars.replace(' ', '_')
            
            # Limit length and ensure it doesn't end with underscore
            if len(safe_chars) > max_length:
                safe_chars = safe_chars[:max_length].rstrip('_')
            
            # If empty or too short, use default
            if len(safe_chars) < 3:
                safe_chars = "exam"
            
            return safe_chars
        
        safe_topic = create_safe_filename(state["knowledge_topic"])
        
        # Add timestamp to ensure uniqueness
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate exam PDFs
        exam_filename = f"{safe_topic}_{state['difficulty_level']}_{timestamp}_exam.pdf"
        exam_pdf_path = os.path.join(output_dir, exam_filename)
        
        pdf_generator = ExamPDFGenerator()
        actual_exam_path = pdf_generator.generate_exam_pdf(
            exam_title=state["exam_title"],
            instructions=state["exam_instructions"],
            questions=state["generated_questions"],
            output_path=exam_pdf_path,
            include_answers=False
        )
        
        # Generate answer key
        answer_key_filename = f"{safe_topic}_{state['difficulty_level']}_{timestamp}_answer_key.pdf"
        answer_key_path = os.path.join(output_dir, answer_key_filename)
        
        pdf_generator.generate_exam_pdf(
            exam_title=f"{state['exam_title']} - Answer Key",
            instructions=state["exam_instructions"],
            questions=state["generated_questions"],
            output_path=answer_key_path,
            include_answers=True
        )
        
        # Generate study notes PDF
        notes_filename = f"{safe_topic}_{state['difficulty_level']}_{timestamp}_notes.pdf"
        notes_pdf_path = os.path.join(output_dir, notes_filename)
        
        notes_generator = StudyNotesPDFGenerator()
        actual_notes_path = notes_generator.generate_study_notes_pdf(
            notes_data=state.get("study_notes", {}),
            topic=state["knowledge_topic"],
            subject=state.get("subject", ""),
            education_level=state.get("education_level", ""),
            output_path=notes_pdf_path
        )
        
        return actual_exam_path, answer_key_path, actual_notes_path
    
    # Run PDF generation in a separate thread to avoid blocking
    actual_exam_path, answer_key_path, actual_notes_path = await asyncio.to_thread(_create_pdfs)
    
    return {
        "pdf_path": actual_exam_path,
        "answer_key_path": answer_key_path,
        "notes_path": actual_notes_path,
        "messages": [AIMessage(content=f"Exam and study notes generated successfully! Files saved.")]
    }


# Create the exam generation graph
def create_exam_graph():
    """Create and return the exam generation graph."""
    builder = StateGraph(ExamGenerationState, config_schema=Configuration)
    
    # Add nodes
    builder.add_node("generate_research_topics", generate_research_topics)
    builder.add_node("research_knowledge", research_knowledge)
    builder.add_node("generate_questions", generate_questions)
    builder.add_node("compile_exam_metadata", compile_exam_metadata)
    builder.add_node("generate_study_notes", generate_study_notes)
    builder.add_node("generate_pdf", generate_pdf)
    
    # Add edges
    builder.add_edge(START, "generate_research_topics")
    builder.add_conditional_edges(
        "generate_research_topics", 
        continue_to_research, 
        ["research_knowledge"]
    )
    builder.add_edge("research_knowledge", "generate_questions")
    builder.add_edge("generate_questions", "compile_exam_metadata")
    builder.add_edge("compile_exam_metadata", "generate_study_notes")
    builder.add_edge("generate_study_notes", "generate_pdf")
    builder.add_edge("generate_pdf", END)
    
    return builder.compile(name="exam-generator-agent")


# Create the graph instance
exam_graph = create_exam_graph()