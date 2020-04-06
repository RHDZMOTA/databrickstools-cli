import logging
from typing import List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

block_initializer_pattern = {
    "md": {
        "```scala": "scala",
        "```tut": "scala",
        "```py": "python",
        "```sh": "sh",
        "```sql": "sql"
    },
    "rmd": {
        "```tut": "scala",
        "```{py": "python",
        "```{sh": "sh",
        "```{bash": "sh",
        "```{sql": "sql"
    },
}

block_comment_pattern = {
    "scala": "//",
    "tut": "//",
    "python": "#",
    "sh": "#",
    "md": "#",
    "sql": "--"
}


@dataclass
class Line:
    number: int
    content: str


class Block:

    def __init__(self, lang: str, lines: Optional[List[Line]] = None):
        self.lang = lang
        self.lines = [] if not lines else lines

    @property
    def comment_pattern(self):
        return block_comment_pattern[self.lang]

    @property
    def content(self) -> str:
        content = "\n".join(line.content for line in self.lines)
        return content

    def as_databricks_block(self, global_lang_comment) -> str:
        return "\n".join(
            [
                f"{global_lang_comment} COMMAND ----------",
                "",
                f"{global_lang_comment} MAGIC %{self.lang}",
                "".join([f"{global_lang_comment} MAGIC {line.content}" for line in self.lines]),
                ""
            ]
        )

    @property
    def is_empty(self) -> bool:
        zero_lines = len(self.lines) == 0
        empty_lines = len([line for line in self.lines if line.content.strip()]) == 0
        return zero_lines or empty_lines

    def __repr__(self) -> str:
        return self.content

    def append(self, line: Line) -> 'Block':
        self.lines.append(line)
        return self


class MarkdownFile:

    def __init__(self, blocks: List[Block], raw: Optional[str] = None):
        self.blocks = blocks
        self.raw = raw

    @property
    def n_blocks(self) -> int:
        return len(self.blocks)

    def databricks_source_content(self, global_lang: str) -> str:
        return "\n".join(
            [
                f"{block_comment_pattern[global_lang]} Databricks notebook source",
                *[block.as_databricks_block(block_comment_pattern[global_lang]) for block in self.blocks]
            ]
        )

    @staticmethod
    def from_file(path: str, starting_lang: str = "md") -> 'MarkdownFile':
        file_ending = path.lower().split(".")[-1]  # TODO: Fallback to DATABRICKSTOOLS_DEFAULT_FILE_ENDING
        blocks = [Block(lang=starting_lang)]
        with open(path, "r") as file:
            lines = file.readlines()
            content = file.read()
        for i, line in enumerate(lines):
            n_blocks = len(blocks)
            for pattern, lang in block_initializer_pattern[file_ending].items():
                if line.startswith(pattern):
                    blocks.append(Block(lang=lang))
                    break
            new_block_added = len(blocks) > n_blocks
            if new_block_added:
                continue
            if line.strip() == "```" and blocks[-1].lang != "md":
                blocks.append(Block(lang="md"))
                continue
            blocks[-1].append(Line(number=i, content=line))
        return MarkdownFile(blocks=[block for block in blocks if not block.is_empty], raw=content)
