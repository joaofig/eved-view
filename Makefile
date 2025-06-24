
setup:
	uv init --app --description "eVED Web-based viewer" --python 3.12
	uv sync
	uv run python -m ensurepip --upgrade


run:
	uv run evedview.py

check:
	uvx ruff check .


format:
	uvx ruff format .
	uvx ruff check . --fix
	uvx ruff check --select I . --fix
