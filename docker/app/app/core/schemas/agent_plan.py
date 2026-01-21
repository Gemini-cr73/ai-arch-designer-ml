from pydantic import BaseModel


class ComponentSpec(BaseModel):
    name: str
    role: str
    technologies: list[str]


class AgentArchitecturePlan(BaseModel):
    components: list[ComponentSpec]
    deployment: str
    scaling: str
    security: list[str]
