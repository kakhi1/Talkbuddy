#uvicorn main:app
#uvicorn main:app --reload
#source venv/Scripts/activate


#Main Imports
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import openai

#custom Function Imports
from functions.database import store_messages, reset_messages
from functions.openai_requests import convert_audio_to_text, get_chat_response
from functions.text_to_speech import convert_text_to_speech


#Initiate App
app = FastAPI()

# CORS - Origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
]


# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Check Health
@app.get("/health")
async def check_health():
    return {"message": "healthy"}

# Reset Messages
@app.get("/reset")
async def reset_conversation():
    reset_messages()
    return {"message": "conversation reset"}


#Get audio

@app.post ("/post-audio/")
async def post_audio(file:UploadFile=File(...)):
   
   # Get saved audio 
   # audio_input = open("voice.mp3", "rb") 


   # Save file from Frontend
   with open(file.filename, "wb") as buffer:
       buffer.write(file.file.read())
   audio_input = open(file.filename, "rb")    


   # Decode Audio 
   message_decoded = convert_audio_to_text (audio_input)

   # Guard: Ensure message decode 
   if not message_decoded:
       return HTTPException(status_code=400, detail="Failed to decode audio")
   
   # Get ChadtGPT response
   chat_reponse = get_chat_response (message_decoded)

   # Guard: Ensure message decode 
   if not chat_reponse:
       return HTTPException(status_code=400, detail="Failed to get chat response")

   # Store messages
   store_messages(message_decoded, chat_reponse)

   # Convert chat response to audio
   audio_output = convert_text_to_speech(chat_reponse)

   # Guard: Ensure message decode 
   if not audio_output:
       return HTTPException(status_code=400, detail="Failed to get Eleven labs audio response")
   
   # Create a generator that yields chunks of data 
   def iterfile():
       yield audio_output

   # Return audio file 
   return StreamingResponse(iterfile(), media_type="application/octet-stream")    

 


