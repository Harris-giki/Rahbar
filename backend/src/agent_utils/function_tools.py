import os
from typing import Annotated
from pydantic import Field
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, RunContext
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB globals
client = None
database = None

async def get_mongodb_connection():
    """Create or re-use MongoDB connection for tax filing data."""
    global client, database

    if client is None:
        connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        database_name = os.getenv('MONGODB_DATABASE_NAME', 'tax_filing_db')

        if not connection_string:
            raise ValueError("Missing MONGODB_CONNECTION_STRING environment variable")

        # Append DB name if not present
        if f"/{database_name}" not in connection_string:
            connection_string = connection_string.rstrip('/') + f"/{database_name}?retryWrites=true&w=majority"

        client = AsyncIOMotorClient(connection_string)
        database = client[database_name]

        # Test connection
        await client.admin.command("ping")

    return database


@function_tool()
async def user_data_inquiry(
    context: RunContext,
    full_name: Annotated[str, Field(description="User's full name")],
    father_name: Annotated[str, Field(description="User's father's full name")],
    cnic: Annotated[str, Field(description="User's CNIC number without dashes")],
    income_amount: Annotated[str, Field(description="The amount (in PKR) for which tax return needs to be filed")],
) -> str:
    """
    Save the user's tax filing data into the MongoDB database.
    This tool should be called ONLY after Rahbar has collected all required details from the user.
    """

    try:
        await context.session.generate_reply(
            instructions="Inform the user that their tax filing information is being securely saved."
        )

        db = await get_mongodb_connection()

        tax_record = {
            "full_name": full_name,
            "father_name": father_name,
            "cnic": cnic,
            "income_amount": income_amount,
            "status": "pending_filing",
            "timestamp": context.session.start_time.isoformat() if hasattr(context.session, "start_time") else None,
        }

        result = await db.tax_records.insert_one(tax_record)

        if result.inserted_id:
            return (
                "آپ کی معلومات کامیابی سے محفوظ کر لی گئی ہیں۔ "
                "اب میں آپ کا ٹیکس ریٹرن خودکار طریقے سے فائل کرنے کے اگلے مراحل مکمل کروں گی۔"
            )

        return "معذرت، معلومات محفوظ نہ ہو سکیں۔ براہ کرم دوبارہ کوشش کریں۔"

    except Exception as e:
        return f"An error occurred while saving your tax filing data: {str(e)}"
