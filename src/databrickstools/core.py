import logging
from typing import Optional

import fire

from .databricks import DatabricksDirectoryManager, DatabricksExporter, DatabricksImporter, DatabricksLangs
from .utils import pretty_print
from .settings import (
    DATABRICKSTOOLS_DATABRIKCS_TOKEN,
    DATABRICKSTOOLS_DEFAULT_LANGUAGE,
    DATABRICKSTOOLS_DEFAULT_FORMAT,
    DATABRICKSTOOLS_DATABRIKCS_URL,
    DATABRICKSTOOLS_LOG_LEVEL
)

logger = logging.getLogger(__name__)


class ImportingCLI:

    @staticmethod
    def _language_from_ending(filepath: str, fallback: str = DATABRICKSTOOLS_DEFAULT_LANGUAGE) -> str:
        if filepath.lower().endswith(".py"):
            return DatabricksLangs.PYTHON
        if filepath.lower().endswith(".scala") or filepath.lower().endswith(".sc"):
            return DatabricksLangs.SCALA
        return fallback

    @staticmethod
    def _file(from_path: str, to_path: str, import_method: str, base_language: str, overwrite: bool):
        logger.info(f"Importing file from {from_path} into Databricks ({to_path}).")
        importer = DatabricksImporter(
            databricks_url=DATABRICKSTOOLS_DATABRIKCS_URL,
            token=DATABRICKSTOOLS_DATABRIKCS_TOKEN,
            default_lang=DATABRICKSTOOLS_DEFAULT_LANGUAGE,
            default_overwrite=overwrite
        )
        import_function = getattr(importer, import_method)
        r = import_function(
            from_path=from_path,
            to_path=to_path,
            language=base_language.upper(),
            overwrite=overwrite
        )
        if r.ok:
            logger.info(f"SUCCESS: File {from_path} imported!")
        else:
            logger.warning(f"FAILURE: Importing {from_path} failed with message: {r.text}")

    def source(self, from_path: str, to_path: str, overwrite: bool = False,
               base_language: Optional[str] = None):
        base_language = base_language if base_language is not None else self._language_from_ending(from_path)
        return self._file(
            from_path=from_path,
            to_path=to_path,
            import_method="import_source",
            base_language=base_language,
            overwrite=overwrite
        )

    def markdown(self, from_path: str, to_path: str, overwrite: bool = False,
                 base_language: Optional[str] = None):
        base_language = base_language if base_language is not None else self._language_from_ending(from_path)
        return self._file(
            from_path=from_path,
            to_path=to_path,
            import_method="import_markdown",
            base_language=base_language,
            overwrite=overwrite
        )


class ExportingCLI:

    def __init__(self):
        self._exporter = DatabricksExporter(
            databricks_url=DATABRICKSTOOLS_DATABRIKCS_URL,
            token=DATABRICKSTOOLS_DATABRIKCS_TOKEN
        )

    def _file(self, from_path: str, to_path: str, export_method: str, **kwargs):
        export_function = getattr(self._exporter, export_method)
        r = export_function(from_path=from_path, to_path=to_path, **kwargs)
        if r.ok:
            logger.info(f"SUCCESS: File {to_path} exported!")
        else:
            logger.warning(f"FAILURE: Exporting {to_path} failed with message: {r.text}")

    def file(self, from_path: str, to_path: str, file_format: str = DATABRICKSTOOLS_DEFAULT_FORMAT):
        return self._file(from_path=from_path, to_path=to_path, export_method="export_file", file_format=file_format)

    def source(self, from_path: str, to_path: str):
        return self._file(from_path=from_path, to_path=to_path, export_method="export_source")

    def html(self, from_path: str, to_path: str):
        return self._file(from_path=from_path, to_path=to_path, export_method="export_html")

    def ipynb(self, from_path: str, to_path: str):
        return self._file(from_path=from_path, to_path=to_path, export_method="export_ipynb")


class Main:

    def __init__(self):
        self.upload = ImportingCLI()
        self.download = ExportingCLI()
        self._directory_manager = DatabricksDirectoryManager(
            databricks_url=DATABRICKSTOOLS_DATABRIKCS_URL,
            token=DATABRICKSTOOLS_DATABRIKCS_TOKEN
        )

    @pretty_print(logger)
    def ls(self, path: str):
        return self._directory_manager.ls(path)

    def mkdir(self, path: str):
        self._directory_manager.mkdirs(path)


def main():
    logging.basicConfig(level=DATABRICKSTOOLS_LOG_LEVEL)
    fire.Fire(Main)


if __name__ == "__main__":
    main()
