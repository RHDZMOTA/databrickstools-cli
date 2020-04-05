import logging
import os


logger = logging.getLogger(__name__)

DATABRICKSTOOLS_DATABRIKCS_URL = os.environ.get(
    "DATABRICKSTOOLS_DATABRIKCS_URL"
)

if DATABRICKSTOOLS_DATABRIKCS_URL is None:
    raise ValueError("Missing environment variable: DATABRICKSTOOLS_DATABRIKCS_URL")

DATABRICKSTOOLS_DATABRIKCS_TOKEN = os.environ.get(
    "DATABRICKSTOOLS_DATABRIKCS_TOKEN"
)

if DATABRICKSTOOLS_DATABRIKCS_TOKEN is None:
    raise ValueError("Missing environment variable: DATABRICKSTOOLS_DATABRIKCS_TOKEN")

DATABRICKSTOOLS_LOG_LEVEL = os.environ.get(
    "DATABRICKSTOOLS_LOG_LEVEL",
    default=logging.INFO
)

DATABRICKSTOOLS_DEFAULT_LANGUAGE = os.environ.get(
    "DATABRICKSTOOLS_DEFAULT_LANGUAGE",
    default="PYTHON"
).upper()

DATABRICKSTOOLS_DEFAULT_OVERWRITE_FLAG = os.environ.get(
    "DATABRICKSTOOLS_DEFAULT_OVERWRITE_FLAG",
    default="TRUE"
).upper().startswith("T")


DATABRICKSTOOLS_DEFAULT_FORMAT = os.environ.get(
    "DATABRICKSTOOLS_DEFAULT_FORMAT",
    default="SOURCE"
).upper()
