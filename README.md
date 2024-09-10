# gcn-classic-text-to-json



## How to contribute

This package uses [Poetry](https://python-poetry.org) for packaging and Python virtual environment management. To get started:

1.  [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) and [clone](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo#cloning-your-forked-repository) this repository.

2.  Install [pre-commit hooks](https://pre-commit.com) by running the following two commands:

        pip install pre-commit
        pre-commit install

3.  Install Poetry by following [their installation instructions](https://python-poetry.org/docs/#installation).

4.  Install this package and its dependencies by running the following command inside your clone of this repository:

        poetry install --all-extras

5.  Run the following command to launch a shell that is preconfigured with the project's virtual environment:

        poetry shell

## How to execute package to obtain GCN Classic JSONs

The package can be executed through two methods:

1. You can obtain all the JSONs associated with a single mission in your current working directory by running the following command:

        python3 -m gcn_classic_text_to_json.notices.{missions_name}

2. Alternatively, you can obtain all JSONs associated with all missions in your current working directory by running the following command:

        python3 -m gcn_classic_text_to_json
