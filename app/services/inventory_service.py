from app.repository.inventory_repo import get_inventory_data

from app.utils.pagination import get_pagination

from app.utils.response import success_response


def get_demand_level(avg):

    if avg > 2:

        return "HIGH"

    elif avg > 0.5:

        return "MEDIUM"

    return "LOW"


def calculate_inventory(

    company_code,

    page,

    pageSize,

    search,

    filter_type="monthly",

    month=None,

    year=None,

    start_date=None,

    end_date=None
):

    offset, limit = get_pagination(
        page,
        pageSize
    )

    data = get_inventory_data(

        search,

        offset,

        limit,

        filter_type,

        month,

        year,

        company_code,

        start_date,

        end_date
    )

    result = []

    for item in data:

        current_stock = int(
            item.get("current_stock") or 0
        )

        historical_sales = float(
            item.get("historical_sales") or 0
        )

        avg_daily_sales = float(
            item.get("avg_daily_sales") or 0
        )

        # ==========================================
        # REQUIRED STOCK LOGIC
        # ==========================================

        if filter_type == "weekly":

            required_stock = round(
                avg_daily_sales * 7
            )

        else:

            required_stock = round(
                avg_daily_sales * 30
            )

        recommended_stock = round(
            required_stock * 1.2
        )

        # ==========================================
        # STOCK STATUS LOGIC
        # ==========================================

        if current_stock <= 0:

            stock_status = "OUT OF STOCK"

        elif current_stock < required_stock:

            stock_status = "LOW STOCK"

        elif current_stock < recommended_stock:

            stock_status = "NEED REORDER"

        else:

            stock_status = "SUFFICIENT STOCK"

        result.append({

            "product_id":
            item["Fitemcode"],

            "product_name":
            item["FitemName"],

            "category":
            item.get("category"),

            "current_stock":
            current_stock,

            "historical_sales":
            historical_sales,

            "average_daily_sales":
            round(
                avg_daily_sales,
                2
            ),

            "required_stock":
            required_stock,

            "recommended_stock":
            recommended_stock,

            "demand_level":
            get_demand_level(
                avg_daily_sales
            ),

            "stock_status":
            stock_status
        })

    return success_response(

        message=
        "Inventory recommendation fetched successfully.",

        data=result,

        page=page,

        pageSize=pageSize,

        total_records=len(result),

        extra={

            "company_code":
            company_code,

            "filter":
            filter_type,

            "month":
            month,

            "year":
            year,

            "start_date":
            start_date,

            "end_date":
            end_date
        }
    )