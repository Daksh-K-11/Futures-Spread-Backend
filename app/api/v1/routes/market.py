from fastapi import APIRouter, Query
from app.core.kite import kite

import pandas as pd
import time

router = APIRouter()


@router.get("/futures-spread")
def futures_spread(

    page: int | None = Query(
        default=None,
        ge=1
    ),

    page_size: int | None = Query(
        default=None,
        ge=1
    ),

    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$"
    )
):

    # -----------------------------
    # Fetch instruments
    # -----------------------------
    instruments = kite.instruments("NFO")

    df = pd.DataFrame(instruments)

    # -----------------------------
    # Only FUT contracts
    # -----------------------------
    df = df[df["instrument_type"] == "FUT"]

    # Optional optimization
    df = df[df["segment"] == "NFO-FUT"]

    # -----------------------------
    # Create instrument format
    # -----------------------------
    df["instrument"] = (
        df["exchange"] + ":" + df["tradingsymbol"]
    )

    # -----------------------------
    # Sort by company + expiry
    # -----------------------------
    df = df.sort_values(
        by=["name", "expiry"]
    )

    instrument_list = df["instrument"].tolist()

    # -----------------------------
    # Fetch LTP in batches
    # -----------------------------
    BATCH_SIZE = 100

    all_ltp = {}

    for i in range(0, len(instrument_list), BATCH_SIZE):

        batch = instrument_list[i:i+BATCH_SIZE]

        ltp_data = kite.ltp(batch)

        all_ltp.update(ltp_data)

        time.sleep(0.2)

    # -----------------------------
    # Attach LTP
    # -----------------------------
    df["ltp"] = df["instrument"].apply(
        lambda x: all_ltp.get(x, {}).get("last_price")
    )

    # -----------------------------
    # Build response
    # -----------------------------
    result = []

    grouped = df.groupby("name")

    for company, group in grouped:

        group = group.sort_values("expiry")

        group = group.reset_index(drop=True)

        if len(group) < 2:
            continue

        for i in range(len(group) - 1):

            current_row = group.iloc[i]
            next_row = group.iloc[i + 1]

            current_ltp = current_row["ltp"]
            next_ltp = next_row["ltp"]

            if current_ltp is None or next_ltp is None:
                continue

            spread = round(
                next_ltp - current_ltp,
                2
            )

            yield_percent = round(
                (spread / current_ltp) * 100,
                2
            )

            result.append({

                "company": company,

                "current_contract":
                    current_row["tradingsymbol"],

                "next_contract":
                    next_row["tradingsymbol"],

                "current_expiry":
                    str(current_row["expiry"]),

                "next_expiry":
                    str(next_row["expiry"]),

                "current_ltp":
                    current_ltp,

                "next_ltp":
                    next_ltp,

                "spread":
                    spread,

                "yield":
                    yield_percent
            })

    # -----------------------------
    # Sort by yield
    # -----------------------------
    reverse_sort = sort_order == "desc"

    result = sorted(
        result,
        key=lambda x: x["yield"],
        reverse=reverse_sort
    )

    total_count = len(result)

    # -----------------------------
    # Optional pagination
    # -----------------------------
    if page is not None and page_size is not None:

        start = (page - 1) * page_size
        end = start + page_size

        result = result[start:end]

    return {

        "success": True,

        "count": len(result),

        "total_count": total_count,

        "page": page,

        "page_size": page_size,

        "sort_order": sort_order,

        "data": result
    }