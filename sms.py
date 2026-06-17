from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

acc_sid = os.getenv('ACC_SID')
auth_token = os.getenv('AUTH_TOKEN')
twilio_phone = os.getenv('TWILIO_PHONE')
phone_number = os.getenv('PHONE')
messaging_service_sid = os.getenv('MESSAGE_SERVICE_SID')


client = Client(acc_sid, auth_token)

client.messages.create(
    body=f"Hello Maurice, this is a test message from your Python script.",
    messaging_service_sid=messaging_service_sid,
    to=phone_number
)
print(acc_sid)
print(auth_token)
print(twilio_phone)
print(phone_number) 
print(messaging_service_sid)
print("Message sent successfully!")
