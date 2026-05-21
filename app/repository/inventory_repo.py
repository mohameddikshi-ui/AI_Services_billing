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


def get_inventory_data(

    search,

    offset,

    limit,

    filter_type="overall",

    month=None,

    year=None,

    start_date=None,

    end_date=None
):

    date_filter = ""

    month_filter = ""

    year_filter = ""

    custom_date_filter = ""

    period_days = 30

    # ==========================================
    # FILTER TYPE LOGIC
    # ==========================================

    if not month and not (start_date and end_date):

        if filter_type == "weekly":

            date_filter = """
            AND it.fDate >= DATEADD(DAY, -7, GETDATE())
            """

            period_days = 7

        elif filter_type == "monthly":

            date_filter = """
            AND it.fDate >= DATEADD(MONTH, -1, GETDATE())
            """

            period_days = 30

    # ==========================================
    # MONTH FILTER
    # ==========================================

    if month:

        month_filter = """
        AND DATENAME(MONTH, it.fDate) = :month
        """

    # ==========================================
    # YEAR FILTER
    # ==========================================

    if year:

        year_filter = """
        AND YEAR(it.fDate) = :year
        """

    # ==========================================
    # CUSTOM DATE FILTER
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

        ISNULL(st.current_stock, 0) AS current_stock,

        SUM(ISNULL(it.fTotQty, 0)) AS historical_sales,

        COUNT(DISTINCT CAST(it.fDate AS DATE)) AS active_days,

        SUM(ISNULL(it.fTotQty, 0)) * 1.0 /
        NULLIF(:period_days, 0)
        AS avg_daily_sales

    FROM Item pd

    LEFT JOIN (

        SELECT

            Itemcode,

            SUM(ISNULL(Qty, 0)) AS current_stock

        FROM Stock

        WHERE Itemcode IS NOT NULL

        AND LTRIM(RTRIM(Itemcode)) <> ''

        GROUP BY Itemcode

    ) st
        ON pd.fItemcode = st.Itemcode

    LEFT JOIN ItemTransaction it
        ON pd.fItemcode = it.fItemcode

        {date_filter}

        {month_filter}

        {year_filter}

        {custom_date_filter}

    WHERE

        pd.fItemName LIKE :search

        AND pd.fItemcode IS NOT NULL

        AND LTRIM(RTRIM(pd.fItemcode)) <> ''

    GROUP BY

        pd.fItemcode,

        pd.fItemName,

        st.current_stock,

        {CATEGORY_CASE}

    HAVING SUM(ISNULL(it.fTotQty, 0)) > 0

    ORDER BY historical_sales DESC

    OFFSET :offset ROWS
    FETCH NEXT :limit ROWS ONLY

    """)

    params = {

        "search": f"%{search}%",

        "offset": offset,

        "limit": limit,

        "period_days": period_days
    }

    if month:

        params["month"] = month

    if year:

        params["year"] = year

    if start_date and end_date:

        params["start_date"] = start_date

        params["end_date"] = end_date

    print("\n📌 INVENTORY FILTER PARAMS\n")

    print(params)

    with engine.connect() as conn:

        result = conn.execute(query, params)

        return [

            dict(row._mapping)

            for row in result.fetchall()
        ]