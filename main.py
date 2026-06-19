import time

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import API_KEY_SECRET, OPENROUTER_API_KEY, SUPABASE_URL
from extractor import extract_fields
from schemas import AnalyzeRequest, AnalyzeResponse
from scoring import calculate_trust_score
from scraper import scrape_domain
import re 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="AI Tool Risk Profiler",
    description="Automated security scoring for AI tools.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/demo")
async def demo():
    return FileResponse("index.html")

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    request: AnalyzeRequest,
    x_api_key: str = Header(None),
) -> AnalyzeResponse:
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API key.")

    raw = request.domain.strip().lower()
    raw = re.sub(r"^https?://", "", raw)   # strip http:// or https://
    raw = re.sub(r"/.*$", "", raw)          # strip any path after the domain
    domain = raw.strip("/")
    start = time.time()

    pages = await scrape_domain(domain)
    if not pages:
        return AnalyzeResponse(
            success=False,
            domain=domain,
            error="Could not fetch website. It may be down or blocking requests.",
        )

    fields = await extract_fields(pages)
    if not fields:
        return AnalyzeResponse(
            success=False,
            domain=domain,
            error="Failed to extract information from the website content.",
        )

    trust_score = calculate_trust_score(fields)
  

    return AnalyzeResponse(
        success=True,
        domain=domain,
        trust_score=trust_score,
        data_retention=fields.get("data_retention"),
        trains_on_input=fields.get("trains_on_input"),
        soc2_certified=fields.get("soc2_certified"),
        hipaa_compliant=fields.get("hipaa_compliant"),
        gdpr_compliant=fields.get("gdpr_compliant"),
        iso_27001=fields.get("iso_27001"),
        breach_mentions=fields.get("breach_mentions"),
        processing_time_ms=int((time.time() - start) * 1000),
    )


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "supabase_configured": bool(SUPABASE_URL),
        "openrouter_configured": bool(OPENROUTER_API_KEY),
    }


@app.get("/")
async def root():
    return {
        "name": "AI Tool Risk Profiler",
        "version": "1.0.0",
        "docs": "/docs",
    }