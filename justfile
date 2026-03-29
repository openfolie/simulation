dev *FLAGS:
  uv run main.py {{FLAGS}}

fmt *FLAGS:
  black . {{FLAGS}}

test *FLAGS:
  uv run pytest {{FLAGS}}
