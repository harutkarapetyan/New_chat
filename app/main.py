# FastAPI
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from core.security import get_current_user

template = Jinja2Templates(directory="templates")
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/auth/login")

# Database and models
from database import engine, check_connection
from models.models import Base


# Routers
from api.auth.auth import auth_router
from api.auth.forgot_password import forgot_router
from api.endpoints.chat import chat_router


Base.metadata.create_all(bind=engine)
check_connection()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name='static')
# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],
)


response_headers = {
    "Access-Control-Allow-Origin": "*",  # Allow all origins, or replace with specific domains
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",  # Specify allowed methods
    "Access-Control-Allow-Headers": "Authorization, Content-Type",  # Specify allowed custom headers
    "Access-Control-Allow-Credentials": "true",  # Allow credentials if needed
}


@app.get("/")
def get_welcome():
    return "WELCOME"


@app.get("/home")
async def get(request: Request,token = Depends(get_current_user)):
    return template.TemplateResponse("index.html", {"request": request})


@app.get("/signup-page")
def get_signup_page(request: Request):
    return template.TemplateResponse("signup.html", {"request": request})


@app.get("/signin-page")
def get_signin_page(request: Request):
    return template.TemplateResponse("auth.html", {"request": request})


@app.get("/home-page")
def get_home_page(request: Request):
    return template.TemplateResponse("index.html", {"request": request})

@app.get("/selection-page")
def get_selection_page(request: Request):
    return template.TemplateResponse("chat_selection.html", {"request": request})

@app.get("/ws/one-to-one/{user_id}")
def get_one_to_one_page(request: Request, user_id: int):
    return template.TemplateResponse("one_to_one_chat.html", {"request": request})

app.include_router(auth_router)
app.include_router(forgot_router)
app.include_router(chat_router)