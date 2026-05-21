from fastapi import APIRouter, Query
from typing import Optional

from app.services.top_selling_service import get_top_selling

router = APIRouter(tags=["Top Selling Products Analysis"])


@router.get("/top-selling")
def top_selling(

    page: int = 1,

    pageSize: int = 10,

    search: str = "",

    filter: str = "overall",

    month: Optional[str] = None,

    year: Optional[int] = None,

    start_date: str = Query(None),

    end_date: str = Query(None)
):

    return get_top_selling(

        page,

        pageSize,

        search,

        filter,

        month,

        year,

        start_date,

        end_date
    )