import json
import queue
import threading
import uuid

from flask import Flask, Response, jsonify, render_template, request

from pipeline import run_research_pipeline_stream

app = Flask(__name__)

# Job id -> queue.Queue of progress events. In-memory, single-process store.
# Good enough for local/dev use; swap for Redis pub/sub if you scale to
# multiple workers or processes.
JOBS: dict[str, "queue.Queue"] = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/research", methods=["POST"])
def start_research():
    data = request.get_json(silent=True) or {}
    topic = (data.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "Topic is required."}), 400

    job_id = uuid.uuid4().hex
    q: "queue.Queue" = queue.Queue()
    JOBS[job_id] = q

    def worker():
        def emit(event):
            q.put(event)

        try:
            run_research_pipeline_stream(topic, callback=emit)
        except Exception as exc:  # surface pipeline errors instead of hanging
            emit({"step": "error", "status": "error", "content": str(exc)})
        finally:
            emit({"step": "pipeline", "status": "done", "content": None})

    threading.Thread(target=worker, daemon=True).start()
    return jsonify({"job_id": job_id})


@app.route("/api/stream/<job_id>")
def stream(job_id):
    q = JOBS.get(job_id)
    if q is None:
        return jsonify({"error": "Unknown or expired job."}), 404

    def gen():
        while True:
            event = q.get()
            yield f"data: {json.dumps(event)}\n\n"
            if event.get("step") == "pipeline" and event.get("status") == "done":
                JOBS.pop(job_id, None)
                break

    return Response(gen(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
