# CeaserHotelsSample

This project demonstrates an Amazon Connect and Lex V2 integration for handling customer interactions related to hotel reservations and event details at Caesar Hotels. It consists of:

Amazon Connect Flow – Manages customer interactions.
Lex V2 Bot – Determines user intent (Check Reservation, Get Event Details).
DynamoDB Table – Stores hotel reservation details.
S3 Bucket – Stores event information.
AWS Lambda Function – Retrieves reservation details from DynamoDB and event details from S3.

1. Prerequisites
Ensure you have the following AWS services configured:

Amazon Connect instance
Amazon Lex V2 Bot with proper intents
DynamoDB Table named CaesarsReservations
S3 Bucket named caesars-hotel-events with events.json
AWS Lambda Function with execution permissions

2. Deployment Steps
Step 1: Set Up Amazon Connect Contact Flow
Import the CeaserEntertainment 2.0_contactFlow into Amazon Connect.
Modify the flow to integrate with Lex V2.
Set the GetUserInput block to call the Lex bot.
Add a Lambda invocation block to call the reservation lookup function.

Step 2: Configure Lex V2 Bot
Import the lex-bot.json file into Amazon Lex V2.



Step 3: Set Up DynamoDB Table

Set the Table Name to CaesarsReservations.
Set the Primary Key as:
Partition Key: reservation_id (String)

Click Create Table.
Step 2: Import JSON Data to DynamoDB

Click "Import Data" CaesarsReservations_Dynamodb → Select "Upload JSON".
Upload the JSON file and click Start Import.

Step 4: Upload Event Data to S3
Create a bucket caesars-hotel-events.
Upload events.json, which contains daily event details.

Step 5: Deploy AWS Lambda Function
Deploy the CaesarsAssistant_lambda script as a Lambda function.

Assign permissions to read from DynamoDB and S3.
Set the function to trigger from Amazon Connect and Lex V2.

Step 6: Testing
Call Amazon Connect and ask:
"Can you check my reservation for ID 12345?"
"What events are happening on Friday?"
Ensure the correct responses are returned.

3. AWS Lambda Code Breakdown
get_reservation_details(reservation_id) → Fetches reservation from DynamoDB.
get_s3_data() → Retrieves event details from S3.
lambda_handler(event, context) → Handles both Amazon Connect and Lex V2 interactions.
