from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlmodel import Session, select
from decouple import config
from ..models import Site
from ..database import get_session

ADMIN_API_KEY = config("ADMIN_API_KEY", default=None)

router = APIRouter(prefix="/sites", tags=["Sites"])

async def verify_admin_key(x_admin_key: str = Header(None)):
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_API_KEY not configured on server"
        )
    if x_admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Admin API Key"
        )

@router.post("/", response_model=Site, dependencies=[Depends(verify_admin_key)])
async def create_site(site: Site, session: Session = Depends(get_session)):
    session.add(site)
    session.commit()
    session.refresh(site)
    return site

@router.post("/bulk/", response_model=List[Site], dependencies=[Depends(verify_admin_key)])
async def create_sites_bulk(sites: List[Site], session: Session = Depends(get_session)):
    with session:
        for site in sites:
            session.add(site)
        session.commit()
        for site in sites:
            session.refresh(site)
        return sites

@router.get("/", response_model=List[Site])
async def list_sites(session: Session = Depends(get_session)):
    sites = session.exec(select(Site)).all()
    return sites
