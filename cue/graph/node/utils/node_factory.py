from typing import Optional, Union, TYPE_CHECKING
from uuid import uuid4

from cue.graph.node.class_node import ClassNode
from cue.graph.node.deleted_node import DeletedNode
from cue.graph.node.file_node import FileNode
from cue.graph.node.folder_node import FolderNode
from cue.graph.node.function_node import FunctionNode
from cue.graph.node.types.node_labels import NodeLabels

if TYPE_CHECKING:
    from cue.project_file_explorer import Folder
    from cue.graph.graph_environment import GraphEnvironment
    from cue.code_references.types import Reference
    from tree_sitter import Node as TreeSitterNode
    from cue.graph.node.types.definition_node import DefinitionNode


class NodeFactory:
    @staticmethod
    def create_folder_node(
        folder: "Folder", parent: Optional[FolderNode] = None, graph_environment: Optional["GraphEnvironment"] = None
    ) -> FolderNode:
        return FolderNode(
            path=folder.uri_path,
            name=folder.name,
            level=folder.level,
            parent=parent,
            graph_environment=graph_environment,
        )

    @staticmethod
    def create_file_node(
        path: str,
        name: str,
        level: int,
        node_range: "Reference",
        definition_range: "Reference",
        code_text: str,
        parent: Optional[FolderNode],
        tree_sitter_node: "TreeSitterNode",
        body_node: Optional["TreeSitterNode"] = None,
        graph_environment: Optional["GraphEnvironment"] = None,
    ) -> FileNode:
        return FileNode(
            path=path,
            name=name,
            level=level,
            node_range=node_range,
            definition_range=definition_range,
            code_text=code_text,
            parent=parent,
            body_node=body_node,
            tree_sitter_node=tree_sitter_node,
            graph_environment=graph_environment,
        )

    @staticmethod
    def create_class_node(
        class_name: str,
        path: str,
        definition_range: "Reference",
        node_range: "Reference",
        code_text: str,
        body_node: Optional["TreeSitterNode"],
        level: int,
        tree_sitter_node: "TreeSitterNode",
        parent: Optional[Union["DefinitionNode", FileNode, ClassNode, FunctionNode]] = None,
        graph_environment: Optional["GraphEnvironment"] = None,
    ) -> ClassNode:
        return ClassNode(
            name=class_name,
            path=path,
            definition_range=definition_range,
            node_range=node_range,
            code_text=code_text,
            level=level,
            tree_sitter_node=tree_sitter_node,
            body_node=body_node,
            parent=parent,
            graph_environment=graph_environment,
        )

    @staticmethod
    def create_function_node(
        function_name: str,
        path: str,
        definition_range: "Reference",
        node_range: "Reference",
        code_text: str,
        body_node: Optional["TreeSitterNode"],
        level: int,
        tree_sitter_node: "TreeSitterNode",
        parent: Optional[Union["DefinitionNode", FileNode, ClassNode, FunctionNode]] = None,
        graph_environment: Optional["GraphEnvironment"] = None,
    ) -> FunctionNode:
        return FunctionNode(
            name=function_name,
            path=path,
            definition_range=definition_range,
            node_range=node_range,
            code_text=code_text,
            level=level,
            tree_sitter_node=tree_sitter_node,
            body_node=body_node,
            parent=parent,
            graph_environment=graph_environment,
        )

    @staticmethod
    def create_node_based_on_label(
        kind: NodeLabels,
        name: str,
        path: str,
        definition_range: "Reference",
        node_range: "Reference",
        code_text: str,
        body_node: Optional["TreeSitterNode"],
        level: int,
        tree_sitter_node: "TreeSitterNode",
        parent: Optional[Union["DefinitionNode", FileNode, ClassNode, FunctionNode]] = None,
        graph_environment: Optional["GraphEnvironment"] = None,
    ) -> Union[ClassNode, FunctionNode]:
        if kind == NodeLabels.CLASS:
            return NodeFactory.create_class_node(
                class_name=name,
                path=path,
                definition_range=definition_range,
                node_range=node_range,
                code_text=code_text,
                body_node=body_node,
                level=level,
                parent=parent,
                tree_sitter_node=tree_sitter_node,
                graph_environment=graph_environment,
            )
        elif kind == NodeLabels.FUNCTION:
            return NodeFactory.create_function_node(
                function_name=name,
                path=path,
                definition_range=definition_range,
                node_range=node_range,
                code_text=code_text,
                body_node=body_node,
                level=level,
                parent=parent,
                tree_sitter_node=tree_sitter_node,
                graph_environment=graph_environment,
            )
        else:
            raise ValueError(f"Kind {kind} is not supported")

    @staticmethod
    def create_deleted_node(
        graph_environment: Optional["GraphEnvironment"] = None,
    ) -> DeletedNode:
        if graph_environment is None:
            path = f"file:///DELETED-{str(uuid4())}"
        else:
            path = f"file://{graph_environment.root_path}/DELETED-{str(uuid4())}"
        
        return DeletedNode(
            label=NodeLabels.DELETED,
            path=path,
            name="DELETED",
            level=0,
            graph_environment=graph_environment,
        )
