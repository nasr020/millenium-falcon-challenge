from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import tempfile
from src.core.core import OddsService
from contextlib import asynccontextmanager
from src.parser.parser import parse_falcon_config, parse_routes_db
from fastapi.middleware.cors import CORSMiddleware

SERVICE = OddsService()

FALCON_CONFIG = "./src/backend/millennium-falcon.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the Falcon config and routes DB at startup
    """
    try:
        falcon_config = parse_falcon_config(FALCON_CONFIG)
        galaxy = parse_routes_db(falcon_config.routes_db_path)

        SERVICE.falcon_config = falcon_config
        SERVICE.galaxy = galaxy
    except Exception as e:
        raise RuntimeError(
            f"Failed to load the Falcon config or routes DB at startup: {e}"
        ) from e

    yield


app = FastAPI(
    title="Millennium Falcon Odds API",
    description="Compute the odds that the Millennium Falcon reaches Endor in time.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """
    Welcome message
    """
    return {"message": "Welcome to the Millennium Falcon Odds API!"}


@app.post("/api/v1/odds/")
async def compute_odds(empire_file: UploadFile = File(...)):
    """
    Takes an uploaded empire.json file, parse it, then compute the odds.
    The Falcon config is already loaded at startup.
    """
    if not empire_file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="File must be a JSON file")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp_path = tmp.name
        shutil.copyfileobj(empire_file.file, tmp)

    try:
        odds = SERVICE.compute_odds(FALCON_CONFIG, tmp_path)

        return {"odds": odds}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error computing odds: {e}")
    finally:
        # Clean up the temporary file
        os.remove(tmp_path)
