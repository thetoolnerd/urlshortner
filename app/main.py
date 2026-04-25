from datetime import datetime, timezone
import os

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Link
from .schemas import LinkResponse, LinkStatsResponse, ShortenRequest
from .utils import generate_short_code

app = FastAPI(title="URL Shortener", version="0.1.0")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


def _build_short_url(request: Request, code: str) -> str:
    app_base_url = os.getenv("APP_BASE_URL")
    if app_base_url:
        return f"{app_base_url.rstrip('/')}/{code}"
    return str(request.url_for("redirect_to_long_url", code=code))


@app.get("/health")
def health_check():
    return {"ok": True}


@app.post("/api/v1/shorten", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def create_short_url(payload: ShortenRequest, request: Request, db: Session = Depends(get_db)):
    if payload.expires_at and payload.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="expires_at must be in the future")

    is_custom = payload.custom_alias is not None

    if is_custom:
        existing = db.scalar(select(Link).where(Link.short_code == payload.custom_alias))
        if existing:
            raise HTTPException(status_code=409, detail="custom alias already exists")
        code = payload.custom_alias
    else:
        code = generate_short_code()

    link = Link(
        short_code=code,
        long_url=str(payload.url),
        expires_at=payload.expires_at,
        is_custom=is_custom,
        redirect_status_code=payload.redirect_status_code,
    )
    db.add(link)

    if not is_custom:
        max_retries = 5
        for _ in range(max_retries):
            try:
                db.commit()
                db.refresh(link)
                break
            except IntegrityError:
                db.rollback()
                link.short_code = generate_short_code()
                db.add(link)
        else:
            raise HTTPException(status_code=500, detail="failed to generate unique short code")
    else:
        try:
            db.commit()
            db.refresh(link)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="custom alias already exists")

    return LinkResponse(
        id=link.id,
        short_code=link.short_code,
        short_url=_build_short_url(request, link.short_code),
        long_url=link.long_url,
        created_at=link.created_at,
        expires_at=link.expires_at,
        is_custom=link.is_custom,
        redirect_status_code=link.redirect_status_code,
    )


@app.get("/api/v1/links/{code}/stats", response_model=LinkStatsResponse)
def get_link_stats(code: str, db: Session = Depends(get_db)):
    link = db.scalar(select(Link).where(Link.short_code == code))
    if not link:
        raise HTTPException(status_code=404, detail="short code not found")

    return LinkStatsResponse(
        short_code=link.short_code,
        long_url=link.long_url,
        created_at=link.created_at,
        expires_at=link.expires_at,
        click_count=link.click_count,
        redirect_status_code=link.redirect_status_code,
    )


@app.get("/{code}", name="redirect_to_long_url")
def redirect_to_long_url(code: str, db: Session = Depends(get_db)):
    link = db.scalar(select(Link).where(Link.short_code == code))
    if not link:
        raise HTTPException(status_code=404, detail="short code not found")

    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="short code has expired")

    link.click_count += 1
    db.commit()

    return RedirectResponse(url=link.long_url, status_code=link.redirect_status_code)
