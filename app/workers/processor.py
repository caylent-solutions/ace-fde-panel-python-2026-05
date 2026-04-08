import time
from app.workers.queue import dequeue

# TODO: add retry logic, dead-letter queue


def handle(job):
    job_type = job.get("type")
    payload = job.get("payload", {})
    if job_type == "send_notification":
        print("sending notification", payload)
    elif job_type == "run_workflow":
        print("running workflow", payload)
    else:
        print("unknown job type", job_type)


MAX_CONSECUTIVE_ERRORS = 10


def run_worker(poll_interval=1):
    print("worker started")
    errors = 0
    while True:
        job = dequeue()
        if job:
            try:
                handle(job)
                errors = 0
            except Exception as e:
                print("job failed:", e)
                errors += 1
                if errors >= MAX_CONSECUTIVE_ERRORS:
                    print("too many consecutive errors, stopping worker")
                    break
        time.sleep(poll_interval)
