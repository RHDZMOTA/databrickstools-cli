# DatabricksTools CLI

A simple commandline application to keep in sync between databricks and your local filesystem. This project uses the databricks [workspace api](https://docs.databricks.com/dev-tools/api/latest/workspace.html). 
 
Key features:
* List and MkDir commands. 
* Download databricks notebooks as HTML, Jupyter, or Source format. 
* Upload file from your filesystem (source format) to create/overwrite databricks notebooks. 
* Automatically transform markdown files to source!
    * Using markdown syntax instead of source is more convenient. 
    * Use codeblocks to change between languages (e.g. `python`, `scala`, `sql`, `sh`). 
    * Integrate local development and execution with databricks notebooks. 

```commandline
$ databrickstools ls --path /Shared
```

```commandline
$ databrickstools upload markdown \
    --from-path exploration.md \
    --to-path /Shared/merchants/exploration
```

## Setup

Clone the repository and install the commandline application!

1. Clone: `git clone https://github.com/rhdzmota/databrickstools-cli`
1. Install: `pip install -e databrickstools-cli`

**Note**: you'll need python 3.6 or greater. 

Create the `.env` file containing your environment variables.

1. Create `.env` following the example `.env.example`:
    * `cp .env.example .env`
1. Load the variables into the environment:
    *  `export $(cat .env | xargs)`

**Note**: the `.env` file can be on any place of your machine. The commandline application just needs those variables to be present on the environment. 

Test with a simple command:

```commandline
$ databrickstools ls --path /Shared
```

## Use case!

Assume you have a file named `exploration.md` with the following markdown content:

````text
# Exporatory Data Analysis

This is a file containing the initial EDA work.

## Setup

```python
import pandas as pd
from sqlalchemy import create_engine 

connection_string = "..."
engine = create_engine(connection_string) 
```

## Getting the data

Consider the following invalid merchant data:

```python
SQL_INVALID_MERCHANTS = "SELECT * FROM merchants WHERE invalid = 1"

df = pd.read_sql(query, engine)
df.head()
```

Location distribution: 

```python
df.groupby("state").size().to_frame()
```
...

````

You could use [rmarkdown + reticulate](https://rstudio.github.io/reticulate/articles/r_markdown.html) for local development and execution of that report. And then use `databrickstools` to deploy and transform this markdown file into a databricks notebook! 

```commandline
$ databrickstools upload markdown \
    --from-path exploration.md \
    --to-path /Shared/merchants/exploration \
    --base-language python \
    --overwrite
```

## Usage

The CLI contains `groups` or `commands`. A `command` is a method call that received zero or more arguments. A `group` contains one or more `commands` with common functionality. 

Available groups: 

* `download`
* `upload`

### Top Level Commands

#### cmd: ls

List the databricks resources for a give path.

````commandline
$ databrickstools ls --path <value>
````

Where:

`--path` (string)
> Path to folder inside databricks. 

Example: 

```text
$ databrickstools ls --path /Shared
```

#### cmd: mkdir

Create a directory on databricks. 

````commandline
$ databrickstools mkdir --path <value>
````

Where:

`--path` (string)
> Path to folder inside databricks. 

Example: 

```text
$ databrickstools mkdir --path /Shared/temp
```

### Group: Download

#### cmd: file

Download a given file from databricks!

````commandline
$ databrickstools download file \
    --from-path <value> \
    --to-path <value> \
    --file-format <value>
````

Where:

`--from-path` (string)
> Path to file inside databricks. 

`--to-path` (string)
> Path in local machine. 

`--file-format` (string)
> Format used to download file.
> Default: DATABRICKSTOOLS_DEFAULT_FORMAT

Example: 

```text
databrickstools download file \
    --from-path /Shared/example \
    --to-path example \
    --file-format SOURCE
```

#### cmd: html

Download a notebook as an HTML file. 

````commandline
$ databrickstools download html \
    --from-path <value> \
    --to-path <value>
````

Where:

`--from-path` (string)
> Path to file inside databricks. 

`--to-path` (string)
> Path in local machine. 

Example: 

```text
$ databrickstools download html \
    --from-path /Shared/example \
    --to-path example.html
```

#### cmd: ipynb

Download a notebook as a Jupyter file. Only works for python-based notebooks. 

````commandline
$ databrickstools download ipynb \
    --from-path <value> \
    --to-path <value>
````

Where:

`--from-path` (string)
> Path to file inside databricks. 

`--to-path` (string)
> Path in local machine. 

Example: 

```text
$ databrickstools download ipynb \
    --from-path /Shared/example \
    --to-path example.ipynb
```

#### cmd: source

Download a notebook as a source file. This can be either a `.py` file for Python or a `.sc` file for Scala. 

````commandline
$ databrickstools download source \
    --from-path <value> \
    --to-path <value>
````

Where:

`--from-path` (string)
> Path to file inside databricks. 

`--to-path` (string)
> Path in local machine. 


Example: 

```text
$ databrickstools download source \
    --from-path /Shared/example \
    --to-path example.py
```

### Group: Upload

#### cmd: markdown

Upload a markdown file to databricks as a notebook. 

````commandline
$ databrickstools upload markdown \
    --from-path <value> \
    --to-path <value> \
    --base-language <value> \
    --overwrite
````

Where:

`--from-path` (string)
> Path to `file.md` in your local machine.

`--to-path` (string)
> Path to notebook on databricks.

`--base-language` (string)
> The markdown might contain multiple languages, but we'll need to define (or know) the base language of the notebook. If not present, the CLI will try to infer the base language by looking into the file-ending or fallback to: `DATABRICKSTOOLS_DEFAULT_LANGUAGE`.

`--overwrite` (flag)
> If present, the new file will overwrite the current one on databricks. 

Example: 

```text
$ databrickstools markdown \
    --from-path markdown-file.md \
    --to-path /Shared/test \
    --overwrite
```

#### cmd: source

Same as `markdown` but with the `SOURCE` format. 

## Recommendations

To get the most out of markdown please consider taking a look into:
* [Tut](https://tpolecat.github.io/tut/)
* [Pandoc](https://pandoc.org/)
* [RMarkdown](https://rmarkdown.rstudio.com/lesson-1.html)
* [Reticulate](https://rstudio.github.io/reticulate/articles/r_markdown.html)