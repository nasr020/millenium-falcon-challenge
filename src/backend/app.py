from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import tempfile
from src.core.core import OddsService
from contextlib import asynccontextmanager
from src.parser.parser import parse_falcon_config, parse_routes_db
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

SERVICE = OddsService()

FALCON_CONFIG = "./src/backend/millennium-falcon.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the Falcon config and routes DB at startup
    """
    logger.info("Starting up: Loading Falcon config '%s'", FALCON_CONFIG)
    try:
        falcon_config = parse_falcon_config(FALCON_CONFIG)
        logger.debug("Falcon config parsed: %s", falcon_config)

        galaxy = parse_routes_db(falcon_config.routes_db_path)
        logger.debug("Galaxy created from '%s'", falcon_config.routes_db_path)

        SERVICE.falcon_config = falcon_config
        SERVICE.galaxy = galaxy
        logger.info("Falcon config and Galaxy loaded successfully.")
    except Exception as e:
        logger.exception("Failed to load the Falcon config or routes DB: %s", e)
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
    logger.debug("GET / request received.")
    return {"message": "Welcome to the Millennium Falcon Odds API!"}


@app.post("/api/v1/odds/")
async def compute_odds(empire_file: UploadFile = File(...)):
    """
    Takes an uploaded empire.json file, parse it, then compute the odds.
    The Falcon config is already loaded at startup.
    """
    logger.info("POST /api/v1/odds/ called with file: %s", empire_file.filename)

    if not empire_file.filename.endswith(".json"):
        logger.warning("Uploaded file is not JSON: %s", empire_file.filename)
        raise HTTPException(status_code=400, detail="File must be a JSON file")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp_path = tmp.name
        logger.debug("Created temporary file: %s", tmp_path)
        shutil.copyfileobj(empire_file.file, tmp)

    try:
        logger.info(
            "Computing odds for file '%s' using falcon config '%s'",
            tmp_path,
            FALCON_CONFIG,
        )
        odds = SERVICE.compute_odds(FALCON_CONFIG, tmp_path)

        logger.info("Odds computed successfully: %d%%", odds)
        return {"odds": odds}
    except Exception as e:
        logger.exception("Error while computing odds: %s", e)
        raise HTTPException(status_code=400, detail=f"Error computing odds: {e}")
    finally:
        # Clean up the temporary file
        logger.debug("Removing temp file: %s", tmp_path)
        os.remove(tmp_path)
