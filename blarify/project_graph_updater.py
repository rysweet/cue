from dataclasses import dataclass
from blarify.project_graph_diff_creator import ProjectGraphDiffCreator, FileDiff, ChangeType
from typing import List
from blarify.graph.graph_update import GraphUpdate

from blarify.graph.graph_environment import GraphEnvironment


@dataclass
class UpdatedFile:
    path: str


class ProjectGraphUpdater(ProjectGraphDiffCreator):
    updated_files: List[UpdatedFile]

    def __init__(self, updated_files: List[UpdatedFile], graph_environment: GraphEnvironment, *args, **kwargs):
        """
        This class is just a wrapper around ProjectGraphDiffCreator

        All the updated files are considered as added files and the pr_environment is set to the same as the graph_environment
        """

        self.updated_files = updated_files
        super().__init__(
            file_diffs=self.get_file_diffs_from_updated_files(),
            graph_environment=graph_environment,
            pr_environment=graph_environment,
            *args,
            **kwargs,
        )

    def build(self) -> GraphUpdate:
        self.create_code_hierarchy()
        self.create_relationship_from_references_for_modified_and_added_files()
        self.keep_only_files_to_create()

        return GraphUpdate(
            graph=self.graph,
            external_relationship_store=self.external_relationship_store,
        )

    def get_file_diffs_from_updated_files(self) -> List[FileDiff]:
        return [
            FileDiff(path=updated_file.path, diff_text="", change_type=ChangeType.ADDED)
            for updated_file in self.updated_files
        ]
