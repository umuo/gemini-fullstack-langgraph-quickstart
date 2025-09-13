# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
import os
import asyncio
from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List

# Define the FastAPI app
app = FastAPI()


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    return StaticFiles(directory=build_path, html=True)


# Exam generation request model
class ExamRequest(BaseModel):
    education_level: str = "middle"  # primary, middle, high
    subject: str = "math"
    knowledge_topic: str
    difficulty_level: str = "medium"
    question_count: int = 10
    question_types: List[str] = ["multiple_choice", "short_answer"]


# API endpoint for exam generation
@app.post("/generate-exam")
async def generate_exam(request: ExamRequest):
    """Generate an exam based on the provided parameters."""
    try:
        from agent.exam_graph import exam_graph
        from agent.configuration import Configuration
        from langchain_core.messages import HumanMessage
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=f"Generate an exam about {request.knowledge_topic}")],
            "knowledge_topic": request.knowledge_topic,
            "difficulty_level": request.difficulty_level,
            "question_count": request.question_count,
            "question_types": request.question_types,
            "research_content": [],
            "generated_questions": [],
            "exam_title": "",
            "exam_instructions": "",
            "pdf_content": None,
            "pdf_path": None
        }
        
        # Run the exam generation graph
        config = {"configurable": {}}
        result = exam_graph.invoke(initial_state, config)
        
        return {
            "success": True,
            "exam_title": result.get("exam_title", ""),
            "exam_instructions": result.get("exam_instructions", ""),
            "questions": result.get("generated_questions", []),
            "pdf_path": result.get("pdf_path", ""),
            "answer_key_path": result.get("answer_key_path", ""),
            "message": "Exam generated successfully!"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating exam: {str(e)}")


# API endpoint for streaming exam generation
from fastapi.responses import StreamingResponse
import json
import time

@app.post("/generate-exam-stream")
async def generate_exam_stream(request: ExamRequest):
    """Generate an exam with streaming progress updates."""
    
    async def generate():
        try:
            from agent.exam_graph import exam_graph
            from agent.configuration import Configuration
            from langchain_core.messages import HumanMessage
            
            # Send initial status
            yield f"data: {json.dumps({'step': 'initializing', 'message': '初始化试卷生成...', 'progress': 5})}\n\n"
            await asyncio.sleep(0.1)  # Small delay to ensure message is sent
            
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=f"Generate an exam about {request.knowledge_topic}")],
                "education_level": request.education_level,
                "subject": request.subject,
                "knowledge_topic": request.knowledge_topic,
                "difficulty_level": request.difficulty_level,
                "question_count": request.question_count,
                "question_types": request.question_types,
                "research_content": [],
                "generated_questions": [],
                "exam_title": "",
                "exam_instructions": "",
                "pdf_content": None,
                "pdf_path": None
            }
            
            config = {"configurable": {}}
            
            # Manual step execution with progress updates
            yield f"data: {json.dumps({'step': 'research_topics', 'message': '生成研究主题...', 'progress': 15})}\n\n"
            
            # Step 1: Generate research topics
            from agent.exam_graph import generate_research_topics
            state = generate_research_topics(initial_state, config)
            initial_state.update(state)
            
            topics = initial_state.get('research_topics', [])
            yield f"data: {json.dumps({'step': 'research_topics', 'message': f'已生成 {len(topics)} 个研究主题', 'progress': 25, 'data': topics})}\n\n"
            
            # Step 2: Research knowledge
            yield f"data: {json.dumps({'step': 'research_knowledge', 'message': '收集知识内容...', 'progress': 35})}\n\n"
            
            from agent.exam_graph import research_knowledge
            research_results = []
            for i, topic in enumerate(topics):
                research_state = {
                    "research_topic": topic,
                    "main_topic": initial_state["knowledge_topic"],
                    "difficulty_level": initial_state["difficulty_level"],
                    "id": i
                }
                result = research_knowledge(research_state, config)
                research_results.extend(result.get("research_content", []))
                
                progress = 35 + (i + 1) / len(topics) * 15
                yield f"data: {json.dumps({'step': 'research_knowledge', 'message': f'正在研究: {topic}', 'progress': progress})}\n\n"
            
            initial_state["research_content"] = research_results
            
            # Step 3: Generate questions
            yield f"data: {json.dumps({'step': 'generate_questions', 'message': '开始生成题目...', 'progress': 55})}\n\n"
            
            from agent.exam_graph import generate_questions
            question_state = generate_questions(initial_state, config)
            initial_state.update(question_state)
            
            questions = initial_state.get("generated_questions", [])
            yield f"data: {json.dumps({'step': 'generate_questions', 'message': f'已生成 {len(questions)} 道题目', 'progress': 70, 'data': {'question_count': len(questions)}})}\n\n"
            
            # Step 4: Compile metadata
            yield f"data: {json.dumps({'step': 'compile_metadata', 'message': '编译试卷信息...', 'progress': 70})}\n\n"
            
            from agent.exam_graph import compile_exam_metadata
            metadata_state = compile_exam_metadata(initial_state, config)
            initial_state.update(metadata_state)
            
            title = initial_state.get("exam_title", "")
            yield f"data: {json.dumps({'step': 'compile_metadata', 'message': '试卷信息编译完成', 'progress': 75, 'data': {'title': title}})}\n\n"
            
            # Step 5: Generate study notes
            yield f"data: {json.dumps({'step': 'generate_notes', 'message': '生成学习笔记...', 'progress': 80})}\n\n"
            
            from agent.exam_graph import generate_study_notes
            notes_state = generate_study_notes(initial_state, config)
            initial_state.update(notes_state)
            
            yield f"data: {json.dumps({'step': 'generate_notes', 'message': '学习笔记生成完成', 'progress': 85})}\n\n"
            
            # Step 6: Generate PDF
            yield f"data: {json.dumps({'step': 'generate_pdf', 'message': '生成PDF文件...', 'progress': 90})}\n\n"
            
            from agent.exam_graph import generate_pdf
            pdf_state = await generate_pdf(initial_state, config)
            initial_state.update(pdf_state)
            
            # Send completion
            result = {
                'success': True,
                'exam_title': initial_state.get('exam_title', ''),
                'exam_instructions': initial_state.get('exam_instructions', ''),
                'questions': initial_state.get('generated_questions', []),
                'pdf_path': initial_state.get('pdf_path', ''),
                'answer_key_path': initial_state.get('answer_key_path', ''),
                'notes_path': initial_state.get('notes_path', ''),
                'study_notes': initial_state.get('study_notes', {})
            }
            
            yield f"data: {json.dumps({'step': 'completed', 'message': '试卷生成完成！', 'progress': 100, 'result': result})}\n\n"
            
        except Exception as e:
            import traceback
            error_msg = f"生成失败: {str(e)}"
            print(f"Error in exam generation: {traceback.format_exc()}")
            yield f"data: {json.dumps({'step': 'error', 'message': error_msg, 'progress': 0, 'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")


