import base64
import logging
import os
from typing import Optional

import requests

from .markdown import MarkdownFile
from .settings import (
    DATABRICKSTOOLS_DEFAULT_FORMAT,
    DATABRICKSTOOLS_DEFAULT_LANGUAGE,
    DATABRICKSTOOLS_DEFAULT_OVERWRITE_FLAG
)

logger = logging.getLogger(__name__)


class DatabricksLangs:
    PYTHON = "PYTHON"
    SCALA = "SCALA"
    SQL = "SQL"


class DatabricksFormats:
    SOURCE = "SOURCE"
    JUPYTER = "JUPYTER"
    HTML = "HTML"


class DatabricksEndpoint:
    endpoint = ""

    def __init__(self, databricks_url: str, token: str):
        self.databricks_url = databricks_url
        self.token = token

    @property
    def headers(self):
        return {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}"
            }

    @property
    def api_url(self):
        if not self.endpoint:
            raise ValueError("Missing 'endpoint' implementation.")
        databricks_url = self.databricks_url if self.databricks_url.replace("/", "").endswith("api") \
            else os.path.join(self.databricks_url, "api")
        return os.path.join(databricks_url, self.endpoint)

    def _payload(self, *args, **kwargs):
        pass


class DatabricksDirectoryManager:

    class DatabricksList(DatabricksEndpoint):
        endpoint = "2.0/workspace/list"

        def _payload(self, path: str):
            return {
                "path": path
            }

        def ls(self, path: str):
            response = requests.get(
                url=self.api_url,
                headers=self.headers,
                params=self._payload(path=path)
            )
            if not response.ok:
                raise ValueError(f"List operation failed due to: {response.text}")
            notebooks = response.json()["objects"]
            return notebooks

    class DatabricksMkdirs(DatabricksEndpoint):
        endpoint = "2.0/workspace/mkdirs"

        def _payload(self, path: str):
            return {
                "path": path
            }

        def mkdirs(self, path: str):
            response = requests.post(
                url=self.api_url,
                headers=self.headers,
                json=self._payload(path=path)
            )
            if not response.ok:
                raise ValueError(f"Mkdirs operation failed due to: {response.text}")
            return response

    def __init__(self, databricks_url: str, token: str):
        self.databricks_url = databricks_url
        self.token = token
        self.endpoint_list = self.DatabricksList(
            databricks_url=databricks_url,
            token=token
        )
        self.endpoint_mkdirs = self.DatabricksMkdirs(
            databricks_url=databricks_url,
            token=token
        )

    def ls(self, path: str):
        return self.endpoint_list.ls(path=path)

    def mkdirs(self, path: str):
        return self.endpoint_mkdirs.mkdirs(path=path)


class DatabricksImporter(DatabricksEndpoint):
    endpoint = "2.0/workspace/import"

    def __init__(self, databricks_url: str, token: str,
                 default_lang: str = DATABRICKSTOOLS_DEFAULT_LANGUAGE,
                 default_overwrite: bool = DATABRICKSTOOLS_DEFAULT_OVERWRITE_FLAG):
        self.default_overwrite = default_overwrite
        self.default_lang = default_lang
        super().__init__(databricks_url=databricks_url, token=token)

    def _payload(self, content: str, path: str, language: str, overwrite: bool):
        return {
            "content": str(base64.b64encode(bytes(content, "utf-8")))[2:-1],
            "format": DatabricksFormats.SOURCE,
            "path": path,
            "language": language,
            "overwrite": overwrite
        }

    def _import_file(self, source: str, to_path: str,
                     language: Optional[str] = None, overwrite: Optional[bool] = None):
        lang = language if language is not None else self.default_lang
        overwrite = overwrite if overwrite is not None else self.default_overwrite
        return requests.post(
            url=self.api_url,
            headers=self.headers,
            json=self._payload(
                content=source,
                path=to_path,
                language=lang,
                overwrite=overwrite
            )
        )

    def import_markdown(self, from_path: str, to_path: str,
                        language: Optional[str] = None, overwrite: Optional[bool] = None):
        lang = language if language is not None else self.default_lang
        source = MarkdownFile.from_file(path=from_path).databricks_source_content(global_lang=lang.lower())
        return self._import_file(
            source=source,
            to_path=to_path,
            language=language,
            overwrite=overwrite
        )

    def import_source(self, from_path: str, to_path: str,
                      language: Optional[str] = None, overwrite: Optional[bool] = None):
        with open(from_path, "r") as file:
            source = file.read()
        return self._import_file(
            source=source,
            to_path=to_path,
            language=language,
            overwrite=overwrite
        )


class DatabricksExporter(DatabricksEndpoint):
    endpoint = "2.0/workspace/export"

    def __init__(self, databricks_url: str, token: str, default_file_format: str = DATABRICKSTOOLS_DEFAULT_FORMAT):
        self.default_file_format = default_file_format
        super().__init__(databricks_url=databricks_url, token=token)

    def _payload(self, path: str, file_format: str):
        return {
            "path": path,
            "format": file_format
        }

    def export_file(self, from_path: str, to_path: str, file_format: Optional[str] = None):
        file_format = file_format if file_format is not None else self.default_file_format
        response = requests.get(
            url=self.api_url,
            headers=self.headers,
            params=self._payload(path=from_path, file_format=file_format)
        )
        if not response.ok:
            raise ValueError(f"Failure when fetching the file: {response.content}")
        content = base64.b64decode(response.json()["content"]).decode("utf-8")
        with open(to_path, "w") as file:
            file.write(content)
        return response

    def export_source(self, from_path: str, to_path: str):
        if not any([to_path.endswith(".py"), to_path.endswith(".sc")]):
            raise ValueError("The 'to_path' value must contain a valid ending (.py for python or .sc for scala).")
        return self.export_file(from_path=from_path, to_path=to_path, file_format=DatabricksFormats.SOURCE)

    def export_html(self, from_path: str, to_path: str):
        if not to_path.endswith(".html"):
            raise ValueError("The 'to_path' value must end with '.html'.")
        return self.export_file(from_path=from_path, to_path=to_path, file_format=DatabricksFormats.HTML)

    def export_ipynb(self, from_path: str, to_path: str):
        if not to_path.endswith(".ipynb"):
            raise ValueError("The 'to_path' value must end with '.ipynb'.")
        return self.export_file(from_path=from_path, to_path=to_path, file_format=DatabricksFormats.JUPYTER)
