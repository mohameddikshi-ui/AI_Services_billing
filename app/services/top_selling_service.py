from app.repository.sales_repo import get_top_selling_data

from app.utils.pagination import get_pagination

from app.utils.response import (
    success_response
)


def format_currency(amount):

    if amount >= 10000000:

        return f"₹{round(amount / 10000000, 2)} Cr"

    elif amount >= 100000:

        return f"₹{round(amount / 100000, 2)} Lakh"

    else:

        return f"₹{round(amount, 2):,}"


def get_top_selling(

    page,

    pageSize,

    search,

    filter_type,

    start_date,

    end_date
):

    offset, limit = get_pagination(
        page,
        pageSize
    )

    data = get_top_selling_data(

        search,

        offset,

        pageSize,

        filter_type,

        start_date,

        end_date
    )

    result = []

    for item in data:

        result.append({

            "product_id":
            item["fItemcode"],

            "product_name":
            item["FitemName"],

            "category":
            item.get("category"),

            "total_qty_sold":
            item.get("total_qty", 0),

            "total_sales_amount":
            format_currency(
                item.get("total_sales", 0)
            ),

            "currency":
            item["currency"]
        })

    return success_response(

        message=
        "Top selling products analyzed successfully.",

        data=result,

        page=page,

        pageSize=pageSize,

        extra={

            "filter": filter_type
        }
    )