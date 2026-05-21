from app.repository.sales_repo import (
    get_seasonal_insights
)

from app.utils.pagination import (
    get_pagination
)

from app.utils.response import (
    success_response
)


def analyze_seasonal_insights(

    company_code,

    page,

    pageSize,

    month,

    start_date=None,

    end_date=None
):

    # ============================================================
    # PAGINATION
    # ============================================================

    offset, limit = get_pagination(

        page,

        pageSize
    )

    # ============================================================
    # FETCH DB DATA
    # ============================================================

    data = get_seasonal_insights(

        company_code,

        month,

        offset,

        limit,

        start_date,

        end_date
    )

    result = []

    # ============================================================
    # SEASONAL ANALYSIS
    # ============================================================

    for item in data:

        total_orders = int(
            item.get("total_orders") or 0
        )

        # ============================================================
        # DEMAND CLASSIFICATION
        # ============================================================

        if total_orders >= 1000:

            seasonal_trend = "PEAK DEMAND"

        elif total_orders >= 500:

            seasonal_trend = "HIGH DEMAND"

        elif total_orders >= 100:

            seasonal_trend = "MODERATE DEMAND"

        else:

            seasonal_trend = "LOW DEMAND"

        # ============================================================
        # DATA CONFIDENCE
        # ============================================================

        if total_orders >= 1000:

            data_confidence = "HIGH"

        elif total_orders >= 100:

            data_confidence = "MEDIUM"

        else:

            data_confidence = "LOW"

        # ============================================================
        # FINAL RESPONSE OBJECT
        # ============================================================

        result.append({

            "month":
            item.get("month_name"),

            "category":
            item.get("category"),

            "total_orders":
            total_orders,

            "seasonal_trend":
            seasonal_trend,

            "data_confidence":
            data_confidence
        })

    # ============================================================
    # SUCCESS RESPONSE
    # ============================================================

    return success_response(

        message=
        "Seasonal insights analyzed successfully.",

        data=result,

        page=page,

        pageSize=pageSize,

        total_records=len(result),

        extra={

            "company_code":
            company_code,

            "month":
            month,

            "start_date":
            start_date,

            "end_date":
            end_date
        }
    )