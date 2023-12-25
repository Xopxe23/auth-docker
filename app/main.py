import os
import sys

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.auth.middlewares import refresh_tokens_middleware
from app.config import settings

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from app.auth.router import auth_router

app = FastAPI()


app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.middleware("http")(refresh_tokens_middleware)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", reload=True,
        # host=settings.ID_ADDRESS
    )
