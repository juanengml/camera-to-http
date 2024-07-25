from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import io
import cv2

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/streaming", response_class=HTMLResponse)
async def index(request: Request):
    """Video streaming home page."""
    return templates.TemplateResponse("index.html", {"request": request})


def gen():
    """Video streaming generator function."""
    vc = cv2.VideoCapture("http://72.253.153.216:81/mjpg/video.mjpg")
    while True:
        read_return_code, frame = vc.read()
        if not read_return_code:
            break
        encode_return_code, image_buffer = cv2.imencode('.jpg', frame)
        io_buf = io.BytesIO(image_buffer)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')


@router.get("/video_feed")
async def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return StreamingResponse(gen(), media_type='multipart/x-mixed-replace; boundary=frame')
