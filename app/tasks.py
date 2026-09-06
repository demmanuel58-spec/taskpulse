import time
import random

def task_generate_pdf_report(payload: dict) -> dict:
    """Simulates a heavy PDF generation job."""
    report_id = payload.get("report_id", "N/A")
    time.sleep(3)  # Simulate CPU/IO delay
    return {"status": "success", "message": f"Report {report_id} generated successfully."}

def task_send_bulk_email(payload: dict) -> dict:
    """Simulates sending transactional emails with artificial failure for testing retries."""
    recipient_count = payload.get("count", 0)
    
    # Simulate flaky network connection
    if random.choice([True, False]):
        raise ConnectionError("SMTP server timeout. Retry required.")
        
    return {"status": "success", "message": f"Dispatched {recipient_count} emails."}

# Task registry mapping string names to functions
TASK_REGISTRY = {
    "generate_pdf_report": task_generate_pdf_report,
    "send_bulk_email": task_send_bulk_email,
}
