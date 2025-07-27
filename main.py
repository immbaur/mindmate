import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from tools.news import get_latest_news
from fastapi.middleware.cors import CORSMiddleware
# import memory  # optional conversation store

# ── logging setup ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,  # set to INFO or WARNING in production
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ── environment and OpenAI client setup ─────────────────────────────────────
load_dotenv()
client = OpenAI()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for stricter control
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── OpenAI function tool definition ─────────────────────────────────────────
# This schema enables the model to call external functions like get_latest_news()
tools = [
    {
        "type": "function",
        "name": "get_latest_news",
        "description": "Fetch the most recent headlines for a topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "News topic"
                },
                "max_items": {
                    "type": "integer",
                    "description": "How many articles to return",
                    "default": 3
                }
            },
            "required": ["topic"],
            "additionalProperties": False  # strict schema enforcement
        }
    }
]

# ── DTOs for FastAPI request/response payloads ──────────────────────────────
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

# ── POST /chat endpoint ─────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Initial message history sent to the model
    # Optional: replace with memory.history(req.user_id) for persistence
    history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": req.message},
    ]

    # ── First model call ─────────────────────────────────────────────────────
    try:
        logger.info("Sending initial prompt to model...")
        logger.debug(f"History: {json.dumps(history, indent=2)}")
        logger.debug(f"Tools: {json.dumps(tools, indent=2)}")
        model_response = client.responses.create(
            model="gpt-4o-mini",
            input=history,
            tools=tools,
        )
        logger.debug(f"Model raw response: {model_response}")
    except Exception as e:
        logger.exception("Failed during initial model call.")
        raise HTTPException(status_code=500, detail=str(e))

    # ── Handle model output ──────────────────────────────────────────────────
    output = model_response.output[0]

    if output.type == "message":
        # Model returned a direct answer, return it as-is
        logger.info("Received direct text response from model.")
        return ChatResponse(reply=output.content[0].text)

    elif output.type == "function_call":
        # Model requested a tool to be called
        logger.info(f"Model requested tool invocation: {output.name}")

        # Parse function arguments from model
        try:
            function_args = json.loads(output.arguments)
            logger.debug(f"Parsed tool arguments: {function_args}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse function arguments: {e}")
            raise HTTPException(status_code=500, detail=f"bad tool args: {e}")

        # Call the actual backend tool
        try:
            tool_result = get_latest_news(**function_args)
            logger.info("Tool executed successfully.")
        except Exception as e:
            logger.exception("Tool execution failed.")
            raise HTTPException(status_code=500, detail=f"news fetch failed: {e}")

        # Update the history with the tool response for a second model call
        history.extend([
            output,  # model's function_call
            {
                "type": "function_call_output",
                "call_id": output.call_id,
                "output": json.dumps(tool_result),
            },
        ])

        # ── Final model call with tool output ────────────────────────────────
        try:
            logger.info("Sending tool result back to model for final answer...")
            # logger.debug(f"Updated history: " + json.dumps(history, indent=2)) 
            # logger.debug(f"Tools: {json.dumps(tools, indent=2)}")
            final_response = client.responses.create(
                model="gpt-4o-mini",
                input=history,
                tools=tools,
            )
            logger.debug(f"Final model response: {final_response}")
        except Exception as e:
            logger.exception("Failed during final model call.")
            raise HTTPException(status_code=500, detail=str(e))

        return ChatResponse(reply=final_response.output_text)

    else:
        # Unknown model output type — likely an SDK or logic error
        logger.error(f"Unexpected response type from model: {output.type}")
        raise HTTPException(status_code=500, detail="unexpected response type")