from pydantic import BaseModel
from typing import List


class ArchitectureTrainingSample(BaseModel):
    domain: str
    scale: str
    users: int
    compliance: int
    budget: int
    pattern: str
    components: List[str]
    risk_score: float
