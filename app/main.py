from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
from dateutil.parser import parse
from .models import VesselResponse, NLQuery
from .calculator import calculate_all
from .llm_client import parse_nl_to_request, generate_explanation
from .utils import prepare_query_for_api
import json
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(
    title="South African Port Tariff Calculator",
    description="Calculate port tariffs for South African ports",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify your frontend origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "name": "South African Port Tariff Calculator API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/nl_calculate", "method": "POST", "description": "Calculate tariffs from natural language query"}
        ]
    }


@app.post("/nl_calculate", response_model=VesselResponse)
def nl_calculate(query: NLQuery):
    """
    Calculate port tariffs from natural language query using Gemini
    """
    try:
        # Prepare query for API processing
        prepared_query = prepare_query_for_api(query.query)
        
        # Parse natural language query to structured data
        data = parse_nl_to_request(prepared_query["query"])
        
        # Log parsed data for debugging
        logging.getLogger("uvicorn.error").info(f"Parsed NL data: {json.dumps(data)}")
        
        # Format dates if they're strings
        if isinstance(data.get("arrival"), str):
            data["arrival"] = parse(data["arrival"])
        if isinstance(data.get("departure"), str):
            data["departure"] = parse(data["departure"])
            
        # Calculate tariffs
        results = calculate_all(data)
        
        # Generate explanation
        explanation = generate_explanation(data, results)
        
        # Return formatted response with explanation
        return VesselResponse(**{**results, "explanation": explanation})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # Return detailed validation errors
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)