"""Small data models shared by the Aegis application."""

from dataclasses import dataclass
from typing import Literal


Visibility = Literal["public", "internal", "restricted"]
DocumentStatus = Literal["active", "superseded"]


@dataclass(frozen=True)
class Question:
    text: str
    user_id: str


@dataclass(frozen=True)
class Answer:
    text: str
    sources: tuple[str, ...] = ()
    warning: str | None = None
