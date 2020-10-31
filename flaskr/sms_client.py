import sys
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from flaskr.service_factory import get_twilio_client

fromPhoneNumber = "+18442783972"
def send_text(to, message):
    client = get_twilio_client()
    print("sending text to: " + to, file=sys.stderr)
    print("sending text to: " + to)
    print("message: " + message, file=sys.stderr)
    # try:
        # message = client.messages.create(
        #     to=to,
        #     from_=fromPhoneNumber,
        #     body=message)
    # except TwilioRestException as e:
    #     print(e)
