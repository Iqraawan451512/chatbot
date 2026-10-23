"""
Vercel serverless entry point.
Runs the FastAPI backend from backend/ for every /api/* and /health request
(see the rewrites in vercel.json); the React frontend is served as static files.
"""

import sys
from pathlib import Path

# Make backend/ importable, the same way running it from that folder does
backend_dir = Path(__file__).resolve().parents[1] / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app  # noqa: E402,F401  (Vercel serves this ASGI app)
from src.services.database import create_db_and_tables  # noqa: E402

# Serverless platforms may skip ASGI startup events, so make sure the
# tables (and any newly added columns) exist on every cold start.
create_db_and_tables()
