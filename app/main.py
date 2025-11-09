"""
FastAPI Application for SHL Assessment Recommendation System
Main server that exposes API endpoints for the recommendation engine
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import uvicorn
from dotenv import load_dotenv

# CRITICAL: Load environment variables from .env file FIRST
# This must happen before importing RecommendationEngine (which needs OPENAI_API_KEY)
load_dotenv()

# Import our recommendation engine (requires OPENAI_API_KEY from .env)
from app.core.logic import RecommendationEngine


# ============================================================================
# Pydantic Models - Define Request/Response Schemas
# ============================================================================

class QueryRequest(BaseModel):
    """
    Request model for recommendation queries.
    
    Attributes:
        query: Natural language query describing the desired candidate profile
               e.g., "I need a Java developer who is also a good collaborator"
    
    Example:
        {
            "query": "Python developer with leadership skills"
        }
    """
    query: str = Field(
        ...,
        description="Natural language query describing candidate requirements",
        min_length=1,
        example="I need a Java developer who is also a good collaborator"
    )


class Recommendation(BaseModel):
    """
    Individual assessment recommendation.
    
    Attributes:
        name: Assessment name
        url: Link to the assessment details
        description: Brief description of what the assessment measures
        adaptive_support: Whether adaptive testing is supported
        duration: Duration of the assessment in minutes
        remote_support: Whether remote proctoring is available
        test_type: List of test types/categories
    
    Example:
        {
            "name": "Java Programming Test",
            "url": "https://example.com/test",
            "description": "Assesses Java coding skills",
            "adaptive_support": "Yes",
            "duration": 60,
            "remote_support": "Yes",
            "test_type": ["Technical", "Programming"]
        }
    """
    name: str
    url: str
    description: str
    adaptive_support: str
    duration: int
    remote_support: str
    test_type: List[str]


class RecommendationResponse(BaseModel):
    """
    Response model containing list of recommended assessments.
    
    Attributes:
        recommended_assessments: List of Recommendation objects
    
    Example:
        {
            "recommended_assessments": [
                {
                    "name": "Java Programming Test",
                    "url": "https://example.com/test",
                    "description": "Assesses Java coding skills",
                    "adaptive_support": "Yes",
                    "duration": 60,
                    "remote_support": "Yes",
                    "test_type": ["Technical", "Programming"]
                }
            ]
        }
    """
    recommended_assessments: List[Recommendation]


# ============================================================================
# FastAPI Application Setup
# ============================================================================

# Initialize FastAPI app
app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="GenAI-powered system for recommending SHL assessments based on recruiter queries",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize the Recommendation Engine (loaded once at startup)
print("\n" + "=" * 70)
print("Starting FastAPI Application")
print("=" * 70)
print("Loading environment variables from .env file...")

try:
    engine = RecommendationEngine()
    print("\n✓ Recommendation Engine loaded successfully")
    print("✓ API Server ready to handle requests")
    print("=" * 70 + "\n")
except Exception as e:
    print(f"\n✗ Failed to initialize Recommendation Engine: {e}")
    print("=" * 70 + "\n")
    raise


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Simple JSON response indicating the service is healthy
    
    Example:
        GET /health
        Response: {"status": "healthy"}
    """
    return {"status": "healthy"}


