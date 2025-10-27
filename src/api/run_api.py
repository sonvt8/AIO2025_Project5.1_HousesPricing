"""
Script to run the FastAPI server for House Price Prediction.
Run this script from project root: python src/api/run_api.py
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import uvicorn after adding to path
import uvicorn

if __name__ == "__main__":
    # Change to project root directory for proper path resolution
    os.chdir(project_root)

    print(f"✅ Starting API server from: {project_root}")
    print("📍 Running on: http://localhost:8000")
    print("📚 Docs at: http://localhost:8000/docs")
    print()

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root)],  # Watch for changes in project root
    )
