
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth import (
    fake_users_db, get_password_hash, verify_password, 
    create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import UserCreate, Token, AllocationRequest, AllocationResponse, TelemetryData
from hardware import engine
from utils import collector
from datetime import timedelta

router = APIRouter()

# --- Auth Endpoints ---
@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pw = get_password_hash(user.password)
    fake_users_db[user.username] = {"username": user.username, "hashed_password": hashed_pw}
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ CORRECTED LOGIN ENDPOINT
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Uses FastAPI's built-in OAuth2 form handler. 
    Do NOT use = Depends() with Pydantic models here.
    """
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Compute Endpoints ---
@router.post("/allocate", response_model=AllocationResponse)
async def allocate_resources(
    request: AllocationRequest, # ✅ Pydantic model passed directly (No Depends)
    current_user: dict = Depends(get_current_user) # ✅ Function passed to Depends
):
    # 1. Synthesize Virtual Cores based on user request
    v_cores = engine.synthesize_virtual_cores(request.compute_percent)
    
    # 2. Provision Docker Container
    try:
        container_id = engine.provision_container(v_cores, request.rom_percent)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # 3. Start Telemetry Collection
    collector.start_monitoring(container_id)

    return AllocationResponse(
        status="success",
        container_id=container_id[:12],
        virtual_cores_allocated=v_cores,
        message=f"Allocated {v_cores} virtual cores for user {current_user['username']}"
    )

@router.get("/telemetry/{container_id}", response_model=TelemetryData)
async def get_telemetry(container_id: str, current_user: dict = Depends(get_current_user)):
    return collector.get_telemetry(container_id, engine.docker_client)

@router.get("/system-health")
async def system_health():
    density = engine.get_cluster_density()
    return {
        "status": "operational",
        "cluster_density": density,
        "active_monitors": len(collector.active_monitors)
                }
