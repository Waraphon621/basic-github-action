# basic-github-action

Lab repo for **Lab 3 — GitHub Actions** and **Lab 3b — Secrets & Environment Variables**
(see `resource/github-action-lab-guide.pdf`).

Minimal FastAPI app + Dockerfile + GitHub Actions workflows demonstrating CI build, test, and push to Docker Hub.

## Structure

```
.
├── Dockerfile
├── requirements.txt
├── src/
│   ├── main.py              # FastAPI app: GET / -> {"message","status"}
│   └── tests/test_main.py   # pytest, 1 test
└── .github/workflows/
    ├── 01-echo.yaml         # echo demo, push + workflow_dispatch
    ├── 02-echo-2.yaml       # echo demo 2
    ├── 03-build-test.yaml   # docker build + pytest
    └── 04-build-test-push.yaml  # build + test + login + tag + push to Docker Hub
```

## Workflows

| File | Trigger | Job |
|---|---|---|
| `01-echo.yaml` | `push`, `workflow_dispatch` | echo context vars, `actions/checkout@v4`, `ls` workspace |
| `02-echo-2.yaml` | `push` | minimal echo + checkout |
| `03-build-test.yaml` | `push` to `main`, `workflow_dispatch` | `docker build -t testapi .` → `docker run testapi pytest` |
| `04-build-test-push.yaml` | `push` to `main` | build + test + `docker/login-action@v3` + tag `dev-${{ github.run_number }}` + push to Docker Hub |

## Required secrets (for `04-build-test-push.yaml`)

Repo → Settings → Secrets and variables → Actions:

- `DOCKER_USERNAME` — Docker Hub username
- `DOCKER_PASSWORD` — Docker Hub access token (PAT, not password)

## Local test

### Build + pytest in Docker

```bash
docker build -t testapi .
docker run --rm testapi pytest
```

### Run workflows locally via [act](https://github.com/nektos/act)

```bash
# 01-echo
act push -W .github/workflows/01-echo.yaml \
  --container-architecture linux/amd64 \
  -P ubuntu-latest=catthehacker/ubuntu:act-latest

# 03-build-test
act push -W .github/workflows/03-build-test.yaml \
  --container-architecture linux/amd64 \
  -P ubuntu-latest=catthehacker/ubuntu:act-latest

# 04-build-test-push (needs real Docker Hub creds for full pass)
act push -W .github/workflows/04-build-test-push.yaml \
  --container-architecture linux/amd64 \
  -P ubuntu-latest=catthehacker/ubuntu:act-latest \
  -s DOCKER_USERNAME=<user> -s DOCKER_PASSWORD=<token>
```

### Run app locally

```bash
docker build -t testapi .
docker run --rm -p 10000:10000 testapi
# open http://localhost:10000/
```

## Simple Todo demo

The app now serves a small Todo UI at `/`.

API routes:

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/tasks` | List all tasks |
| `POST` | `/api/tasks` | Create a task with title, detail, due date, and checklist |
| `PATCH` | `/api/tasks/{task_id}/end` | Mark a task as done |

Example create request:

```json
{
  "title": "Prepare demo",
  "detail": "Create a simple Todo example",
  "due_at": "2026-05-22T10:00:00",
  "checklist": [
    { "text": "Create API" },
    { "text": "Add UI" }
  ]
}
```

## Lab tasks (from `resource/github-action-lab-guide.pdf`)

### Lab 3 — GitHub Actions
1. Fork + clone repo
2. View `.github/workflows/*.yml`
3. Enable Actions on forked repo
4. Trigger via `git push`
5. View run on Actions tab
6. Add custom step to a workflow:
   ```yaml
   - name: Say Hello
     run: echo "Hello from ${{ github.actor }}!"
   ```

### Lab 3b — Secrets & Environment Variables
1. Add repo secret `MY_SECRET_MESSAGE` = `Hello from secret!`
2. Add step using secret as env:
   ```yaml
   - name: Use Secret
     run: |
       echo "Secret value: $MY_MSG"
       echo "Actor: ${{ github.actor }}"
     env:
       MY_MSG: ${{ secrets.MY_SECRET_MESSAGE }}
   ```
3. Push + view logs (secret masked as `***`)
4. Add workflow-level `env:` block:
   ```yaml
   env:
     APP_NAME: my-fastapi-app
     NODE_ENV: production
   ```
   Use via `${{ env.APP_NAME }}`
5. Try printing secret directly — confirm GitHub masks output:
   ```yaml
   - name: Try to print secret directly
     run: echo ${{ secrets.MY_SECRET_MESSAGE }}
   ```
 อ้อน
