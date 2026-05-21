from fastapi import APIRouter

from datetime import date

from typing import Optional

from sqlalchemy import text

from app.core.db import engine

from app.services.forecast_service import get_demand_forecast


router = APIRouter(tags=["Demand Forecasting"])


@router.get("/forecast")
def demand_forecast(

    company_code: str,

    page: int = 1,

    pageSize: int = 10,

    search: str = "",

    filter: str = "monthly",

    start_date: Optional[date] = None,

    end_date: Optional[date] = None
):

    # ============================================================
    # EMPTY COMPANY CODE VALIDATION
    # ============================================================

    if not company_code or not company_code.strip():

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

            "message": "Invalid company name",

            "error_code": "INVALID_COMPANY_CODE"
        }

    # ============================================================
    # CALL SERVICE
    # ============================================================

    return get_demand_forecast(

        company_code,

        page,

        pageSize,

        search,

        filter,

        start_date,

        end_date
    )