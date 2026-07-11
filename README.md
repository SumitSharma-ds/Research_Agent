# Research_Agent

A Flask web UI for a multi-agent research pipeline (search → read → write → critique). Instead of waiting on one long response, each agent streams its status live over Server-Sent Events, so you watch the pipeline work stage by stage in a clean, modern interface.

## Features

 **4-stage agent pipeline** — search, read/scrape, write, and self-critique, wired to your existing LangChain/LangGraph agents
 **Live progress via SSE** — a pipeline "rail" lights up in real time as each agent starts and finishes, no page refresh or long blank spinner
 **Markdown-rendered report** — the final report renders on a distinct "paper" card, separate from the agent step logs
 **Modern, responsive UI** — clean white theme, collapsible step cards, works down to mobile

## Tech stack

- **Backend:** Flask, Server-Sent Events, Python threading for background jobs
- **Frontend:** vanilla HTML/CSS/JS,for Markdown rendering
- **Agents:**

## Project structure

```
Research_Agent/
├── app.py             
├── pipeline.py          
├── agents.py           
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/script.js
```

## How it works

1. `POST /api/research` starts the pipeline in a background thread and returns a `job_id`.
2. `GET /api/stream/<job_id>` is an SSE endpoint the browser subscribes to; each pipeline stage pushes a `{step, status, content}` event as it starts and finishes.
3. `pipeline.py` wraps `build_search_agent`, `build_reader_agent`, `writer_chain`, and `critic_chain` — same logic as a plain sequential run, just instrumented with progress callbacks.

## Roadmap ideas

- [ ] Persist past runs (SQLite) instead of in-memory job store
- [ ] Export report as PDF / Markdown file
- [ ] Support multiple concurrent pipelines per session
- [ ] Auth for multi-user deployments
