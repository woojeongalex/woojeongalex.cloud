from pydantic import BaseModel


class SiliconValleyResponse(BaseModel):
    id: int
    name: str
    role: str = ""
    description: str = ""
    ability: str = ""
