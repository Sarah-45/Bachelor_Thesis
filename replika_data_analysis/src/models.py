from typing import Literal

from pydantic import BaseModel


class PostRelevance(BaseModel):
    is_relevant: bool
    confidence: Literal["High", "Medium", "Low"]
