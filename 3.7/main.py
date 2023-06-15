import os
import sys

sys.dont_write_bytecode = True

from flask import Flask
from flask import request
import logging
import random
import platform
import time
import pickle

# Try to import App Engine Bundled Service
# https://github.com/GoogleCloudPlatform/appengine-python-standard/tree/main
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.api import memcache
from google.appengine.api import taskqueue, wrap_wsgi_app

QUEUE_PULL_NAME = "queue-pull"
QUEUE_PULL = taskqueue.Queue(QUEUE_PULL_NAME)

QUEUE_PUSH_NAME = "queue-push"
QUEUE_PUSH = taskqueue.Queue(QUEUE_PUSH_NAME)

app = Flask(__name__)
# Prevent AssertionError: No api proxy found for service "taskqueue", ...
app.wsgi_app = wrap_wsgi_app(app.wsgi_app, use_deferred=True)
# To log INFO and DEBUG messages when running my Flask application behind uwsgi
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

python_version = platform.python_version()


def throw_random_exception():
    exception_list = [
        IndexError("Index out of range!"),
        ValueError("Invalid value!"),
        TypeError("Invalid type!"),
        KeyError("Key not found!"),
        IOError("Input/output error!"),
    ]

    should_throw_exception = random.choice([True, False])

    if should_throw_exception:
        random_exception = random.choice(exception_list)
        raise random_exception


def do_something_later(timestamp):
    app.logger.info("Process by deferred queue")
    path = ""
    if os.getenv("GAE_ENV", "").startswith("standard"):
        # Production in the standard environment
        # The filesystem is read-only except for the location /tmp, which is a virtual disk storing data in your App Engine instance's RAM.
        path = "/tmp"
    else:
        # Local execution.
        path = os.getcwd()
    # Appending to file
    with open("{path}/do_something.log".format(path=path), "a+") as f:
        f.write(str(timestamp))
        f.write("\n")
    logging.info(
        "Do something with deferred queue. File {path} / {timestamp}".format(
            path=path, timestamp=timestamp
        )
    )


def get_unix_timestamp():
    return int(time.time())


@app.route("/")
def home():
    return "[{v}] Home page".format(v=python_version)


@app.route("/about")
def about():
    try:
        throw_random_exception()
        print("No exception was thrown.")
        return "[{v}] About page".format(v=python_version)
    except Exception as e:
        logging.exception("An LOGGING exception occurred: {ex}".format(ex=str(e)))
        return "[{v}] Exception: {ex}".format(v=python_version, ex=str(e))


@app.route("/error")
def error():
    try:
        raise ValueError("This is a sample value error.")
    except ValueError:
        logging.error("This is an error message")
        return "[{v}] Error page".format(v=python_version)


@app.route("/task")
def task():
    logging.info("Operate Task schedule with Cron")
    return "[{v}] Task schedule page".format(v=python_version)


@app.route("/pushq")
def pushq():
    app.logger.info("Enqueue task to PUSH queue")
    timestamp = get_unix_timestamp()
    payload = pickle.dumps({"name": QUEUE_PUSH_NAME, "timestamp": timestamp})
    QUEUE_PUSH.add(taskqueue.Task(payload=payload, method="PUT"))
    return "[{v}] Enqueue task to PUSH queue page".format(v=python_version)


@app.route("/pullq")
def pullq():
    app.logger.info("Enqueue task to PULL queue")
    timestamp = get_unix_timestamp()
    payload = pickle.dumps({"name": QUEUE_PULL_NAME, "timestamp": timestamp})
    QUEUE_PULL.add(taskqueue.Task(payload=payload, method="PULL"))
    return "[{v}] Enqueue task to PULL queue page".format(v=python_version)


@app.route("/_ah/queue/queue-push", methods=["PUT"])
def queue_push():
    data = pickle.loads(request.data)
    app.logger.info(data)
    return "OK", 200


@app.route("/depullq")
def depullq():
    app.logger.info("Dequeue PUSH QUEUE task")
    HOUR = 3600
    TASKS = 1000
    tasks = QUEUE_PULL.lease_tasks(HOUR, TASKS)
    for task in tasks:
        payload = pickle.loads(task.payload)
        app.logger.info(
            "Process {name} queue - {timestamp} task".format(
                name=payload["name"], timestamp=payload["timestamp"]
            )
        )
    if tasks:
        QUEUE_PULL.delete_tasks(tasks)
    return "[{v}] Dequeue page - Done {t} tasks".format(v=python_version, t=len(tasks))


@app.route("/defer")
def defer():
    retry = taskqueue.TaskRetryOptions(task_retry_limit=0)
    timestamp = get_unix_timestamp()
    # Use default URL and queue name, no task name, execute after 5s.
    deferred.defer(
        do_something_later, str(timestamp), _countdown=5, _retry_options=retry
    )
    return "[{v}] Deferred Queue page".format(v=python_version)


@app.route("/_ah/queue/deferred", methods=["POST"])
def dequeue_defer():
    app.logger.info(request.data)
    # deferred.run(request.data)
    return "OK", 200


@app.route("/setcache", methods=["GET"])
def setcache():
    timestamp = get_unix_timestamp()
    memcache.add(key="ts", value=timestamp, time=30)
    return "[{v}] SET cache = {ts} with ttl=30s".format(v=python_version, ts=timestamp)


@app.route("/getcache", methods=["GET"])
def getcache():
    timestamp = memcache.get(key="ts")
    if timestamp is None:
        return "[{v}] Uninitialized cache"
    return "[{v}] GET cache = {ts}".format(v=python_version, ts=timestamp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8037")
