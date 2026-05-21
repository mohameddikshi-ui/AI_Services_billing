from fastapi import APIRouter, Query

from typing import Optional

from sqlalchemy import text

from app.core.db import engine

from app.services.top_selling_service import get_top_selling


router = APIRouter(

    tags=["Top Selling Products Analysis"]
)


@router.get("/top-selling")
def top_selling(

    company_code: str,

    page: int = 1,

    pageSize: int = 10,

    search: str = "",

    filter: str = "overall",

    month: Optional[str] = None,

    year: Optional[int] = None,

    start_date: str = Query(None),

    end_date: str = Query(None)
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

    return get_top_selling(

        company_code,

        page,

        pageSize,

        search,

        filter,

        month,

        year,

        start_date,

        end_date
    )