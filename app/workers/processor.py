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


def run_worker(poll_interval=1):
    print("worker started")
    while True:
        job = dequeue()
        if job:
            try:
                handle(job)
            except Exception as e:
                print("job failed:", e)
        time.sleep(poll_interval)
