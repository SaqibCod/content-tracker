# API Contract — Telusko Workflow Engine

Derived from `frontend/app.js` (`api.*` wrappers + `mockFetch`). The backend
must satisfy these exact shapes so the frontend can swap `mockFetch` for real
`fetch()` against `http://localhost:8000` with no other changes.

## Conventions

- Base URL: `http://localhost:8000`
- All request/response bodies are JSON (`Content-Type: application/json`).
- Task `state` is one of the ordered `STATES` keys:
  `code_ready` → `recorded` → `editing` → `uploaded` → `published`.
- `assignedRole` is one of: `Admin`, `Content`, `Editor`, `Uploader`.

### Task object

The shape the frontend reads when rendering cards:

```json
{
  "id": 1,
  "title": "Introduction to Spring Boot",
  "assignedRole": "Content",
  "state": "code_ready",
  "description": "Cover project setup, auto-configuration, and starter dependencies.",
  "createdAt": "2026-05-01"
}
```

| Field          | Type   | Notes                                              |
| -------------- | ------ | -------------------------------------------------- |
| `id`           | int    | Server-assigned, unique.                           |
| `title`        | string | Required, non-empty.                               |
| `assignedRole` | string | One of the four roles above.                       |
| `state`        | string | One of the five `STATES` keys.                     |
| `description`  | string | May be empty.                                      |
| `createdAt`    | string | Date `YYYY-MM-DD`. Server-assigned on create.      |

> Field names are **camelCase** (`assignedRole`, `createdAt`). Pydantic schemas
> must serialize with these aliases — the frontend reads them verbatim.

---

## 1. `getTasks` — `GET /api/tasks`

Frontend call (`api.getTasks`):
- Sends no body.
- Expects `res.ok` true and `res.data` to be an **array of Task objects**.

**Response `200`:**

```json
[
  { "id": 1, "title": "...", "assignedRole": "Content", "state": "code_ready", "description": "...", "createdAt": "2026-05-01" }
]
```

Error handling: this is the only call that swallows errors — on non-2xx or
network failure it shows a toast and falls back to the local in-memory list.
The backend should still return a proper array on success.

---

## 2. `createTask` — `POST /api/tasks`

Frontend call (`api.createTask(payload)`) sends:

```json
{
  "title": "string",
  "description": "string",
  "assignedRole": "Content",
  "state": "code_ready"
}
```

- `id` and `createdAt` are **not** sent — the server assigns them.
- `title` is trimmed and guaranteed non-empty by the UI (still validate server-side).

**Response `201` (or `200`)** — the created Task object including `id` and `createdAt`:

```json
{ "id": 6, "title": "...", "assignedRole": "Content", "state": "code_ready", "description": "...", "createdAt": "2026-06-17" }
```

On non-2xx the frontend throws and surfaces `Save failed: Server error <status>`.

---

## 3. `updateTask` — `PUT /api/tasks/{id}`

Used in two ways, so the endpoint must accept a **partial** body:

1. Drag/advance — `{ "state": "recorded" }`
2. Modal edit — full payload:

```json
{
  "title": "string",
  "description": "string",
  "assignedRole": "Editor",
  "state": "editing"
}
```

**Response `200`** — the updated Task object (same shape as `getTasks` items).

On non-2xx the frontend throws: `Could not move/advance task` or `Save failed`.

> Recommend treating this as PATCH-like semantics under the PUT verb: only
> overwrite fields present in the body. `id`/`createdAt` are never sent and must
> not be required.

---

## 4. `deleteTask` — `DELETE /api/tasks/{id}`

- Sends no body.
- Frontend only checks `res.ok`; it ignores the response body and returns `true`.

**Response `200` or `204`** — body optional/ignored.

On non-2xx the frontend throws: `Could not delete task: Server error <status>`.

---

## Error-handling contract

`mockFetch` normalizes every response to `{ ok, status, data }`:

- `ok` = HTTP response `ok` (2xx).
- `status` = HTTP status code.
- `data` = parsed JSON when `Content-Type` includes `application/json`, else `null`.

The wrappers then enforce:

| Method       | On non-2xx                                            |
| ------------ | ----------------------------------------------------- |
| `getTasks`   | Toast `Failed to load tasks: Server error <status>`, falls back to local cache (no throw). |
| `createTask` | Throws `Server error <status>` → toast `Save failed`. |
| `updateTask` | Throws `Server error <status>` → toast `Could not move/advance task` or `Save failed`. |
| `deleteTask` | Throws `Server error <status>` → toast `Could not delete task`. |

Implications for the backend:
- Use standard HTTP status codes; any non-2xx is treated as failure.
- Error bodies are not parsed by the frontend (only `status` is shown), so an
  error JSON shape is optional — but a FastAPI `{ "detail": "..." }` body is fine.
- Validation failures (e.g. bad `state`/`assignedRole`, empty `title`) should
  return `4xx`. Permission checks are UX-only in the frontend and **must be
  re-enforced server-side**.
