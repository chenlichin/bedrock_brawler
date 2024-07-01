import boto3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Update if needed
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)


def generate_conversation(model_id, system_prompts, messages):
    """
    Sends messages to a model.
    Args:
        model_id (str): The model ID to use.
        system_prompts (JSON) : The system prompts for the model to use.
        messages (JSON) : The messages to send to the model.

    Returns:
        response (JSON): The conversation that the model generated.

    """

    print(f"Generating message with model {model_id}")

    # Inference parameters to use.
    temperature = 0.7

    # Base inference parameters to use.
    inference_config = {"temperature": temperature}

    # Send the message.
    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
    )

    # Log token usage.
    token_usage = response["usage"]
    print(f"Input tokens: {token_usage['inputTokens']}")
    print(f"Output tokens: {token_usage['outputTokens']}")
    print(f"Total tokens: {token_usage['totalTokens']}")
    print(f"Stop reason: {response['stopReason']}")

    text_response = response["output"]["message"]["content"][0]["text"]

    return text_response


@app.route("/invoke_model", methods=["POST"])
def invoke_model():
    data = request.json
    model = data["model"]
    system_prompt = data["system_prompt"]
    prompt = data["prompt"]

    system_prompts = [{"text": system_prompt}]
    message_1 = {
        "role": "user",
        "content": [{"text": prompt}],
    }

    messages = [message_1]

    print(system_prompts)
    print(model)

    results = generate_conversation(model, system_prompts, messages)
    print(results)

    return jsonify({"actions": results})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
