from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import io
import cv2

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
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


@app.get("/video_feed")
async def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return StreamingResponse(gen(), media_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="debug")
