from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
import traceback
from app.models.gov_dash import (
    AccidentAnalyticsFilters1,
    AccidentAnalyticsResponse1
)
from app.db import get_supabase
from supabase import Client


def get_accident_trends_service():
    supabase = get_supabase()
    
    # Fetch all data using pagination
    all_data = []
    offset = 0
    limit = 1000  # Supabase max limit per page
    
    while True:
        resp = supabase.table("Accident Record").select('"incident at date","Severity"').range(offset, offset + limit - 1).execute()
        
        if not resp.data:
            break
            
        all_data.extend(resp.data)
        offset += limit

    if not all_data:
        return {
            "monthly_counts": {},
            "yearly_counts": {},
            "day_of_week_counts": {}
        }

    from collections import defaultdict
    import datetime

    monthly_counts = defaultdict(lambda: {"total": 0, "serious": 0})
    yearly_counts = defaultdict(lambda: {"total": 0, "serious": 0})
    day_of_week_counts = defaultdict(lambda: {"total": 0, "serious": 0})

    for row in all_data:
        date_str = row.get("incident at date")
        severity = row.get("Severity")

        if not date_str:
            continue

        try:
            date_obj = datetime.date.fromisoformat(date_str)

            # keys
            month_key = date_obj.strftime("%Y-%m")   # e.g. "2022-06"
            year_key = str(date_obj.year)            # e.g. "2022"
            day_key = date_obj.strftime("%A")        # e.g. "Monday"

            # increment totals
            monthly_counts[month_key]["total"] += 1
            yearly_counts[year_key]["total"] += 1
            day_of_week_counts[day_key]["total"] += 1

            # increment serious
            if severity == "S":
                monthly_counts[month_key]["serious"] += 1
                yearly_counts[year_key]["serious"] += 1
                day_of_week_counts[day_key]["serious"] += 1

        except Exception:
            continue

    return {
        "monthly_counts": dict(monthly_counts),
        "yearly_counts": dict(yearly_counts),
        "day_of_week_counts": dict(day_of_week_counts)
    }


import traceback

# def get_comprehensive_analytics_service1(filters: AccidentAnalyticsFilters1) -> AccidentAnalyticsResponse1:
#     """Get comprehensive accident analytics filtered by date and severity"""

#     supabase: Client = get_supabase()

#     # Columns to analyze (exact schema matches, no quotes)
#     columns = [
#         "time of collision",
#         "Collision with",
#         "Road Condition",
#         "Road Type",
#         "Category of Road",
#         "Alcohol Consumption",
#         "Illicit Drugs",
#         "Time taken to reach hospital",
#         "Bystander expenditure per day",
#         "Discharge Outcome",
#         "First aid given at seen",  # Exact schema name
#     ]

#     results = {}

#     for col in columns:
#         query = f"""
#             SELECT "{col}" AS category, COUNT(*) AS count
#             FROM "Accident Record"
#             WHERE "incident at date" BETWEEN '{filters.start_date}' AND '{filters.end_date}'
#               AND "Severity" = '{filters.severity}'
#             GROUP BY "{col}"
#             ORDER BY count DESC;
#         """

#         try:
#             print(f"Executing for {col}: {query[:200]}...")  # Truncated log

#             response = supabase.rpc("exec_sql", {"sql": query}).execute()

#             # Extract data (handle error JSON from function)
#             rows = []
#             data = None
#             if hasattr(response, "data"):
#                 data = response.data
#             elif isinstance(response, dict) and "data" in response:
#                 data = response["data"]

#             if data:
#                 if isinstance(data, list):
#                     rows = data
#                 elif isinstance(data, dict) and "error" in data:
#                     raise ValueError(f"SQL Error for {col}: {data['error']}")

#             # Build valid int dict
#             results[col] = {
#                 (row.get("category") or "Unknown"): int(row.get("count", 0))
#                 for row in (rows or [])
#                 if row.get("count") is not None
#             }

#             if not results[col]:  # Empty? Add fallback
#                 results[col] = {"Unknown": 0}

#             print(f"Success for {col}: {list(results[col].keys())}")

#         except Exception as e:
#             error_msg = str(e)
#             print(f"Error for {col}: {error_msg}\nTraceback: {traceback.format_exc()}")
#             # VALID INT FALLBACK: Empty or single zero to pass Pydantic
#             results[col] = {"Error": 0}  # Or {} if model allows empty dicts

#     return AccidentAnalyticsResponse1(results=results)


def get_comprehensive_analytics_service1(filters: AccidentAnalyticsFilters1) -> AccidentAnalyticsResponse1:
    """Get comprehensive accident analytics filtered by date and severity"""

    supabase: Client = get_supabase()

    columns = [
        "time of collision",
        "Collision with",
        "Road Condition",
        "Road Type",
        "Category of Road",
        "Alcohol Consumption",
        "Illicit Drugs",
        "Time taken to reach hospital",
        "Bystander expenditure per day",
        "Discharge Outcome",
        "First aid given at seen",
    ]

    results = {}

    for col in columns:
        try:
            print(f"Querying {col}...")
            
            # Properly quote column names with spaces for SQL
            quoted_col = f'"{col}"'
            
            # Fetch filtered records  
            response = supabase.table("Accident Record")\
                .select(quoted_col)\
                .gte('"incident at date"', str(filters.start_date))\
                .lte('"incident at date"', str(filters.end_date))\
                .eq('"Severity"', filters.severity)\
                .execute()

            # Count categories manually
            from collections import Counter
            categories = [row.get(col) or "Unknown" for row in response.data]
            counts = Counter(categories)
            
            results[col] = dict(counts)
            
            if not results[col]:
                results[col] = {"No Data": 0}

            print(f"✓ {col}: {len(results[col])} categories")

        except Exception as e:
            print(f"❌ Error for {col}: {str(e)}")
            print(traceback.format_exc())
            results[col] = {"Error": 0}

    return AccidentAnalyticsResponse1(results=results)