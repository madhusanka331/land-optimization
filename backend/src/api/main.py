"""
FastAPI Application - AI Land Optimization Backend
Main application entry point with API routes, CORS, and documentation.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from loguru import logger
import time

from ..config.settings import settings
from .database import init_db
from .routes import optimization


# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Continue anyway for development

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## AI-Based Land Optimization API

    Optimize house layouts using **Genetic Algorithm** and **Multi-Objective Optimization**.

    ### Features

    * 🧬 **Genetic Algorithm Optimization** - Evolve optimal house layouts
    * 📐 **Sri Lankan Building Rules** - UDA regulation compliance
    * 🎨 **Floor Plan Visualization** - Professional PNG images
    * 📊 **Multi-Objective Scoring** - Space, sunlight, privacy, circulation, regulations
    * 💾 **Optimization History** - Save and retrieve past results
    * 🔍 **Search & Filter** - Find optimizations by parameters

    ### How It Works

    1. **Validate** land parameters using `/optimization/validate`
    2. **Optimize** layout using `/optimization/optimize`
    3. **View** floor plan visualization
    4. **Save** results to database
    5. **Retrieve** past optimizations from history

    ### Technology Stack

    - **AI Engine**: PyGAD (Genetic Algorithm)
    - **Framework**: FastAPI + Pydantic
    - **Database**: PostgreSQL + SQLAlchemy
    - **Visualization**: Matplotlib
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all requests with timing information.
    """
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    # Add custom header
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Exception handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors with detailed messages.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    logger.warning(f"Validation error: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation Error",
            "message": "Invalid request parameters",
            "details": errors,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


# Include routers
app.include_router(
    optimization.router,
    prefix=settings.API_PREFIX,
)


# Root endpoints

@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Get API information and status"
)
async def root():
    """
    API root endpoint.

    Returns API information and available endpoints.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "online",
        "docs": "/docs",
        "api_prefix": settings.API_PREFIX,
        "endpoints": {
            "validate": f"{settings.API_PREFIX}/optimization/validate",
            "optimize": f"{settings.API_PREFIX}/optimization/optimize",
            "history": f"{settings.API_PREFIX}/optimization/history",
            "visualization": f"{settings.API_PREFIX}/optimization/visualization/{{filename}}",
        }
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check API health and database connectivity"
)
async def health_check():
    """
    Health check endpoint.

    Returns API health status and component status.
    """
    # Check database connection
    db_status = "healthy"
    try:
        from .database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Database health check failed: {e}")

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "components": {
            "api": "healthy",
            "database": db_status,
            "ai_engine": "healthy",
        }
    }


@app.get(
    settings.API_PREFIX + "/info",
    tags=["Info"],
    summary="System Information",
    description="Get system configuration and parameters"
)
async def system_info():
    """
    Get system configuration information.

    Returns GA parameters, building rules, and system settings.
    """
    return {
        "genetic_algorithm": {
            "default_generations": settings.GA_GENERATIONS,
            "default_population_size": settings.GA_POPULATION_SIZE,
            "mutation_rate": settings.GA_MUTATION_RATE,
            "crossover_rate": settings.GA_CROSSOVER_RATE,
            "tournament_size": settings.GA_TOURNAMENT_SIZE,
        },
        "building_rules": {
            "enabled": settings.ENABLE_SRI_LANKAN_RULES,
            "setback_front": settings.SETBACK_FRONT,
            "setback_side": settings.SETBACK_SIDE,
            "setback_back": settings.SETBACK_BACK,
            "max_coverage_percent": settings.MAX_COVERAGE_PERCENT,
        },
        "api": {
            "prefix": settings.API_PREFIX,
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
            "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
        }
    }


# Run application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
