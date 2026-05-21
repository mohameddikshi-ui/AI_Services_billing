import math

from app.repository.sales_repo import (
    get_purchase_patterns
)

from app.utils.pagination import get_pagination

from app.utils.response import (
    success_response
)


def analyze_purchase_patterns(

    company_code,

    page,

    pageSize,

    search,

    filter_type,

    start_date=None,

    end_date=None
):

    offset, limit = get_pagination(
        page,
        pageSize
    )

    response = get_purchase_patterns(

        search,

        offset,

        limit,

        filter_type,

        company_code,

        start_date,

        end_date
    )

    data = response["records"]

    total_records = response["total_records"]

    total_pages = math.ceil(
        total_records / limit
    ) if limit > 0 else 1

    result = []

    for item in data:

        pair_count = int(
            item.get("pair_count") or 0
        )

        # ==========================================
        # AI ASSOCIATION STRENGTH
        # ==========================================

        if pair_count >= 100:

            strength = "VERY HIGH"

        elif pair_count >= 50:

            strength = "HIGH"

        elif pair_count >= 20:

            strength = "MEDIUM"

        else:

            strength = "LOW"

        result.append({

            "primary_product":
            item["primary_product"],

            "frequently_bought_with":
            item["paired_product"],

            "pair_count":
            pair_count,

            "strength":
            strength
        })

    # ==========================================
    # ANALYZED PERIOD
    # ==========================================

    analyzed_period = "Overall"

    if filter_type == "weekly":

        analyzed_period = "Last 7 Days"

    elif filter_type == "monthly":

        analyzed_period = "Last 1 Month"

    elif start_date and end_date:

        analyzed_period = (
            f"{start_date} to {end_date}"
        )

    # ==========================================
    # FINAL RESPONSE
    # ==========================================

    return success_response(

        message=
        "Purchase patterns analyzed successfully.",

        data=result,

        page=page,

        pageSize=limit,

        total_records=total_records,

        extra={

            "company_code":
            company_code,

            "total_pages":
            total_pages,

            "filter":
            filter_type,

            "analyzed_period":
            analyzed_period,

            "start_date":
            start_date,

            "end_date":
            end_date
        }
    )