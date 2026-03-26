from typing import List, Dict, Optional
from pydantic import BaseModel

class MatrixRequest(BaseModel):
    matrix: List[List[int]]

class RoutingRequest(BaseModel):
    routes: List[List[int]]  # List of machine sequences for parts

class FlowAnalysisRequest(BaseModel):
    matrix: List[List[int]]
    groups: Dict[int, int]  # machine index -> group id
    routing: Optional[List[List[int]]] = None
