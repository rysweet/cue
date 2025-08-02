from typing import List, Dict, Any

class RelationshipMarker:
    @staticmethod
    def replace_all(nodes_as_objects: List[Dict[str, Any]]) -> None:
        node_names = RelationshipMarker.__get_all_node_names(nodes_as_objects)
        for node in nodes_as_objects:
            for name in node_names:
                if not node.get("attributes") or not node.get("attributes").get("text"):
                    print("Node does not have attributes or text")
                    continue
                import re

                pattern = rf"\b{name}\b(?=\s*\(|\s*\.|\s*:)"

                node["attributes"]["text"] = re.sub(pattern, f"<<<{name}>>>", node["attributes"]["text"])

    @staticmethod
    def __get_all_node_names(nodes_as_objects: List[Dict[str, Any]]) -> List[str]:
        return [node["attributes"]["name"] for node in nodes_as_objects]
