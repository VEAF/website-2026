from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nickname: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    pass  # Refresh token is in HttpOnly cookie


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    token: str
    password: str
