import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import uvicorn
from fastapi import FastAPI


app = FastAPI(
    title="NotiHub",
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888)
