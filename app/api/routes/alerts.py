from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.alert import PriceAlert
from app.schemas.alert import AlertCreate, AlertRead, AlertUpdate
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertRead, status_code=201)
async def create_alert(payload: AlertCreate, session: AsyncSession = Depends(get_session)):
    return await AlertService(session).create(payload)


@router.get("", response_model=list[AlertRead])
async def list_alerts(session: AsyncSession = Depends(get_session)):
    return (await session.scalars(select(PriceAlert).order_by(PriceAlert.created_at.desc()))).all()


@router.patch("/{alert_id}", response_model=AlertRead)
async def update_alert(alert_id: int, payload: AlertUpdate, session: AsyncSession = Depends(get_session)):
    alert = await session.get(PriceAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="alert not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(alert, key, str(value) if key == "email" and value else value)
    await session.commit()
    await session.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(alert_id: int, session: AsyncSession = Depends(get_session)):
    alert = await session.get(PriceAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="alert not found")
    await session.delete(alert)
    await session.commit()

