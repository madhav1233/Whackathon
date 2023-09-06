from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount
import sqlite3
import openai

class DatabaseBot(ActivityHandler):

    def __init__(self, database_path, openai_api_key):
        self.database_path = database_path
        openai.api_key = openai_api_key

    async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome! Ask me anything about our data.")

    async def on_message_activity(self, turn_context: TurnContext):
        user_input = turn_context.activity.text
        response = self.query_database(user_input)
        await turn_context.send_activity(response)

    def query_database(self, user_input: str) -> str:
        # Generate SQL query using GPT-3
        prompt = f"Translate the following user request into an SQL query: '{user_input}'"
        response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=1000)
        query = response.choices[0].text.strip()

        # Connect to the SQLite database
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        # Execute the query and fetch results
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            response = "\n".join([str(row) for row in rows])
        except Exception as e:
            response = f"Error executing query: {e}"

        connection.close()
        return response
