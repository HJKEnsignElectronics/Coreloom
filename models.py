# models.py
from pydantic import BaseModel, Field
from typing import Optional, List

# --- Auth Models ---
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- Allocation Models ---
class AllocationRequest(BaseModel):
    rom_percent: float = Field(..., ge=0, le=100, description="Requested ROM/Storage %")
    compute_percent: float = Field(..., ge=0, le=100, description="Requested Energy/Compute %")
    task_description: Optional[str] = "Default CoreLoom Task"

class AllocationResponse(BaseModel):
    status: str
    container_id: str
    virtual_cores_allocated: int
    message: str

# --- Telemetry Models ---
class TelemetryData(BaseModel):
    container_id: str
    cpu_usage: float
    memory_usage: float
    thread_speed_mhz: float
    status: str
