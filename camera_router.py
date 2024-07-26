from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import io
import cv2

router = APIRouter()

templates = Jinja2Templates(directory="templates")

# Dicionário para mapear IDs de câmera para URLs
camera_urls = {
    "1": "http://72.253.153.216:81/mjpg/video.mjpg",
    "2": "http://85.158.74.20/mjpg/video.mjpg",
    "3": "http://190.210.250.149:91/mjpg/video.mjpg",
    "4": "http://37.247.81.113:91/mjpg/video.mjpg",
    "5": "http://76.174.92.213:81/mjpg/video.mjpg",
    "6": "http://66.76.193.12:8000/mjpg/video.mjpg"
}

@router.get("/streaming/{camera_id}", response_class=HTMLResponse)
async def index(request: Request, camera_id: str):
    """Video streaming home page."""
    if camera_id not in camera_urls:
        raise HTTPException(status_code=404, detail="Camera ID not found")
    return templates.TemplateResponse("index.html", {"request": request, "camera_id": camera_id})


@router.get("/grid", response_class=HTMLResponse)
async def grid(request: Request):
    """Video grid page."""
    return templates.TemplateResponse("grid.html", {"request": request, "camera_ids": camera_urls.keys()})


def gen(camera_url):
    """Video streaming generator function."""
    vc = cv2.VideoCapture(camera_url)
    while True:
        read_return_code, frame = vc.read()
        if not read_return_code:
            break
        encode_return_code, image_buffer = cv2.imencode('.jpg', frame)
        io_buf = io.BytesIO(image_buffer)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')


@router.get("/video_feed/{camera_id}")
async def video_feed(camera_id: str):
    """Video streaming route. Put this in the src attribute of an img tag."""
    if camera_id not in camera_urls:
        raise HTTPException(status_code=404, detail="Camera ID not found")
    return StreamingResponse(gen(camera_urls[camera_id]), media_type='multipart/x-mixed-replace; boundary=frame')
