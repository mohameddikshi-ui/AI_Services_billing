from sqlalchemy import text
from app.core.db import engine


CATEGORY_CASE = """
CASE
    WHEN LTRIM(RTRIM(pd.fItemName)) LIKE 'G %' THEN 'Gold'
    WHEN LTRIM(RTRIM(pd.fItemName)) LIKE 'S %' THEN 'Silver'
    WHEN LTRIM(RTRIM(pd.fItemName)) LIKE 'D %' THEN 'Diamond'
    WHEN LTRIM(RTRIM(pd.fItemName)) LIKE 'DIAMOND%' THEN 'Diamond'
    WHEN LTRIM(RTRIM(pd.fItemName)) LIKE '%DIAMOND%' THEN 'Diamond'
    WHEN LTRIM(RTRIM(pd.fItemName)) LIKE 'N %' THEN 'Silver/Other'
    ELSE 'Other'
END
"""

# # ============================================================
# TOP SELLING PRODUCTS
# ============================================================

def get_top_selling_data(search, offset, limit, filter_type, start_date=None, end_date=None):

    date_filter = ""
    custom_date_filter = ""

    if filter_type == "weekly":
        date_filter = "AND it.fDate >= DATEADD(DAY, -7, GETDATE())"

    elif filter_type == "monthly":
        date_filter = "AND it.fDate >= DATEADD(MONTH, -1, GETDATE())"

    if start_date and end_date:
        custom_date_filter = """
        AND it.fDate >= :start_date
        AND it.fDate < DATEADD(DAY, 1, :end_date)
        """

    query = text(f"""
    SELECT 

        it.fItemcode AS fItemcode,

        pd.fItemName AS FitemName,

        {CATEGORY_CASE} AS category,

        SUM(ISNULL(it.fTotQty, 0)) AS total_qty,

        SUM(ISNULL(it.fGms, 0)) AS total_weight,

        ROUND(SUM(ISNULL(it.fAmount, 0)), 2) AS total_sales,

        'INR' AS currency

    FROM ItemTransaction it WITH (NOLOCK)

    JOIN Item pd 
        ON it.fItemcode = pd.fItemcode

    WHERE pd.fItemName LIKE :search

    {date_filter}

    {custom_date_filter}

    GROUP BY 

        it.fItemcode,

        pd.fItemName,

        {CATEGORY_CASE}

    ORDER BY SUM(ISNULL(it.fTotQty, 0)) DESC

    OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
    """)

    params = {

        "search": f"%{search}%",

        "offset": offset,

        "limit": limit
    }

    if start_date and end_date:

        params["start_date"] = start_date

        params["end_date"] = end_date

    with engine.connect() as conn:

        result = conn.execute(query, params)

        return [

            dict(row._mapping)

            for row in result
        ]
# ============================================================
# dead stock and slow moving
# ==========================================================



def get_dead_stock_data(search, offset, limit, start_date=None, end_date=None):

    custom_date_filter = ""

    if start_date and end_date:
        custom_date_filter = """
        AND it.fDate >= :start_date
        AND it.fDate < DATEADD(DAY, 1, :end_date)
        """
    else:
        custom_date_filter = """
        AND it.fDate >= DATEADD(DAY, -30, GETDATE())
        """

    query = text(f"""
    SELECT 
        pd.fItemcode AS Fitemcode,
        pd.fItemName AS FitemName,
        {CATEGORY_CASE} AS category,

        SUM(CASE 
            WHEN it.fDate IS NOT NULL
            THEN ISNULL(it.fTotQty, 0)
            ELSE 0 
        END) AS recent_sales,

        CASE
            WHEN SUM(CASE 
                WHEN it.fDate IS NOT NULL
                THEN ISNULL(it.fTotQty, 0)
                ELSE 0 
            END) = 0
            THEN 'Dead Stock'
            ELSE 'Slow Moving'
        END AS stock_status

    FROM Item pd

    LEFT JOIN ItemTransaction it 
        ON pd.fItemcode = it.fItemcode
        {custom_date_filter}

    WHERE pd.fItemName LIKE :search
    AND pd.fItemcode IS NOT NULL
    AND LTRIM(RTRIM(pd.fItemcode)) <> ''
    AND pd.fItemName NOT LIKE '%GOLD%'
    AND pd.fItemName NOT LIKE '%SILVER%'
    AND pd.fItemName NOT LIKE '%OLD%'
    AND pd.fItemName NOT LIKE '%ROUND OFF%'
    AND pd.fItemName NOT LIKE '%CONVERSION%'

    GROUP BY 
        pd.fItemcode,
        pd.fItemName,
        {CATEGORY_CASE}

    HAVING 
        SUM(CASE 
            WHEN it.fDate IS NOT NULL
            THEN ISNULL(it.fTotQty, 0)
            ELSE 0 
        END) <= 5

    ORDER BY recent_sales ASC, pd.fItemName

    OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
    """)

    params = {
        "search": f"%{search}%",
        "offset": offset,
        "limit": limit
    }

    if start_date and end_date:
        params["start_date"] = start_date
        params["end_date"] = end_date

    with engine.connect() as conn:
        result = conn.execute(query, params)
        return [dict(row._mapping) for row in result]
