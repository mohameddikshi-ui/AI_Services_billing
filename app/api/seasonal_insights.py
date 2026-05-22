from fastapi import APIRouter

from sqlalchemy import text

from app.core.db import engine

from app.services.seasonal_service import (
    analyze_seasonal_insights
)


router = APIRouter(

    tags=["Seasonal Insights"]
)


@router.get("/seasonal-insights")
def seasonal_insights(

    company_code: str,

    page: int = 1,

    pageSize: int = 10,

    month: str = None,

    year: int = None,

    start_date: str = None,

    end_date: str = None
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

            "message": "Invalid company code.",

            "error_code": "INVALID_COMPANY_CODE"
        }

    # ============================================================
    # CALL SERVICE
    # ============================================================

    return analyze_seasonal_insights(

        company_code,

        page,

        pageSize,

        month,

        year,

        start_date,

        end_date
    )