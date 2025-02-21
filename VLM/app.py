from fastapi import FastAPI, File, UploadFile
import shutil
from docuPanda import *

app = FastAPI()
# Start the server: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
# Send POST request: curl -X 'POST' 'http://127.0.0.1:8000/predict/' -H 'Content-Type: multipart/form-data' -F 'file=@data/Test_1.jpg'
    
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    # Read image file
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    url = "https://app.docupanda.io/document"
    api_key = "QBNaKu99Yia3N7fqBLSk9MEfEOy1"
    schema_id = "97a2e3ec"
    
    document_id = getDocumentId(url, api_key, file_path)
    sleep(15) # Wait for response
    standardization_id = getStandardizationId(api_key, document_id, schema_id)
    sleep(15) # Wait for response
    output = getJSON(api_key, standardization_id)
    return output

@app.get("/")
def home():
    return {"message": "FastAPI is running"}