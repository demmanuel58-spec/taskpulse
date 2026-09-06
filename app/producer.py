from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.database import get_db, engine, Base
from app.models import TaskRecord, TaskStatus
from app.broker import MessageBroker
from app.tasks import TASK_REGISTRY

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskPulse Producer API",
    description="High-throughput distributed task dispatching and state monitoring API.",
    version="1.0.0"
)

broker = MessageBroker()

class TaskSubmitRequest(BaseModel):
    task_type: str = Field(..., example="generate_pdf_report")
    payload: Dict[str, Any] = Field(..., example={"report_id": "REP-8802", "format": "pdf"})
    max_retries: Optional[int] = Field(default=3, ge=1, le=10)

class TaskSubmitResponse(BaseModel):
    task_id: str
    task_type: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    task_type: str
    status: str
    retry_count: int
    max_retries: int
    error_log: Optional[str]
    created_at: str

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "TaskPulse Producer"}

@app.post(
    "/tasks", 
    response_model=TaskSubmitResponse, 
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Task Dispatcher"]
)
def submit_task(request: TaskSubmitRequest, db: Session = Depends(get_db)):
    if request.task_type not in TASK_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task_type. Supported types: {list(TASK_REGISTRY.keys())}"
        )

    # 1. Persist initial task state in PostgreSQL
    new_task = TaskRecord(
        task_type=request.task_type,
        payload=request.payload,
        max_retries=request.max_retries,
        status=TaskStatus.PENDING
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # 2. Push job payload into Redis Message Queue
    try:
        broker.enqueue(
            task_id=new_task.id,
            task_type=new_task.task_type,
            payload=new_task.payload
        )
    except Exception as exc:
        new_task.status = TaskStatus.FAILED
        new_task.error_log = f"Failed to enqueue to Redis: {str(exc)}"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit task to message broker."
        )

    return TaskSubmitResponse(
        task_id=new_task.id,
        task_type=new_task.task_type,
        status=new_task.status.value,
        message="Task queued successfully for background execution."
    )

@app.get("/tasks/{task_id}", response_model=TaskStatusResponse, tags=["Task Monitor"])
def get_task_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task ID not found.")

    return TaskStatusResponse(
        task_id=task.id,
        task_type=task.task_type,
        status=task.status.value,
        retry_count=task.retry_count,
        max_retries=task.max_retries,
        error_log=task.error_log,
        created_at=task.created_at.isoformat()
    )
