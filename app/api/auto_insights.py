from fastapi import APIRouter

from sqlalchemy import text

from app.core.db import engine

from app.services.auto_insights_service import (
    generate_auto_insights
)


router = APIRouter(

    tags=["AI Auto Insights"]
)


@router.get("/auto-insights")
def auto_insights(

    company_code: str,

    page: int = 1,

    pageSize: int = 10,

    filter: str = "overall",

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

            "message": "Invalid company name.",

            "error_code": "INVALID_COMPANY_CODE"
        }

    # ============================================================
    # CALL SERVICE
    # ============================================================

    return generate_auto_insights(

        company_code,

        page,

        pageSize,

        filter,

        start_date,

        end_date
    )