# API endpoint to download generated PDF
@app.get("/download-pdf/{filename}")
async def download_pdf(filename: str):
    """Download a generated PDF file."""
    
    def _check_file():
        file_path = os.path.join("generated_exams", filename)
        return file_path, os.path.exists(file_path)
    
    file_path, exists = await asyncio.to_thread(_check_file)
    
    if not exists:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment"}
    )


@app.get("/preview-pdf/{filename}")
async def preview_pdf(filename: str):
    """Preview a generated PDF file inline in browser."""
    
    def _check_file():
        file_path = os.path.join("generated_exams", filename)
        return file_path, os.path.exists(file_path)
    
    file_path, exists = await asyncio.to_thread(_check_file)
    
    if not exists:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline",
            "Cache-Control": "no-cache"
        }
    )


# API endpoint to list generated exams
@app.get("/list-exams")
async def list_exams():
    """List all generated exam files."""
    
    def _list_files():
        exam_dir = "generated_exams"
        if not os.path.exists(exam_dir):
            return []
        
        files = []
        for filename in os.listdir(exam_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(exam_dir, filename)
                file_stats = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": file_stats.st_size,
                    "created": file_stats.st_ctime
                })
        return files
    
    files = await asyncio.to_thread(_list_files)
    return {"exams": files}


# Mount the frontend under /app to not conflict with the LangGraph API routes
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
