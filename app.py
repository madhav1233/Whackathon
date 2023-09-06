from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from bot import DatabaseBot  # Import the bot from bot.py

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Initialize Flask
app = Flask(__name__)

# Bot Framework Adapter settings
SETTINGS = BotFrameworkAdapterSettings("YOUR_APP_ID")
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Retrieve OpenAI API key from Azure Key Vault
key_vault_url = "https://openAIticketkey.vault.azure.net/"
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
openai_api_key = secret_client.get_secret("OpenAIkey").value

# Initialize our bot
BOT = DatabaseBot("tickets.db", openai_api_key)

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)

    async def call_bot(turn_context):
        await BOT.on_turn(turn_context)

    task = ADAPTER.process_activity(activity, "", call_bot)
    return Response(status=201)

if __name__ == "__main__":
    app.run(port=3978)
