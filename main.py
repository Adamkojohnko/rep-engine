from fastapi import FastAPI, Request, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

sid = os.getenv("TWILIO_ACCOUNT_SID")
token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(sid, token)

@app.get("/start")
def start(name: str, phone: str):
    # This line pulls the number specifically from your .env
    my_twilio_number = os.getenv("TWILIO_NUMBER")
    
    print(f"DEBUG: Attempting to send from {my_twilio_number} to {phone}")
    
    try:
        message = client.messages.create(
            body=f"Hi {name}, thanks for choosing us! On a scale of 1-5, how was your experience today?",
            from_=my_twilio_number,  # Ensure this matches your .env variable name
            to=phone
        )
        return {"status": "Success", "message_sid": message.sid}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"status": "Failed", "error": str(e)}    

@app.post("/webhook")
async def webhook(request: Request):
    try:
        # 1. Capture the data from Twilio
        form_data = await request.form()
        body = form_data.get("Body", "").strip()
        print(f"DEBUG: Received a text message: {body}")

        # 2. Build the Response
        twiml_response = MessagingResponse()

        if body in ["4", "5"]:
            twiml_response.message("Thanks! Leave a review here: https://google.com")
        elif body in ["1", "2", "3"]:
            twiml_response.message("Sorry! Give us feedback here: https://feedback.com")
        else:
            twiml_response.message("Thanks for reaching out! Please rate us 1-5.")

        # 3. Send it back to Twilio
        return Response(content=str(twiml_response), media_type="application/xml")

    except Exception as e:
        # This will print the EXACT error in your terminal so we stop guessing
        print(f"CRITICAL ERROR IN WEBHOOK: {e}")
        return Response(content="Error", status_code=500)