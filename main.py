from fastapi import FastAPI, status, Body
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

#Stage 2
# @app.get('/tasks')
# def get_all_tasks():
#     return tasks

# @app.get('/tasks/{id}')
# def get_specific_task(id: int):
#     for task in tasks:
#         if task['id']==id:
#             return task
#     return JSONResponse(
#         status_code=404,
#         content={"error":"Task {id} not found!"}
#     )

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

