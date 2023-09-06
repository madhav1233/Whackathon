from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from bot import DatabaseBot  # Import the bot from bot.py

# Initialize Flask
app = Flask(__name__)

# Bot Framework Adapter settings
SETTINGS = BotFrameworkAdapterSettings("cb1d782a-d2ea-48fb-90a5-75dcb6333844")
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Initialize our bot
BOT = DatabaseBot("tickets.db", "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")

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
