# Import necessary modules from the botbuilder.core package
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount
# Import sqlite3 for database operations
import sqlite3
# Import openai for GPT-3 interactions
import openai

# Define a class named DatabaseBot that inherits from ActivityHandler
class DatabaseBot(ActivityHandler):

    # Initialize the bot with a database path and an OpenAI API key
    def __init__(self, database_path, openai_api_key):
        # Set the database path
        self.database_path = database_path
        # Set the OpenAI API key
        openai.api_key = openai_api_key

    # Define an asynchronous method to handle when new members are added to the chat
    async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            # Check if the added member is not the bot itself
            if member.id != turn_context.activity.recipient.id:
                # Send a welcome message to the user
                await turn_context.send_activity("Hello and welcome! Ask me anything about our data.")

    # Define an asynchronous method to handle incoming messages from users
    async def on_message_activity(self, turn_context: TurnContext):
        # Extract the user's input from the incoming message
        user_input = turn_context.activity.text
        # Get a response by querying the database with the user's input
        response = self.query_database(user_input)
        # Send the response back to the user
        await turn_context.send_activity(response)

    # Define a method to query the database based on user input
    def query_database(self, user_input: str) -> str:
        # Use GPT-3 to generate an SQL query based on the user's input
        prompt = f"Translate the following user request into an SQL query: '{user_input}'"
        response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=1000)
        query = response.choices[0].text.strip()

        # Connect to the SQLite database using the provided path
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        # Try to execute the generated SQL query and fetch results
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            # Convert the results into a string format
            response = "\n".join([str(row) for row in rows])
        except Exception as e:
            # If there's an error in executing the query, return an error message
            response = f"Error executing query: {e}"

        # Close the database connection
        connection.close()
        # Return the response (either the query results or an error message)
        return response
