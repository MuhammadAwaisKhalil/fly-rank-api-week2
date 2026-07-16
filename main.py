from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
#Stage 1

@app.get('/')
def api_desc():
    return {"name":"Task API",
            "version":1.0,
            "endpoints":["/tasks"]}



@app.get('/health')
def get_health():
    return {"status":"ok"}

tasks = [{"id":100, "title":"Reading","Done":False},
         {"id":101, "title":"Coding","Done":True},
         {"id":102, "title":"Writing","Done":False}]

@app.get('/tasks')
def get_all_tasks():
    return tasks

@app.get('/tasks/{id}')
def get_specific_task(id: int):
    for task in tasks:
        if task['id']==id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error":"Task {id} not found!"}
    )
