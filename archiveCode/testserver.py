# import the required libraries
from twilio.rest import Client

# Set up your Twilio account credentials
account_sid = 'AC7deedfa313b867076cbac2e8646aae3c'
auth_token = 'c6d5c431a1a98b52b8cdcddcfd533432'
client = Client(account_sid, auth_token)

# Set up the message details
to_number = '+14802046697' # replace with the recipient's phone number
from_number = '+18445040915' # replace with your Twilio phone number
message_body = 'Bwana Masa'

# Send the message using the Twilio REST API
message = client.messages.create(
    body=message_body,
    from_=from_number,
    to=to_number
)

# Print out the message sid (unique ID)
print(message.sid)
