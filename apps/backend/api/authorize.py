"""
Authorization API — Terminal3 authorization endpoint.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.engine import get_db
from models import AuthorizationLog
from schemas import AuthorizationRequest, AuthorizationResponse
from services.authorization.terminal3_client import Terminal3Client

router = APIRouter(tags=["Authorization"])


@router.post("/authorize", response_model=AuthorizationResponse)
async def authorize_action(request: AuthorizationRequest, db: Session = Depends(get_db)):
    """
    Authorize a single agent action through Terminal3.
    """
    terminal3 = Terminal3Client.get_instance()
    result = terminal3.process_action(
        agent_name=request.agent_name,
        action=request.action,
        asset_id=request.asset_id,
        reason=request.reason,
    )

    auth_data = result["authorization"]

    # Persist to DB
    db_auth = AuthorizationLog(
        agent_name=request.agent_name,
        action=request.action,
        asset_id=request.asset_id,
        authorized=auth_data["authorized"],
        policy_applied=auth_data["policy_applied"],
        reason=auth_data["reason"],
        execution_id=auth_data["execution_id"],
    )
    db.add(db_auth)
    db.commit()

    return AuthorizationResponse(
        authorized=auth_data["authorized"],
        policy_applied=auth_data["policy_applied"],
        execution_id=auth_data["execution_id"],
        reason=auth_data["reason"],
    )
