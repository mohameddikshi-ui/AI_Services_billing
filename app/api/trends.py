from fastapi import APIRouter, Query

from sqlalchemy import text

from app.core.db import engine

from app.services.trend_service import (
    get_trend_analysis
)


router = APIRouter(

    tags=["Trend Analysis"]
)


@router.get("/trends")
def trends(

    company_code: str,

    page: int = Query(1),

    pageSize: int = Query(10),

    search: str = Query(""),

    filter: str = Query("monthly")
):

    # ============================================================
    # EMPTY COMPANY CODE VALIDATION
    # ============================================================

    if not company_code.strip():

        return {

            "success": False,

            "message": "Company code is required.",

            "error_code": "COMPANY_CODE_REQUIRED"
        }

    # ============================================================
    # COMPANY EXIST CHECK
    # ============================================================

    check_query = text("""

    SELECT COUNT(*) AS total

    FROM COMPANY

    WHERE LTRIM(RTRIM(fCompCode)) = :company_code

    """)

    with engine.connect() as conn:

        result = conn.execute(

            check_query,

            {

                "company_code": company_code
            }

        ).scalar()

    # ============================================================
    # INVALID COMPANY
    # ============================================================

    if result == 0:

        return {

            "success": False,

            "message": "Invalid company name.",

            "error_code": "INVALID_COMPANY_CODE"
        }

    # ============================================================
    # CALL SERVICE
    # ============================================================

    return get_trend_analysis(

        company_code,

        page,

        pageSize,

        search,

        filter
    )