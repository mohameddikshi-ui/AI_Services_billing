from app.repository.sales_repo import get_forecast_data

from app.utils.pagination import get_pagination

from app.utils.response import success_response


def get_demand_forecast(

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

    data = get_forecast_data(

        search,

        offset,

        limit,

        filter_type,

        company_code,

        start_date,

        end_date
    )

    result = []

    for item in data:

        total_sales = float(
            item.get("total_sales") or 0
        )

        avg_sales = float(
            item.get("avg_sales") or 0
        )

        active_days = int(
            item.get("active_days") or 0
        )

        # ======================================================
        # PREDICTION ENGINE
        # ======================================================

        if filter_type == "weekly":

            predicted_sales = round(
                avg_sales * 7
            )

        else:

            predicted_sales = round(
                avg_sales * 30
            )

        # ======================================================
        # FORECAST LEVEL
        # ======================================================

        if predicted_sales >= 50:

            forecast_level = "HIGH DEMAND"

        elif predicted_sales >= 20:

            forecast_level = "MEDIUM DEMAND"

        else:

            forecast_level = "LOW DEMAND"

        # ======================================================
        # RECOMMENDED STOCK
        # ======================================================

        recommended_stock = round(
            predicted_sales * 1.2
        )

        # ======================================================
        # FINAL RESULT
        # ======================================================

        result.append({

            "product_id":
            item["Fitemcode"],

            "product_name":
            item["FitemName"],

            "category":
            item.get("category"),

            "historical_sales":
            total_sales,

            "average_daily_sales":
            round(avg_sales, 2),

            "active_sales_days":
            active_days,

            "predicted_sales":
            predicted_sales,

            "recommended_stock":
            recommended_stock,

            "forecast_level":
            forecast_level
        })

    # ==========================================================
    # FINAL RESPONSE
    # ==========================================================

    return success_response(

        message=
        "Demand forecast generated successfully.",

        data=result,

        page=page,

        pageSize=pageSize,

        total_records=len(result),

        extra={

            "company_code":
            company_code,

            "filter":
            filter_type,

            "start_date":
            start_date,

            "end_date":
            end_date
        }
    )