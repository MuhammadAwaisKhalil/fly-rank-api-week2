from fastapi import FastAPI, status, Body
from fastapi.responses import JSONResponse
import sqlite3

app = FastAPI()

def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def setup_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   done BOOLEAN NOT NULL DEFAULT 0)
                   """)
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("INSERT INTO tasks(title, done) VALUES ('Reading', 0)")
        cursor.execute("INSERT INTO tasks(title, done) VALUES ('Coding', 1)")
        cursor.execute("INSERT INTO tasks(title, done) VALUES ('Writing', 0)")
    conn.commit()
    conn.close()


@app.get('/')
def api_desc():
    return {"name":"Task API",
            "version":1.0,
            "endpoints":["/tasks"]}



@app.get('/health')
def get_health():
    return {"status":"ok"}

# tasks = [{"id":100, "title":"Reading","Done":False},
#          {"id":101, "title":"Coding","Done":True},
#          {"id":102, "title":"Writing","Done":False}]


@app.get('/tasks')
def get_all_tasks():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tasks')
    rows = cursor.fetchall()

    tasks=[]
    for row in rows:
        tasks.append({
            "id":row["id"],
            "title":row["title"],
            "done":bool(row["done"])
        })
    return tasks

@app.get('/tasks/{id}')
def get_specific_task(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", id)

    row = cursor.fetchone()
    conn.commit()

    conn.close()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error":"Task {id} not found!"}
        )
    return {"id":row["id"],
            "title":row["title"],
            "done":bool(row["done"])}


@app.post("/tasks")
def add_new_task(title:str, done:bool):
    

    if not title or title.strip()=='':
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error':'title is missing'}
        )
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks(title, done) VALUES(?, ?)",(title, done))
    conn.commit()
    conn.close()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"title":title,"done":done}
    )

@app.put('/tasks/{id}')
def update_task(id: int, task: dict = Body(default={})):
    
    if "title" not in task and "done" not in task:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error': "Must provide a 'title' or 'done' status"}
        )
    
    if "title" in task and (task["title"] is None or str(task["title"]).strip() == ""):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error': "Task cannot be empty"}
        )
    
    conn = get_db()
    cursor = conn.cursor()

    
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    existing_task = cursor.fetchone()
    
    if existing_task is None:
        conn.close()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'error': f'Task {id} not found'}
        )

    
    if "title" in task and "done" in task:
        cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (task["title"], task["done"], id))
    elif "title" in task:
        cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (task["title"], id))
    elif "done" in task:
        cursor.execute("UPDATE tasks SET done = ? WHERE id = ?", (task["done"], id))
    
    
    conn.commit()

   
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (id,))
    updated_row = cursor.fetchone()
    conn.close()

    
    return {
        "id": updated_row["id"],
        "title": updated_row["title"],
        "done": bool(updated_row["done"])
    }


@app.delete('/tasks/{id}')
def delete_task(id:int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?",id)

    row = cursor.fetchone()
    if row is None:
        conn.close()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'error':f'Task {id} not found'}
        )
    cursor.execute("DELETE FROM tasks WHERE id = ?",id)
    conn.commit()
    conn.close()
    return
