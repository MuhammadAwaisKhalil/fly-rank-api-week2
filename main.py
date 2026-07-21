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
    cursor.close()


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
def add_new_task(task: dict= Body(default={})):
    title = task.get('title')

    if not title or title.strip()=='':
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error':'title is missing'}
        )
    
    next_id = max((t['id'] for t in tasks), default=0)+1
    new_task = {
        'id':next_id,
        'title':title,
        'Done':False
    }
    tasks.append(new_task)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=new_task
    )

@app.put('/tasks/{id}')
def update_task(id:int, task:dict=Body(default={})):
    if "title" not in task and "Done" not in task:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error':'Must provide a \'title\' or \'Done\' status'}
        )
    
    if "title" in task and (task["title"] is None or str(task["title"]).strip() == ""):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error':'Task cannot be empty'}
        )
    
    for t in tasks:
        if t['id']==id:
            if "title" in task:
                t['title']=task['title']
            if "Done" in task:
                t['Done']=task['Done']
            
            return t
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'error':f'Task {id} not found'}
    )

@app.delete('/tasks/{id}')
def delete_task(id:int):
    for task in tasks:
        if task['id']==id:
            tasks.remove(task)

            return
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'error':f'Task {id} not found'}
    )
