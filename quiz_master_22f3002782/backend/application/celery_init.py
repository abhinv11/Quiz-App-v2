from celery import Celery, Task
import celery_config  # <-- import the actual config module

def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)

    # Fix: load config directly from celery_config.py
    celery_app.config_from_object(celery_config)

    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

