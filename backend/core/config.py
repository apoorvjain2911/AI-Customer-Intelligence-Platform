from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _required_env(name: str) -> str:
	value = os.getenv(name)
	if not value:
		raise RuntimeError(f"Missing required environment variable: {name}")
	return value


SECRET_KEY = _required_env("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
	os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
