from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class PortEnum(str, Enum):
    DURBAN = "Durban"
    CAPE_TOWN = "Cape_Town"
    RICHARDS_BAY = "Richards_Bay"
    NGQURA = "Ngqura"
    PORT_ELIZABETH = "Port_Elizabeth"
    SALDANHA = "Saldanha"
    EAST_LONDON = "East_London"
    MOSSEL_BAY = "Mossel_Bay"


class VesselRequest(BaseModel):
    port: PortEnum
    gt: float = Field(..., gt=0)
    loa: float = Field(..., gt=0)
    days_alongside: float = Field(..., gt=0)
    arrival: datetime
    departure: datetime
    operations: int = Field(..., ge=0)

    @field_validator("port", mode="before")
    def normalize_port(cls, v):
        # Convert spaces/apostrophes to underscores
        return str(v).replace(" ", "_").replace("'", "").strip()


class VesselResponse(BaseModel):
    light_dues: float
    port_dues: float
    towage_dues: float
    vts_dues: float
    pilotage_dues: float
    line_running_dues: float
    total: float
    explanation: Optional[str] = None


class NLQuery(BaseModel):
    query: str