# ============================================================
# trend analysis
# ==========================================================



def get_trend_data(search, offset, limit, filter_type):

    current_filter = ""
    previous_filter = ""

    if filter_type == "monthly":
        current_filter = "it.fDate >= DATEADD(MONTH, -1, GETDATE())"
        previous_filter = """
        it.fDate >= DATEADD(MONTH, -2, GETDATE())
        AND it.fDate < DATEADD(MONTH, -1, GETDATE())
        """

    elif filter_type == "weekly":
        current_filter = "it.fDate >= DATEADD(DAY, -7, GETDATE())"
        previous_filter = """
        it.fDate >= DATEADD(DAY, -14, GETDATE())
        AND it.fDate < DATEADD(DAY, -7, GETDATE())
        """

    else:
        current_filter = "1=1"
        previous_filter = "1=0"

    query = text(f"""
    SELECT
        pd.fItemcode AS Fitemcode,
        pd.fItemName AS FitemName,
        {CATEGORY_CASE} AS category,

        SUM(
            CASE
                WHEN {current_filter}
                THEN ISNULL(it.fTotQty, 0)
                ELSE 0
            END
        ) AS current_sales,

        SUM(
            CASE
                WHEN {previous_filter}
                THEN ISNULL(it.fTotQty, 0)
                ELSE 0
            END
        ) AS previous_sales

    FROM ItemTransaction it WITH (NOLOCK)

    JOIN Item pd
        ON it.fItemcode = pd.fItemcode

    WHERE pd.fItemName LIKE :search

    GROUP BY
        pd.fItemcode,
        pd.fItemName,
        {CATEGORY_CASE}

    ORDER BY current_sales DESC

    OFFSET :offset ROWS
    FETCH NEXT :limit ROWS ONLY
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "search": f"%{search}%",
            "offset": offset,
            "limit": limit
        })

        return [dict(row._mapping) for row in result]
# ============================================================
# forecasting 
# ==========================================================



def get_forecast_data(

    search,

    offset,

    limit,

    filter_type,

    start_date=None,

    end_date=None
):

    date_filter = ""

    custom_date_filter = ""

    forecast_days = 30

    # ==========================================
    # FILTER LOGIC
    # ==========================================

    if filter_type == "weekly":

        date_filter = """
        AND it.fDate >= DATEADD(DAY, -7, GETDATE())
        """

        forecast_days = 7

    elif filter_type == "monthly":

        date_filter = """
        AND it.fDate >= DATEADD(MONTH, -1, GETDATE())
        """

        forecast_days = 30

    # ==========================================
    # CUSTOM DATE RANGE
    # ==========================================

    if start_date and end_date:

        custom_date_filter = """
        AND it.fDate >= :start_date
        AND it.fDate < DATEADD(DAY, 1, :end_date)
        """

    query = text(f"""

    SELECT

        pd.fItemcode AS Fitemcode,

        pd.fItemName AS FitemName,

        {CATEGORY_CASE} AS category,

        SUM(ISNULL(it.fTotQty, 0)) AS total_sales,

        COUNT(DISTINCT CAST(it.fDate AS DATE)) AS active_days,

        CASE 
            WHEN :forecast_days > 0
            THEN 
                SUM(ISNULL(it.fTotQty, 0)) * 1.0 / :forecast_days
            ELSE 0
        END AS avg_sales

    FROM ItemTransaction it WITH (NOLOCK)

    JOIN Item pd
        ON it.fItemcode = pd.fItemcode

    WHERE

        pd.fItemName LIKE :search

        {date_filter}

        {custom_date_filter}

    GROUP BY

        pd.fItemcode,

        pd.fItemName,

        {CATEGORY_CASE}

    HAVING SUM(ISNULL(it.fTotQty, 0)) > 0

    ORDER BY avg_sales DESC

    OFFSET :offset ROWS
    FETCH NEXT :limit ROWS ONLY

    """)

    params = {

        "search": f"%{search}%",

        "offset": offset,

        "limit": limit,

        "forecast_days": forecast_days
    }

    if start_date and end_date:

        params["start_date"] = start_date

        params["end_date"] = end_date

    with engine.connect() as conn:

        result = conn.execute(query, params)

        return [

            dict(row._mapping)

            for row in result.fetchall()
        ]
# ============================================================
# purchase patterns
# ==========================================================
def get_purchase_patterns(
    search,
    offset,
    limit,
    filter_type,
    start_date=None,
    end_date=None
):

    date_filter = ""

    # Weekly filter
    if filter_type == "weekly":

        date_filter = """

        AND CAST(it1.fDate AS DATE) >=
        CAST(DATEADD(DAY, -7, GETDATE()) AS DATE)

        """

    # Monthly filter
    elif filter_type == "monthly":

        date_filter = """

        AND CAST(it1.fDate AS DATE) >=
        CAST(DATEADD(MONTH, -1, GETDATE()) AS DATE)

        """

    # Custom date filter
    elif start_date and end_date:

        date_filter = """

        AND it1.fDate >= :start_date

        AND it1.fDate < DATEADD(DAY, 1, :end_date)

        """

    # ==========================================
    # MAIN DATA QUERY
    # ==========================================

    query = text(f"""

    SELECT

        i1.fItemName AS primary_product,

        i2.fItemName AS paired_product,

        COUNT(*) AS pair_count

    FROM ItemTransaction it1 WITH (NOLOCK)

    INNER JOIN ItemTransaction it2
        ON it1.fVoucher = it2.fVoucher
        AND it1.fItemcode < it2.fItemcode

    INNER JOIN Item i1
        ON it1.fItemcode = i1.fItemcode

    INNER JOIN Item i2
        ON it2.fItemcode = i2.fItemcode

    WHERE

        (:search = '' OR i1.fItemName LIKE :search)

        AND ISNULL(it1.fTotQty, 0) > 0

        AND ISNULL(it2.fTotQty, 0) > 0

        {date_filter}

    GROUP BY

        i1.fItemName,

        i2.fItemName

    ORDER BY pair_count DESC

    OFFSET :offset ROWS
    FETCH NEXT :limit ROWS ONLY

    """)

    # ==========================================
    # COUNT QUERY
    # ==========================================

    count_query = text(f"""

    SELECT COUNT(*) FROM (

        SELECT

            i1.fItemName AS primary_product,

            i2.fItemName AS paired_product

        FROM ItemTransaction it1 WITH (NOLOCK)

        INNER JOIN ItemTransaction it2
            ON it1.fVoucher = it2.fVoucher
            AND it1.fItemcode < it2.fItemcode

        INNER JOIN Item i1
            ON it1.fItemcode = i1.fItemcode

        INNER JOIN Item i2
            ON it2.fItemcode = i2.fItemcode

        WHERE

            (:search = '' OR i1.fItemName LIKE :search)

            AND ISNULL(it1.fTotQty, 0) > 0

            AND ISNULL(it2.fTotQty, 0) > 0

            {date_filter}

        GROUP BY

            i1.fItemName,

            i2.fItemName

    ) AS grouped_pairs

    """)

    params = {

        "search": f"%{search}%" if search else "",

        "offset": offset,

        "limit": limit
    }

    # Add custom date params only if provided
    if start_date and end_date:

        params["start_date"] = start_date

        params["end_date"] = end_date

    with engine.connect() as conn:

        # Fetch records
        result = conn.execute(
            query,
            params
        )

        records = [
            dict(row._mapping)
            for row in result
        ]

        # Fetch total count
        total_records = conn.execute(
            count_query,
            params
        ).scalar()

        return {

            "records": records,

            "total_records": total_records
        }
# ============================================================
# category performance
# ==========================================================

def get_category_performance(search, offset, limit, filter_type, start_date=None, end_date=None):

    date_filter = ""
    custom_date_filter = ""

    if filter_type == "weekly":
        date_filter = "AND it.fDate >= DATEADD(DAY, -7, GETDATE())"

    elif filter_type == "monthly":
        date_filter = "AND it.fDate >= DATEADD(MONTH, -1, GETDATE())"

    if start_date and end_date:
        custom_date_filter = """
        AND it.fDate >= :start_date
        AND it.fDate < DATEADD(DAY, 1, :end_date)
        """

    query = text(f"""
    SELECT
        {CATEGORY_CASE} AS category,

        COUNT(DISTINCT pd.fItemcode) AS total_designs,

        SUM(ISNULL(it.fTotQty, 0)) AS total_orders

    FROM ItemTransaction it WITH (NOLOCK)

    JOIN Item pd
        ON it.fItemcode = pd.fItemcode

    WHERE pd.fItemName LIKE :search
    {date_filter}
    {custom_date_filter}

    GROUP BY
        {CATEGORY_CASE}

    ORDER BY total_orders DESC

    OFFSET :offset ROWS
    FETCH NEXT :limit ROWS ONLY
    """)

    params = {
        "search": f"%{search}%",
        "offset": offset,
        "limit": limit
    }

    if start_date and end_date:
        params["start_date"] = start_date
        params["end_date"] = end_date

    with engine.connect() as conn:
        result = conn.execute(query, params)
        return [dict(row._mapping) for row in result]
# ============================================================
# seasonal insights
# ==========================================================

def get_seasonal_insights(

    month,

    offset,

    limit,

    start_date=None,

    end_date=None
):

    month_filter = ""

    custom_date_filter = ""

    if month:

        month_filter = """
        AND DATENAME(MONTH, it.fDate) = :month
        """

    if start_date and end_date:

        custom_date_filter = """
        AND it.fDate >= :start_date
        AND it.fDate < DATEADD(DAY, 1, :end_date)
        """

    query = text(f"""

    SELECT

        DATENAME(MONTH, it.fDate) AS month_name,

        {CATEGORY_CASE} AS category,

        SUM(ISNULL(it.fTotQty, 0)) AS total_orders

    FROM ItemTransaction it WITH (NOLOCK)

    INNER JOIN Item pd
        ON it.fItemcode = pd.fItemcode

    WHERE

        ISNULL(it.fTotQty, 0) > 0

        {month_filter}

        {custom_date_filter}

    GROUP BY

        DATENAME(MONTH, it.fDate),

        {CATEGORY_CASE}

    ORDER BY

        total_orders DESC

    OFFSET :offset ROWS
    FETCH NEXT :limit ROWS ONLY

    """)

    params = {

        "offset": offset,

        "limit": limit
    }

    if month:

        params["month"] = month

    if start_date and end_date:

        params["start_date"] = start_date

        params["end_date"] = end_date

    with engine.connect() as conn:

        result = conn.execute(query, params)

        return [dict(row._mapping) for row in result]
# ============================================================
# ai auto insights
# ==========================================================

def get_auto_insights_data(

    offset,

    limit,

    filter_type=None,

    start_date=None,

    end_date=None
):

    date_filter = ""

    # Weekly filter
    if filter_type == "weekly":

        date_filter = """

        AND CAST(it.fDate AS DATE) >=
        CAST(DATEADD(DAY, -7, GETDATE()) AS DATE)

        """

    # Monthly filter
    elif filter_type == "monthly":

        date_filter = """

        AND CAST(it.fDate AS DATE) >=
        CAST(DATEADD(MONTH, -1, GETDATE()) AS DATE)

        """

    # Custom date filter
    elif start_date and end_date:

        date_filter = """

        AND it.fDate >= :start_date

        AND it.fDate < DATEADD(DAY, 1, :end_date)

        """

    data_query = text(f"""

    SELECT

        pd.fItemcode AS Fitemcode,

        pd.fItemName AS FitemName,

        {CATEGORY_CASE} AS category,

        SUM(ISNULL(it.fTotQty, 0)) AS total_orders,

        SUM(ISNULL(it.fAmount, 0)) AS total_sales,

        ISNULL(s.current_stock, 0) AS current_stock

    FROM ItemTransaction it WITH (NOLOCK)

    INNER JOIN Item pd
        ON it.fItemcode = pd.fItemcode

    LEFT JOIN (

        SELECT

            Itemcode,

            SUM(ISNULL(Qty, 0)) AS current_stock

        FROM Stock

        WHERE Itemcode IS NOT NULL

        GROUP BY Itemcode

    ) s
        ON pd.fItemcode = s.Itemcode

    WHERE

        ISNULL(it.fTotQty, 0) > 0

        {date_filter}

    GROUP BY

        pd.fItemcode,

        pd.fItemName,

        {CATEGORY_CASE},

        s.current_stock

    ORDER BY total_orders DESC

    OFFSET :offset ROWS
    FETCH NEXT :limit ROWS ONLY

    """)

    count_query = text(f"""

    SELECT COUNT(DISTINCT it.fItemcode)

    FROM ItemTransaction it

    WHERE

        ISNULL(it.fTotQty, 0) > 0

        {date_filter}

    """)

    params = {

        "offset": offset,

        "limit": limit
    }

    if start_date and end_date:

        params["start_date"] = start_date

        params["end_date"] = end_date

    with engine.connect() as conn:

        data_result = conn.execute(
            data_query,
            params
        )

        records = [

            dict(row._mapping)

            for row in data_result.fetchall()
        ]

        count_result = conn.execute(
            count_query,
            params
        )

        total_records = count_result.scalar()

        return {

            "records": records,

            "total_records": total_records
        }