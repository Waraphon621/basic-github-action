from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


app = FastAPI(title="Simple Todo API")


class ChecklistCreate(BaseModel):
    text: str = Field(..., min_length=1)


class ChecklistItem(ChecklistCreate):
    id: int
    done: bool = False


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    detail: str = ""
    due_at: datetime
    checklist: list[ChecklistCreate] = Field(default_factory=list)


class Task(TaskCreate):
    id: int
    checklist: list[ChecklistItem] = Field(default_factory=list)
    done: bool = False
    created_at: datetime
    ended_at: datetime | None = None


tasks: list[Task] = []
next_task_id = 1


@app.get("/", response_class=HTMLResponse, tags=["home"])
async def home() -> str:
    return """
<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Simple Todo</title>
  <style>
    :root {
      color: #202124;
      font-family: Arial, sans-serif;
      background: #f6f7fb;
    }

    body {
      margin: 0;
    }

    main {
      max-width: 920px;
      margin: 0 auto;
      padding: 32px 18px;
    }

    h1 {
      margin: 0 0 6px;
      font-size: 30px;
    }

    .subtitle {
      margin: 0 0 22px;
      color: #5f6368;
    }

    .panel {
      background: #fff;
      border: 1px solid #e1e4ea;
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 10px 26px rgba(32, 33, 36, 0.06);
    }

    form {
      display: grid;
      gap: 12px;
      margin-bottom: 18px;
    }

    label {
      display: grid;
      gap: 6px;
      font-weight: 700;
      font-size: 14px;
    }

    input,
    textarea {
      border: 1px solid #c9ced6;
      border-radius: 6px;
      padding: 10px 12px;
      font: inherit;
    }

    textarea {
      min-height: 86px;
      resize: vertical;
    }

    button {
      border: 0;
      border-radius: 6px;
      background: #1967d2;
      color: #fff;
      cursor: pointer;
      font-weight: 700;
      padding: 11px 14px;
    }

    button.secondary {
      background: #1f7a4d;
    }

    .tasks {
      display: grid;
      gap: 12px;
      margin-top: 18px;
    }

    .task {
      border: 1px solid #e1e4ea;
      border-radius: 8px;
      padding: 14px;
      background: #fff;
    }

    .task.done {
      background: #eef8f1;
      color: #4d6657;
    }

    .task-head {
      align-items: start;
      display: flex;
      gap: 12px;
      justify-content: space-between;
    }

    .task h2 {
      font-size: 18px;
      margin: 0;
    }

    .meta {
      color: #5f6368;
      font-size: 13px;
      margin-top: 4px;
    }

    .detail {
      margin: 10px 0;
      white-space: pre-wrap;
    }

    ul {
      margin: 8px 0 0;
      padding-left: 20px;
    }

    @media (min-width: 760px) {
      form {
        grid-template-columns: 1fr 1fr;
      }

      label.wide {
        grid-column: 1 / -1;
      }
    }
  </style>
</head>
<body>
  <main>
    <h1>Simple Todo</h1>
    <p class="subtitle">สร้าง task ใส่รายละเอียด วันเวลาที่ต้องทำ checklist และกด End task เมื่อเสร็จแล้ว</p>
    <section class="panel">
      <form id="task-form">
        <label>
          ชื่องาน
          <input id="title" required placeholder="เช่น ส่งรายงาน" />
        </label>
        <label>
          วันเวลาที่ต้องทำ
          <input id="due_at" required type="datetime-local" />
        </label>
        <label class="wide">
          รายละเอียด
          <textarea id="detail" placeholder="รายละเอียดของงาน"></textarea>
        </label>
        <label class="wide">
          Checklist
          <input id="checklist" placeholder="คั่นแต่ละข้อด้วย comma เช่น เตรียมไฟล์, ตรวจข้อมูล" />
        </label>
        <button type="submit">Create task</button>
      </form>
      <div id="tasks" class="tasks"></div>
    </section>
  </main>
  <script>
    const form = document.querySelector("#task-form");
    const list = document.querySelector("#tasks");
    const escapeHtml = (value) => String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

    const formatDate = (value) => new Intl.DateTimeFormat("th-TH", {
      dateStyle: "medium",
      timeStyle: "short"
    }).format(new Date(value));

    async function loadTasks() {
      const response = await fetch("/api/tasks");
      const tasks = await response.json();

      list.innerHTML = tasks.length ? "" : "<p class='meta'>ยังไม่มี task</p>";
      tasks.forEach((task) => {
        const item = document.createElement("article");
        item.className = `task ${task.done ? "done" : ""}`;
        item.innerHTML = `
          <div class="task-head">
            <div>
              <h2>${task.title}</h2>
              <div class="meta">Due: ${formatDate(task.due_at)}</div>
            </div>
            ${task.done ? "<strong>Done</strong>" : `<button class="secondary" data-id="${task.id}">End task</button>`}
          </div>
          <p class="detail">${escapeHtml(task.detail || "")}</p>
          ${task.checklist.length ? `<ul>${task.checklist.map((check) => `<li>${escapeHtml(check.text)}</li>`).join("")}</ul>` : ""}
        `;
        item.querySelector("h2").textContent = task.title;
        list.appendChild(item);
      });
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const checklist = document.querySelector("#checklist").value
        .split(",")
        .map((text) => text.trim())
        .filter(Boolean)
        .map((text) => ({ text }));

      await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: document.querySelector("#title").value,
          detail: document.querySelector("#detail").value,
          due_at: new Date(document.querySelector("#due_at").value).toISOString(),
          checklist
        })
      });

      form.reset();
      await loadTasks();
    });

    list.addEventListener("click", async (event) => {
      const button = event.target.closest("button[data-id]");
      if (!button) return;

      await fetch(`/api/tasks/${button.dataset.id}/end`, { method: "PATCH" });
      await loadTasks();
    });

    loadTasks();
  </script>
</body>
</html>
    """


@app.get("/api/health", tags=["health"])
async def health() -> dict:
    return {"message": "Hello world", "status": True}


@app.get("/api/tasks", response_model=list[Task], tags=["tasks"])
async def list_tasks() -> list[Task]:
    return tasks


@app.post("/api/tasks", response_model=Task, status_code=201, tags=["tasks"])
async def create_task(payload: TaskCreate) -> Task:
    global next_task_id

    task = Task(
        id=next_task_id,
        title=payload.title,
        detail=payload.detail,
        due_at=payload.due_at,
        checklist=[
            ChecklistItem(id=index + 1, text=item.text)
            for index, item in enumerate(payload.checklist)
        ],
        created_at=datetime.utcnow(),
    )
    next_task_id += 1
    tasks.append(task)
    return task


@app.patch("/api/tasks/{task_id}/end", response_model=Task, tags=["tasks"])
async def end_task(task_id: int) -> Task:
    for task in tasks:
        if task.id == task_id:
            task.done = True
            task.ended_at = datetime.utcnow()
            return task

    raise HTTPException(status_code=404, detail="Task not found")
