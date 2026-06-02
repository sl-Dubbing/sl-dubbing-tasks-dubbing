# tasks_dubbing.py — Celery dubbing worker: R2 → RunPod or Modal
import logging

from flask import Flask

from shared import config
from shared.celery_setup import QUEUE_DUBBING, make_celery_app
from shared.dub_worker_submit import fail_dub_job_permanently, run_dub_worker_pipeline
from shared.job_events import publish_job_status
from shared.models import DubbingJob, db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

celery_app = make_celery_app("tasks-dubbing", queue_name=QUEUE_DUBBING)

flask_app = Flask(__name__)
flask_app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL.replace(
    "postgres://", "postgresql://", 1,
)
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(flask_app)


@celery_app.task(name="tasks_dubbing.process_dub", bind=True, max_retries=0)
def process_dub(
    self,
    job_id,
    user_id,
    file_key,
    lang,
    voice_config=None,
    return_video=True,
    **kwargs,
):
    with flask_app.app_context():
        job = DubbingJob.query.get(job_id)
        if not job:
            logger.error("Job %s not found", job_id)
            return

        job.status = "processing"
        db.session.commit()
        publish_job_status(job_id, {"status": "processing"})

        try:
            run_dub_worker_pipeline(
                job,
                job_id,
                user_id,
                file_key,
                lang,
                voice_config,
                return_video,
                **kwargs,
            )
        except Exception as exc:
            fail_dub_job_permanently(job, job_id, exc)
