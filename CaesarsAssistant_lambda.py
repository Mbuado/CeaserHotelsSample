import json
import boto3
import logging

# Initialize AWS clients
dynamodb = boto3.client("dynamodb")
s3 = boto3.client("s3")

# Resource names
TABLE_NAME = "CaesarsReservations"
BUCKET_NAME = "caesars-hotel-events"
FILE_NAME = "events.json"

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_s3_data():
    """Fetches event information from S3."""
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
        data = json.loads(response["Body"].read().decode("utf-8"))
        logger.info(json.dumps({"action": "get_s3_data", "status": "success", "data": data}))
        return data
    except Exception as e:
        logger.error(json.dumps({"action": "get_s3_data", "status": "error", "error": str(e)}))
        return {}

def get_reservation_details(reservation_id):
    """Fetches reservation details from DynamoDB."""
    try:
        response = dynamodb.get_item(
            TableName=TABLE_NAME,
            Key={"reservation_id": {"S": reservation_id}}
        )
        logger.info(json.dumps({"action": "get_reservation_details", "status": "success", "response": response}))
        return response.get("Item", {})
    except Exception as e:
        logger.error(json.dumps({"action": "get_reservation_details", "status": "error", "error": str(e)}))
        return {}

def format_response(is_connect_event, message, intent_name=None, slots=None):
    """Formats the response for Amazon Connect or Lex V2."""
    if is_connect_event:
        return {
            "status": "success",
            "message": message
        }
    else:
        return {
            "sessionState": {
                "intent": {
                    "name": intent_name if intent_name else "FallbackIntent",
                    "state": "Fulfilled",
                    "slots": slots if slots else {}
                },
                "dialogAction": {
                    "type": "Close"
                }
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": message
                }
            ]
        }

def lambda_handler(event, context):
    try:
        # Log the incoming event
        logger.info(json.dumps({"action": "lambda_handler", "status": "start", "event": event}))

        # Initialize variables
        intent_name = None
        reservation_id = None
        day = None
        slots = {}

        # Determine if the event is from Amazon Connect or Lex V2
        is_connect_event = "Details" in event and "ContactData" in event["Details"]

        if is_connect_event:
            # Handle Amazon Connect input
            parameters = event.get("Details", {}).get("Parameters", {})
            intent_name = parameters.get("intent")
            reservation_id = parameters.get("reservation_id")
            day = parameters.get("day")
        else:
            # Handle Lex V2 input
            intent_name = event.get("sessionState", {}).get("intent", {}).get("name")
            slots = event.get("sessionState", {}).get("intent", {}).get("slots", {})
            reservation_id = slots.get("reservation_id", {}).get("value", {}).get("interpretedValue")
            day = slots.get("day", {}).get("value", {}).get("interpretedValue", "Friday").title()

        # Handle the intent
        if intent_name == "CheckReservation":
            logger.info(json.dumps({"action": "CheckReservation", "reservation_id": reservation_id}))

            # Fetch reservation details from DynamoDB
            reservation = get_reservation_details(reservation_id)
            if reservation:
                customer_name = reservation.get("customer_name", {}).get("S")
                restaurant = reservation.get("restaurant", {}).get("S")
                date = reservation.get("date", {}).get("S")
                time = reservation.get("time", {}).get("S")

                message = f"You have a reservation at {restaurant} on {date} at {time}."
            else:
                message = "No reservation found with that ID."

            return format_response(is_connect_event, message, intent_name, slots)

        elif intent_name == "GetEventDetails":
            logger.info(json.dumps({"action": "GetEventDetails", "day": day}))

            # Fetch event details from S3
            s3_data = get_s3_data()
            event_details = s3_data.get(day, "No events scheduled for that day.")

            message = f"Here are the event details for {day}: {event_details}"
            return format_response(is_connect_event, message, intent_name, slots)

        else:
            return format_response(is_connect_event, "I'm sorry, I didn't understand your request.", intent_name, slots)

    except Exception as e:
        logger.error(json.dumps({"action": "lambda_handler", "status": "error", "error": str(e)}))
        return format_response(is_connect_event, "An unexpected error occurred. Please try again later.", intent_name, slots)