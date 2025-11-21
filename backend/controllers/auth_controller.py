"""Authentication controller for login and registration endpoints."""
from fastapi import APIRouter, HTTPException, status
from dtos.auth_dto import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest) -> RegisterResponse:
    """
    Register a new user.
    
    Args:
        request: Registration data (email, password, full_name)
        
    Returns:
        RegisterResponse: Created user information
        
    Raises:
        HTTPException 400: If email already exists or validation fails
    """
    try:
        user = await AuthService.register_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        
        return RegisterResponse(
            id=user.id,
            email=user.email,
            name=user.full_name,
            role=user.role.value
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """
    Authenticate a user and return user information.
    
    NextAuth.js on the frontend will handle creating the JWT session.
    This endpoint just validates credentials and returns user info.
    
    IMPORTANT: Do NOT return a token here. NextAuth handles token creation.
    The token will be sent as an HTTP-only cookie automatically.
    
    Args:
        request: Login credentials (email and password)
        
    Returns:
        LoginResponse: User information if authentication succeeds
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    user = await AuthService.authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return LoginResponse(
        id=user.id,
        email=user.email,
        name=user.full_name,
        role=user.role.value
    )