@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(query: QueryRequest):
    """
    Get assessment recommendations based on a natural language query.
    
    This endpoint processes recruiter queries and returns relevant SHL assessments
    using a RAG-based recommendation engine powered by vector embeddings.
    
    Args:
        query: QueryRequest containing the recruiter's query
    
    Returns:
        RecommendationResponse with a list of recommended assessments
    
    Raises:
        HTTPException: If an error occurs during recommendation processing
    
    Example:
        POST /recommend
        Body: {"query": "I need a Java developer who is also a good collaborator"}
        Response: {
            "recommended_assessments": [
                {
                    "name": "Java Programming Test",
                    "url": "https://example.com/test",
                    "description": "Assesses Java coding skills",
                    "adaptive_support": "Yes",
                    "duration": 60,
                    "remote_support": "Yes",
                    "test_type": ["Technical", "Programming"]
                }
            ]
        }
    """
    try:
        # Log the incoming request
        print(f"\n{'=' * 70}")
        print(f"API Request Received")
        print(f"{'=' * 70}")
        print(f"Query: {query.query}")
        print(f"{'=' * 70}\n")
        
        # ===================================================================
        # CRITICAL UPGRADE: Call the Recommendation Engine "Brain"
        # ===================================================================
        # The engine now returns a List[Dict] with full product data
        products = engine.get_recommendations(query.query)
        
        # Log the results for debugging
        print("\n" + "=" * 70)
        print("Recommendation Engine Output:")
        print("=" * 70)
        print(f"Found {len(products)} recommendations")
        for i, product in enumerate(products, 1):
            print(f"  {i}. {product.get('name', 'Unknown')}")
        print("=" * 70 + "\n")
        
        # ===================================================================
        # CRITICAL: Convert List[Dict] to Pydantic RecommendationResponse
        # ===================================================================
        # Pydantic will automatically validate each dictionary against the
        # Recommendation model schema. If any field is missing or wrong type,
        # it will raise a ValidationError which FastAPI will handle gracefully.
        
        return RecommendationResponse(recommended_assessments=products)
    
    except Exception as e:
        # Log the error with full details
        print(f"\n{'=' * 70}")
        print(f"ERROR: Failed to process recommendation request")
        print(f"{'=' * 70}")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"{'=' * 70}\n")
        
        # Import traceback for detailed error logging
        import traceback
        traceback.print_exc()
        
        # Return HTTP 500 error with details
        raise HTTPException(
            status_code=500,
            detail=f"Error processing recommendation: {str(e)}"
        )


@app.get("/")
async def root():
    """
    Root endpoint - provides API information and available endpoints.
    
    Returns:
        JSON with API metadata and endpoint documentation
    
    Example:
        GET /
        Response: {
            "service": "SHL Assessment Recommendation API",
            "version": "1.0.0",
            ...
        }
    """
    return {
        "service": "SHL Assessment Recommendation API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "GET /health - Check API health status",
            "recommend": "POST /recommend - Get assessment recommendations",
            "docs": "GET /docs - Interactive API documentation (Swagger UI)",
            "redoc": "GET /redoc - Alternative API documentation (ReDoc)"
        },
        "description": "GenAI-powered assessment recommendation system using RAG and vector embeddings",
        "features": {
            "rag_powered": "Uses Retrieval-Augmented Generation for intelligent recommendations",
            "vector_search": "Powered by ChromaDB and OpenAI embeddings",
            "smart_parsing": "Automatically extracts and validates assessment data",
            "balanced_recommendations": "Suggests mix of technical and behavioral assessments"
        }
    }


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    """
    Run the FastAPI application using Uvicorn.
    
    Access the API at:
        - API: http://localhost:8000
        - Interactive Docs: http://localhost:8000/docs
        - Alternative Docs: http://localhost:8000/redoc
        - Health Check: http://localhost:8000/health
    
    Configuration:
        - Host: 0.0.0.0 (accessible from network)
        - Port: 8000
        - Reload: True (auto-reload on code changes)
        - Log Level: info
    
    Testing the API:
        1. Start the server: python main.py
        2. Visit http://localhost:8000/docs for interactive testing
        3. Or use curl:
           curl -X POST http://localhost:8000/recommend \
                -H "Content-Type: application/json" \
                -d '{"query": "Java developer with teamwork skills"}'
    """
    print("\n" + "=" * 70)
    print("Starting Uvicorn Server")
    print("=" * 70)
    print("Access the API at:")
    print("  • API:          http://localhost:8000")
    print("  • Docs:         http://localhost:8000/docs")
    print("  • ReDoc:        http://localhost:8000/redoc")
    print("  • Health Check: http://localhost:8000/health")
    print("=" * 70)
    print("\nTip: Visit /docs for interactive API testing!")
    print("=" * 70 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (disable in production)
        log_level="info"
    )