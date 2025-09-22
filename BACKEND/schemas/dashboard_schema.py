from pydantic import BaseModel
from typing import List

class UltimaResena(BaseModel):
    rating: int
    comment: str

class DashboardOut(BaseModel):
    total_ingresos: float
    trabajos_completados: int
    trabajos_en_progreso: int
    rating_promedio: float
    total_resenas: int
    ultimas_resenas: List[UltimaResena]