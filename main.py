from fastapi import FastAPI
from camera_router import router as camera_router

app = FastAPI()

app.include_router(camera_router, prefix="/cameras")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="debug")
