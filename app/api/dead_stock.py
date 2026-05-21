from fastapi import APIRouter, Query

from sqlalchemy import text

from app.core.db import engine

from app.services.dead_stock_service import (
    get_dead_stock
)


router = APIRouter(

    tags=["Dead Stock Analysis"]
)


@router.get("/dead-stock")
def dead_stock(

    company_code: str,

    page: int = 1,

    pageSize: int = 10,

    search: str = "",

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

    return get_dead_stock(

        company_code,

        page,

        pageSize,

        search,

        start_date,

        end_date
    )