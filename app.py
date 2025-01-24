from flask import Flask, request, jsonify
from flask_cors import CORS
# import openai
from openai import OpenAI

client = OpenAI(
  api_key=
)


# Initialize Flask app
app = Flask(__name__)
CORS(app) 

# Set your OpenAI API key
# openai.api_key = 
@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Endpoint to process text and extract skills using OpenAI.
    """
    try:
        # Extract data from the request
        data = request.json
        prompt_text = data.get("prompt", "")
        print("prompt_text",prompt_text)

        # Validate input
        if not prompt_text:
            return jsonify({"error": "No prompt provided"}), 400



        completion = client.chat.completions.create(
            model="gpt-4o",
            store=True,
            messages=[
                {"role": "user", "content": prompt_text}
            ]
        )


        print(completion.choices[0].message.content)
        # Extract the model's response
        completion_message = completion.choices[0].message.content
        # Process the response
        skills = completion.choices[0].message.content.strip().split(", ")
        return jsonify({"skills": skills})
        
        # Return as a valid JSON response
        # return jsonify({"message": completion_message})





        

        # return jsonify({"message": "POST request received"})

    except Exception as e:
        # Handle errors gracefully
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
