import math

from app.repository.stock_repo import get_alert_data

from app.utils.pagination import get_pagination

from app.utils.response import success_response


def get_smart_alerts(

    company_code,

    page,

    pageSize,

    search,

    filter_type="monthly",

    start_date=None,

    end_date=None
):

    offset, limit = get_pagination(
        page,
        pageSize
    )

    # ==========================================
    # FETCH ALERT DATA
    # ==========================================

    response = get_alert_data(

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

    # ==========================================
    # PERIOD LABEL
    # ==========================================

    if filter_type == "weekly":

        analyzed_period = "Last 7 Days"

    else:

        analyzed_period = "Last 1 Month"

    # ==========================================
    # LOOP
    # ==========================================

    for item in data:

        current_stock = int(
            item.get("current_stock") or 0
        )

        recent_sales = float(
            item.get("recent_sales") or 0
        )

        avg_daily_sales = float(
            item.get("avg_daily_sales") or 0
        )

        # ==========================================
        # REQUIRED STOCK CALCULATION
        # ==========================================

        if filter_type == "weekly":

            required_stock = round(
                avg_daily_sales * 7
            )

        else:

            required_stock = round(
                avg_daily_sales * 30
            )

        # ==========================================
        # SAFETY STOCK
        # ==========================================

        recommended_stock = round(
            required_stock * 1.2
        )

        # ==========================================
        # ALERT ENGINE
        # ==========================================

        alert_type = "NORMAL"

        severity = "LOW"

        recommendation = (
            "Stock level is stable"
        )

        if current_stock <= 0:

            alert_type = "OUT_OF_STOCK"

            severity = "CRITICAL"

            recommendation = (
                "Restock immediately"
            )

        elif current_stock < required_stock:

            alert_type = "LOW_STOCK"

            severity = "HIGH"

            recommendation = (
                "Stock is below expected demand. Reorder soon"
            )

        elif current_stock < recommended_stock:

            alert_type = "REORDER_REQUIRED"

            severity = "MEDIUM"

            recommendation = (
                "Stock is below recommended safety level"
            )

        elif avg_daily_sales >= 2:

            alert_type = "FAST_MOVING"

            severity = "MEDIUM"

            recommendation = (
                "Monitor stock frequently due to high sales speed"
            )

        elif recent_sales == 0:

            alert_type = "NO_RECENT_SALES"

            severity = "LOW"

            recommendation = (
                "Consider promotion or clearance"
            )

        # ==========================================
        # FINAL RESULT
        # ==========================================

        result.append({

            "product_id":
            item["Fitemcode"],

            "product_name":
            item["FitemName"],

            "category":
            item.get("category"),

            "current_stock":
            current_stock,

            "recent_sales":
            recent_sales,

            "average_daily_sales":
            round(avg_daily_sales, 2),

            "required_stock":
            required_stock,

            "recommended_stock":
            recommended_stock,

            "alert_type":
            alert_type,

            "severity":
            severity,

            "recommendation":
            recommendation
        })

    # ==========================================
    # CUSTOM DATE LABEL
    # ==========================================

    if start_date and end_date:

        analyzed_period = (
            f"{start_date} to {end_date}"
        )

    # ==========================================
    # FINAL RESPONSE
    # ==========================================

    return success_response(

        message=
        "Smart alerts fetched successfully.",

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