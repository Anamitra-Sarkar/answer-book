import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.api.v1.ingestion import process_file_ingestion
from app.generate.graph import solve_question

router = APIRouter(tags=["Solver"])

@router.post("/solve-question")
def solve_question_endpoint(payload: Dict[str, Any]):
    """Solves a single question through the LangGraph solver engine."""
    question_data = payload.get("question")
    if not question_data:
        raise HTTPException(
            status_code=400,
            detail="Missing 'question' in payload.",
        )
    paper_metadata = payload.get("metadata", {})

    try:
        solution = solve_question(question_data, paper_metadata)
        return solution
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-paper")
def process_paper_endpoint(
    file: UploadFile = File(...),
    limit: Optional[int] = Query(None, description="Max number of questions to solve"),
    subject: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    board: Optional[str] = Query("CBSE"),
):
    """End-to-end pipeline: Ingests paper, solves questions via LangGraph, and saves Solution Book JSON."""
    content = file.file.read()
    paper = process_file_ingestion(
        file=file,
        content=content,
        subject=subject,
        class_name=class_name,
        board=board,
    )

    questions = paper.questions[:limit] if limit else paper.questions
    metadata = {
        "paper_id": paper.paper_id,
        "fingerprint": paper.fingerprint,
        "subject": paper.subject or "General",
        "class": paper.class_name or "Class 9",
        "board": paper.board or "CBSE",
    }

    solutions = []
    for q in questions:
        sol = solve_question(q.model_dump(), metadata)  # Fixed: q.model_dump() called with ()
        solutions.append(sol)

    output_payload = {
        "paper_id": paper.paper_id,
        "fingerprint": paper.fingerprint,
        "status": "ready",
        "metadata": metadata,
        "total_questions": len(solutions),
        "total_marks": paper.total_marks,
        "sections": paper.sections,
        "solutions": solutions,
    }

    output_dir = Path("solutionPapers")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{paper.paper_id}.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)

    return output_payload


@router.get("/solutions/{paper_id}")
def get_solution_endpoint(paper_id: str):
    """Retrieves a previously saved Solution Book JSON by paper_id."""
    file_path = Path("solutionPapers") / f"{paper_id}.json"
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Solution paper '{paper_id}' not found.",
        )
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)