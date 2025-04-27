from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from archon.archon_graph import agentic_flow
from langgraph.types import Command
from utils.utils import write_to_log
    
app = FastAPI()

class InvokeRequest(BaseModel):
    message: str
    thread_id: str
    is_first_message: bool = False
    config: Optional[Dict[str, Any]] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}    

import asyncio

@app.post("/invoke")
async def invoke_agent(request: InvokeRequest):
    try:
        config = request.config or {
            "configurable": {
                "thread_id": request.thread_id
            }
        }

        response = ""
        timeout_seconds = 30  # ⏰ Timeout if no response in 30 sec
        
        if request.is_first_message:
            write_to_log(f"Processing first message for thread {request.thread_id}")

            async def stream_messages():
                async for msg in agentic_flow.astream(
                    {"latest_user_message": request.message},
                    config,
                    stream_mode="custom"
                ):
                    print(f"[Streaming] Received partial message: {msg}")
                    yield str(msg)

            try:
                async for partial in asyncio.wait_for(stream_messages(), timeout=timeout_seconds):
                    response += partial
            except asyncio.TimeoutError:
                print(f"[Timeout] agentic_flow.astream stuck for thread {request.thread_id}")
                raise HTTPException(status_code=504, detail="Timeout while waiting for agent response")

        else:
            write_to_log(f"Processing continuation for thread {request.thread_id}")

            async def stream_messages():
                async for msg in agentic_flow.astream(
                    Command(resume=request.message),
                    config,
                    stream_mode="custom"
                ):
                    print(f"[Streaming] Received partial message: {msg}")
                    yield str(msg)

            try:
                async for partial in asyncio.wait_for(stream_messages(), timeout=timeout_seconds):
                    response += partial
            except asyncio.TimeoutError:
                print(f"[Timeout] agentic_flow.astream stuck for thread {request.thread_id}")
                raise HTTPException(status_code=504, detail="Timeout while waiting for agent response")

        write_to_log(f"Final response for thread {request.thread_id}: {response}")
        return {"response": response}

    except Exception as e:
        print(f"Exception invoking Archon for thread {request.thread_id}: {str(e)}")
        write_to_log(f"Error processing message for thread {request.thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    """Process a message through the agentic flow and return the complete response.

    The agent streams the response but this API endpoint waits for the full output
    before returning so it's a synchronous operation for MCP.
    Another endpoint will be made later to fully stream the response from the API.
    
    Args:
        request: The InvokeRequest containing message and thread info
        
    Returns:
        dict: Contains the complete response from the agent
    """
    try:
        config = request.config or {
            "configurable": {
                "thread_id": request.thread_id
            }
        }

        response = ""
        if request.is_first_message:
            write_to_log(f"Processing first message for thread {request.thread_id}")
            async for msg in agentic_flow.astream(
                {"latest_user_message": request.message}, 
                config,
                stream_mode="custom"
            ):
                response += str(msg)
        else:
            write_to_log(f"Processing continuation for thread {request.thread_id}")
            async for msg in agentic_flow.astream(
                Command(resume=request.message),
                config,
                stream_mode="custom"
            ):
                response += str(msg)

        write_to_log(f"Final response for thread {request.thread_id}: {response}")
        return {"response": response}
        
    except Exception as e:
        print(f"Exception invoking Archon for thread {request.thread_id}: {str(e)}")
        write_to_log(f"Error processing message for thread {request.thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Archon graph service')
    parser.add_argument('--port', type=int, required=True, help='Port to run the server on')
    args = parser.parse_args()
    
    # Use only the port from command line args
    port = args.port
    print(f"Starting server on port {port}")
    
    # For Streamlit Cloud, we need to bind to 0.0.0.0
    uvicorn.run(app, host="0.0.0.0", port=port)
