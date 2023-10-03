# import the required libraries
from twilio.rest import Client

# Set up your Twilio account credentials
account_sid =
auth_token = 
client = Client(account_sid, auth_token)

# Set up the message details
to_number = '' # replace with the recipient's phone number
from_number = '' # replace with your Twilio phone number
message_body = ''

# Send the message using the Twilio REST API
message = client.messages.create(
    body=message_body,
    from_=from_number,
    to=to_number
)

# Print out the message sid (unique ID)
print(message.sid)
