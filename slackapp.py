from flask import Flask, request, jsonify
from flask_cors import CORS
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from openai import OpenAI
# Fetch messages from a Slack channel
from datetime import datetime, timedelta


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set your Slack Bot Token and OpenAI API Key
SLACK_TOKEN =   # Replace with your Slack bot token
OPENAI_API_KEY = # Replace with your OpenAI API key
client = WebClient(token=SLACK_TOKEN)
# openai.api_key = OPENAI_API_KEY
openaiClient = OpenAI(
  api_key=OPENAI_API_KEY
)

def join_channel(channel_id):
    try:
        response = client.conversations_join(channel=channel_id)
        print(f"Bot joined the channel: {response['channel']['name']}")
    except SlackApiError as e:
        print(f"Error joining channel: {e.response['error']}")



def fetch_last_month_messages_combined(channel_id, user_id):
    try:
        # Calculate the timestamp range for the previous month
        now = datetime.now()
        first_day_of_current_month = datetime(now.year, now.month, 1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_previous_month = datetime(last_day_of_previous_month.year, last_day_of_previous_month.month, 1)
        
        # Convert to Unix timestamps
        oldest = int(first_day_of_previous_month.timestamp())
        latest = int(last_day_of_previous_month.timestamp())
        
        # Fetch messages within the specified date range
        response = client.conversations_history(
            channel=channel_id,
            # oldest=oldest,
            # latest=latest,
            inclusive=True,
            limit=1000  # Set a high limit to fetch as many messages as possible
        )
        print("response", response)
        
        # Filter messages based on the user ID
        messages = response.get("messages", [])
        print("messages", messages)
        user_messages = [msg.get("text", "") for msg in messages if msg.get("user") == user_id]
        print("user_messages", user_messages)

        # Combine all messages into one paragraph
        combined_messages = " ".join(user_messages)
        print("combined_messages", combined_messages)
        
        return combined_messages
    except SlackApiError as e:
        return {"error": f"Slack API error: {e.response['error']}"}


# Extract skills using OpenAI
def extract_skills_from_message(message):
    try:
        completion = openaiClient.chat.completions.create(
            model="gpt-4o",
            store=True,
            messages=[
                {"role": "user", "content": f"list skills from the following text: {message} seperated by comma only without any other word if no skills found return no skills"}
            ]
        )
        print(completion.choices[0].message.content)
        # Extract the model's response
        skills = completion.choices[0].message.content
        return skills.strip()

    except Exception as e:
        return f"Error extracting skills: {str(e)}"

# API endpoint to fetch messages and extract skills
@app.route("/slack/extract-skills", methods=["POST"])
def slack_extract_skills():
    try:
        # Extract the channel ID from the request
        data = request.json
        print("data", data)
        channel_id = data.get("channel_id", "")
        user_id = data.get("user_id", "")
        print("channel_id", channel_id)
        print("user_id ", user_id )

        if not channel_id:
            return jsonify({"error": "No channel_id provided"}), 400

        join_channel(channel_id)

        # Fetch messages from the Slack channel
        messages = fetch_last_month_messages_combined(channel_id, user_id)
        print("fetched msgs", messages)
        skill_list = extract_skills_from_message(messages)


        # if "error" in messages:
        #     return jsonify({"error": messages["error"]}), 500

        # # Extract skills from messages
        # skills_list = {}
        # for msg in messages:
        #     if "text" in msg:
        #         skills = extract_skills_from_message(msg["text"])
        #         skills_list[msg["text"]] = skills

        # Return the extracted skills
        return jsonify({"skills": skills_list})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# def extract_skills_from_response(response):
#     """
#     Extracts skills as an array from the OpenAI API response.

#     Args:
#         response (dict): The API response containing messages and skill extraction results.

#     Returns:
#         list: A list of unique skills extracted from the response.
#     """
#     skills = []

    # Iterate over the messages and their associated skill extraction
    # for message, extracted_text in response.get("skills", {}).items():
    #     if "The provided text does not contain" not in extracted_text:
    #         # Split skills into a list and clean up formatting
    #         extracted_lines = extracted_text.split("\n")
    #         for line in extracted_lines:
    #             # Identify lines with skill mentions
    #             if line.strip().startswith("1.") or line.strip().startswith("•"):
    #                 skills.append(line.strip().lstrip("1.").lstrip("•").strip())

    # # Remove duplicates and return skills as a sorted array
    # return sorted(set(skills))

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

