from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId

from database.databaseMongo import user_collection
from schemas.user_schemas import UserCreate, UserOut
from schemas.token_schema import Token
from utils.security import hash_password, verify_password
from utils.auth_service import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "firstName": user["firstName"],
        "lastName": user["lastName"],
        "role": user["role"],
    }

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def register_user(user_data: UserCreate):
    existing_user = await user_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado.")
    
    user_data.password = hash_password(user_data.password)
    new_user_dict = user_data.model_dump()
    
    result = await user_collection.insert_one(new_user_dict)
    created_user = await user_collection.find_one({"_id": result.inserted_id})
    
    return user_helper(created_user)

@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Credenciales incorrectas")
    
    access_token = create_access_token(data={"user_id": str(user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}