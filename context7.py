from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get('/')
def root():
    return {'status':'Context7 MCP Server Running'}

@app.get('/health')
def health():
    return JSONResponse(content={'healthy': True})

# MCP POST route
@app.post('/')
async def handle_post(request: Request):
    data = await request.json()
    # Claude MCP sirf status check karta hai, dummy response kaafi hai
    return JSONResponse(content={'status': 'ok'})
