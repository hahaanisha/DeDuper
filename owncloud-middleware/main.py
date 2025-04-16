from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from dotenv import load_dotenv
import requests, hashlib, base64, os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

# ✅ CORS setup - allows local frontend and optional production frontend
origins = [
    "http://127.0.0.1:5501",
    "http://localhost:5501",
    "http://yourfrontenddomain.com", 
    "http://50.17.52.208:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔍 Optional: Log incoming request origins (for debugging CORS)
@app.middleware("http")
async def debug_headers(request: Request, call_next):
    print(f"🛬 Incoming request from: {request.headers.get('origin')}")
    response = await call_next(request)
    print(f"📤 Response headers: {response.headers}")
    return response


@app.post("/owncloud-upload")
async def owncloud_upload(request: Request, file: UploadFile = File(...)):
    try:
        user_id = request.query_params.get('userID')
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing userID")

        file_content = await file.read()
        filename = file.filename

        # Encode file in base64
        file_b64 = base64.b64encode(file_content).decode('utf-8')

        # Construct payload
        payload = {
            "fileName": filename,
            "fileContent": file_b64,
            "userID": user_id
        }

        upload_api = os.getenv("UPLOAD_API")
        if not upload_api:
            raise HTTPException(status_code=500, detail="UPLOAD_API not set in environment")

        # Send file to upload API
        lambda_response = requests.post(upload_api, json=payload)

        if lambda_response.status_code != 200:
            print(f"Upload API failed: {lambda_response.status_code}, {lambda_response.text}")
            raise HTTPException(status_code=500, detail="Upload API error")

        return lambda_response.json()

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
