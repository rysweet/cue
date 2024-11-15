from typing import List, TYPE_CHECKING
from hashlib import md5
import os

if TYPE_CHECKING:
    from graph.relationship import Relationship
    from graph.node import NodeLabels


class Node:
    label: "NodeLabels"
    path: str
    name: str
    level: int
    parent: "Node"

    def __init__(self, label: "NodeLabels", path: str, name: str, level: int, parent: "Node" = None):
        self.label = label
        self.path = path
        self.name = name
        self.level = level
        self.parent = parent

        if not self.is_path_format_valid():
            raise ValueError(f"Path format is not valid: {self.path}")

    def is_path_format_valid(self) -> bool:
        return self.path.startswith("file://")

    @staticmethod
    def hash_path_to_id(path: str) -> str:
        return md5(path.encode()).hexdigest()

    @property
    def id(self) -> str:
        return self.__str__()

    @property
    def hashed_id(self) -> str:
        return md5(self.id.encode()).hexdigest()

    @property
    def node_repr_for_identifier(self) -> str:
        return "." + self.name

    @property
    def pure_path(self) -> str:
        return self.path.replace("file://", "")

    @property
    def extension(self) -> str:
        return os.path.splitext(self.pure_path)[1]

    def as_object(self) -> dict:
        return {
            "type": self.label.name,
            "attributes": {
                "label": self.label.name,
                "path": self.path,
                "node_id": self.hashed_id,
                "node_path": self.id,
                "name": self.name,
                "level": self.level,
                "hashed_id": self.hashed_id,
            },
        }

    def get_relationships(self) -> List["Relationship"]:
        return []

    def __str__(self) -> str:
        identifier = ""

        if self.parent:
            identifier += self.parent.id
        identifier += self.node_repr_for_identifier

        return identifier
