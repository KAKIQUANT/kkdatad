from datetime import datetime
from sqlalchemy.orm import Session
from kkdatad.utils.models import QueryAnalytics
from typing import Optional

async def log_query(
    db: Session,
    user_id: int,
    query: str,
    execution_time: float,
    rows_returned: int,
    error: Optional[str] = None
) -> None:
    """Log query execution details for analytics"""
    analytics = QueryAnalytics(
        user_id=user_id,
        query=query,
        execution_time=execution_time,
        rows_returned=rows_returned,
        error=error,
        timestamp=datetime.utcnow()
    )
    db.add(analytics)
    db.commit() 