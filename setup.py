from setuptools import setup, find_packages


with open("README.md") as file:
    readme = file.read()

setup(
    name="databrickstools",
    version="0.3.0",
    description="A simple commandline application to manage databricks resources.",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Rodrigo Hernández Mota",
    author_email='contact@rhdzmota.com',
    url="https://github.com/rhdzmota/databrickstools-cli",
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        "fire==0.3.0",
        "requests==2.23.0"
    ],
    python_requires='>=3.5, <4',
    entry_points={
      "console_scripts": [
          "databrickstools=databrickstools:main"
      ]
    },
    license="LICENSE.md",
    scripts=["bin/databrickstools"],
)
