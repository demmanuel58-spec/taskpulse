import time
import traceback
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import TaskRecord, TaskStatus
from app.broker import MessageBroker
from app.tasks import TASK_REGISTRY

broker = MessageBroker()

def process_task(task_data: dict, db: Session):
    task_id = task_data["task_id"]
    task_type = task_data["task_type"]
    payload = task_data["payload"]

    record = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
    if not record:
        return

    record.status = TaskStatus.RUNNING
    db.commit()

    try:
        handler = TASK_REGISTRY.get(task_type)
        if not handler:
            raise ValueError(f"Unknown task type: {task_type}")

        # Execute task logic
        result = handler(payload)

        # Update success state
        record.status = TaskStatus.COMPLETED
        record.error_log = None
        db.commit()
        print(f"[Worker] Task {task_id} COMPLETED: {result}")

    except Exception as exc:
        record.retry_count += 1
        error_msg = f"{str(exc)}\n{traceback.format_exc()}"
        record.error_log = error_msg

        if record.retry_count < record.max_retries:
            record.status = TaskStatus.FAILED
            db.commit()
            
            # Exponential Backoff Delay: 2^retry_count seconds
            backoff_delay = 2 ** record.retry_count
            print(f"[Worker] Task {task_id} failed. Retrying in {backoff_delay}s... (Attempt {record.retry_count}/{record.max_retries})")
            time.sleep(backoff_delay)
            
            # Re-enqueue task
            broker.enqueue(task_id, task_type, payload)
        else:
            # Shift to Dead-Letter Queue (DLQ)
            record.status = TaskStatus.DEAD_LETTER
            db.commit()
            broker.send_to_dlq(task_data, error_message=str(exc))
            print(f"[Worker] Task {task_id} EXCEEDED MAX RETRIES. Moved to DLQ.")

def start_worker():
    print("[Worker] TaskPulse worker process listening for jobs...")
    db = SessionLocal()
    try:
        while True:
            job = broker.dequeue(timeout=2)
            if job:
                process_task(job, db)
    finally:
        db.close()

if __name__ == "__main__":
    start_worker()
