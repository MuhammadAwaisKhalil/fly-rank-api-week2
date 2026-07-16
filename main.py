from fastapi import FastAPI

app = FastAPI()
#Stage 0
@app.get('/')
async def root():
    return {'message':"Hello World!!!!"}

#STage 1

@app.get('/')
def api_desc():
    return {"name":"Task API",
            "version":1.0,
            "endpoints":["/tasks"]}

@app.get('/health')
def get_health():
    return {"status":"ok"}

