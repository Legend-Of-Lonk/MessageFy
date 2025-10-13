import json
from datetime import datetime

MSG_JOIN = "JOIN"
MSG_LEAVE = "LEAVE"
MSG_MESSAGE = "MESSAGE"
MSG_USERLIST = "USER_LIST"
MSG_ERROR = "ERROR"

def createMessage(sender, type=MSG_MESSAGE, content='<Empty>', timestamp=None):

    if timestamp is None:
        timestamp = datetime.now()

    message = {}
    message["type"] = type
    message["sender"] = sender
    message["content"] = content
    message["timestamp"] = timestamp.isoformat()

    return message

def serialize(message):
    return (json.dumps(message) + "\n").encode('utf-8')

def deserialize(data):
    try:
        jsonString = data.decode('utf-8').strip()
        message = json.loads(jsonString)
        return message
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print("failed to deserialize: ", e)
        return None
