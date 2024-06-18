from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse, Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils.http_error_handler import http_error_handler

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates  
from obtainData import filtrar_y_obtener_por_track_name    
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(http_error_handler)
@app.middleware("http")
async def HTTP_error_handler(request: Request, call_next) -> Response | JSONResponse:
    try:
        return await call_next(request)
    except Exception as e:
        content = f"exc: {str(e)}"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(content=content, status_code=status_code)


static_path = os.path.join(os.path.dirname(__file__), 'static/')
templates_path = os.path.join(os.path.dirname(__file__), 'templates/')

app.mount('/static',StaticFiles(directory=static_path),'static')
templates = Jinja2Templates(directory=templates_path)

app.title = "BD2 API"

app.version = "1.0.0"

@app.get("/", tags=['Home'])
def home(request: Request): 
    return templates.TemplateResponse('index.html', {'request': request,'message': 'Welcome'})


@app.get("/test", tags=['Home'])
def home():
    return HTMLResponse('<h1>Hello World</h1>')

@app.get('/get_file', tags=['Home'])   
def get_files():
    return FileResponse('file.txt') 

@app.get('/dataId', tags=['Spotify'])
def get_data(search: str):
    results_json = filtrar_y_obtener_por_track_name(search)
    results_list = json.loads(results_json)
    
    if results_list:
        return results_list[0]
    else:
        return {"message": "No se encontraron resultados"}

