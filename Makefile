
setup:
	uv init --app --description "eVED Web-based viewer" --python 3.12
	uv sync
	uv run python -m ensurepip --upgrade


run:
	uv run evedview.py

check:
	uvx ruff check .

