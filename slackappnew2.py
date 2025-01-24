from flask import Flask, request, jsonify
from flask_cors import CORS
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from openai import OpenAI

# Initialize Flask app
app = Flask(__name__)
CORS(app)

SLACK_TOKEN =   # Replace with your Slack bot token
OPENAI_API_KEY =   # Replace with your OpenAI API key
client = WebClient(token=SLACK_TOKEN)
# openai.api_key = OPENAI_API_KEY
openaiClient = OpenAI(
  api_key=OPENAI_API_KEY
)
# Fetch messages from a Slack channel
def fetch_channel_messages(channel_id, user_id):
    try:
        response = client.conversations_history(channel=channel_id, limit=10)
        messages = response.get("messages", [])
        user_messages = [msg.get("text", "") for msg in messages if msg.get("user") == user_id]

        return user_messages
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
    """
    API endpoint to fetch Slack messages for a specific user and extract skills using OpenAI.
    """
    try:
        # Extract the channel ID and user ID from the request
        data = request.json
        channel_id = data.get("channel_id", "")
        user_id = data.get("user_id", "")

        if not channel_id:
            return jsonify({"error": "No channel_id provided"}), 400
        if not user_id:
            return jsonify({"error": "No user_id provided"}), 400

        # Fetch messages for the specific user
        messages = fetch_channel_messages(channel_id, user_id)

        if isinstance(messages, dict) and "error" in messages:
            return jsonify({"error": messages["error"]}), 500

        # Extract skills from the user's messages
        skills_list = {}
        for msg in messages:
            skills = extract_skills_from_message(msg)
            skills_list[msg] = skills

        # Return the extracted skills
        return jsonify({"skills": skills_list})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)