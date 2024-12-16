import requests

from fastapi import APIRouter, HTTPException, status, Depends, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic.v1 import BaseModel
from sqlalchemy.orm import Session
from models.models import User  # Assuming the SQLAlchemy User model is in the models.py file
from core import security
import re
from core.confirm_registration import mail_verification_email
from schemas.schemas import UserAdd, UserLogin
from database import get_db
from starlette.responses import RedirectResponse
from pydantic import BaseModel

auth_router = APIRouter(tags=["auth"], prefix="/api/auth")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}



def is_valid_password(password: str) -> bool:
    regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(regex, password) is not None


@auth_router.get("/mail_verification/{email}")
def verify_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    user.status = True
    db.commit()
    db.refresh(user)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "You have successfully passed the verification"},
                        headers=headers)


class  UserSignUp(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str
    phone_number: str


@auth_router.post("/add-user")
def add_user(user_signup_data: UserSignUp,
             db: Session = Depends(get_db)):

    # if user_signup_data.password != user_signup_data.confirm_password:
    #     raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #                         detail="Incorrect password")
    #
    # if not is_valid_password(user_signup_data.password):
    #     raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #                     detail="Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character")

    user_hashed_password = security.hash_password(user_signup_data.password)


    if db.query(User).filter(User.email == user_signup_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already exists")

    # Insert user into database
    new_user = User(
        first_name=user_signup_data.first_name,
        last_name =user_signup_data. last_name,
        email=user_signup_data.email,
        password=user_hashed_password,
        phone_number=user_signup_data.phone_number,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    mail_verification_email(user_signup_data.email)

    # return FileResponse("C:\\Users\\Dell\\PycharmProjects\\Chat_project\\app\\templates\\auth.html")
    return "OK"



@auth_router.get("/get-one-user-by-id/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Error occurred while fetching user by id {user_id} ERROR: {error}')

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"User with id {user_id} was not found!")

    # Return the user data as a JSON response
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"user_id": user.user_id, "first_name": user.first_name, "last_name": user.last_name,
                                 "email": user.email,"phone_number": user.phone_number,"status": user.status},
                        headers=headers)



@auth_router.delete("/delete-user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    target_user = db.query(User).filter(User.user_id == user_id).first()

    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        db.delete(target_user)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Successfully deleted"}, headers=headers)


@auth_router.put("/update-user/{user_id}")
def update_user(user_id: int, first_name: str = Form(None), last_name: str = Form(None),
    email: str = Form(None), phone_number: str = Form(None), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if email:

        if db.query(User).filter(User.email == email, User.user_id != user_id).first():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email already exists",
            )
        user.email = email
    if phone_number:
        user.phone_number = phone_number

    try:
        db.commit()
        db.refresh(user)
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {error}",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "User updated successfully",
            "user": {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "status": user.status,
            },
        },
        headers=headers,
    )


@auth_router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user_email = login_data.email

    user = db.query(User).filter(User.email == user_email).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email '{user_email}' was not found!")

    if not user.status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You cannot log in because you have not completed authentication. Please check your email.")

    if not security.verify_password(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Wrong password")

    access_token = security.create_access_token({"user_id": user.user_id})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "Message": "Successfully logged in! Your access token",
                            "access_token": access_token,
                            "user_id": user.user_id
                        },
                        headers=headers)


@auth_router.get("/get_all_users")
def get_all_users(page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    per_page = 20

    count = db.query(User).count()

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content=[], headers=headers)

    max_page = (count - 1) // per_page + 1

    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    users = db.query(User.user_id, User.first_name, User.last_name, User.email, User.phone_number, User.status) \
              .limit(per_page) \
              .offset(offset) \
              .all()

    users_list = [
        {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "status": user.status,
        }
        for user in users
    ]

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "users": users_list,
                            "page": page,
                            "total_pages": max_page,
                            "total_users": count
                        },
                        headers=headers)
