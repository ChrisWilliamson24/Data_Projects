import pandas as pd
from pathlib import Path


def load_inputs(budget_path, actuals_path):
    budget = pd.read_csv(
        budget_path,
        parse_dates=["month"],
    )
    actuals = pd.read_csv(
        actuals_path,
        parse_dates=["month"],
    )
    print(budget.head())
    print(actuals.head())

    print(budget.shape)
    print(actuals.shape)

    print(budget.dtypes)
    print(actuals.dtypes)
    return budget, actuals


# take a look at our data
def compute_combined(budget, actuals):
    # lets group the two tables so that we reduce the rows and have them grouped together
    gb = (
        budget.groupby(["month", "category", "subcategory"])["amount"]
        .sum()
        .reset_index()
    )
    ga = (
        actuals.groupby(["month", "category", "subcategory"])["amount"]
        .sum()
        .reset_index()
    )

    # merge them together so they are in the same table for comparison
    combined = gb.merge(
        ga,
        on=["month", "category", "subcategory"],
        how="outer",
        suffixes=("_budget", "_actual"),
    )

    combined = combined.fillna(0)

    combined["variance"] = combined["amount_actual"] - combined["amount_budget"]
    combined["variance_pct"] = combined["variance"] / combined["amount_budget"].replace(
        0, pd.NA
    )

    return combined


def category_investigation(combined):
    cat = combined.groupby("category", as_index=False).agg(
        budget=("amount_budget", "sum"),
        actual=("amount_actual", "sum"),
        variance=("variance", "sum"),
    )

    cat["variance_pct"] = cat["variance"] / cat["budget"].replace(0, pd.NA)

    cat = cat.sort_values("variance", ascending=False)

    return cat


def month_investigation(combined):
    mon = combined.groupby("month", as_index=False).agg(
        budget=("amount_budget", "sum"),
        actual=("amount_actual", "sum"),
        variance=("variance", "sum"),
    )
    mon["variance_pct"] = mon["variance"] / mon["budget"].replace(0, pd.NA)

    mon_chrono = mon.sort_values("month", ascending=True)
    mon_diag = mon.sort_values("variance", ascending=False)

    return mon_chrono, mon_diag


# quick sanity check for the grouped data
def sanity_check(combined, mon):
    totals = {
        "combined_budget": float(combined["amount_budget"].sum()),
        "combined_actual": float(combined["amount_actual"].sum()),
        "combined_variance": float(combined["variance"].sum()),
        "mon_budget": float(mon["budget"].sum()),
        "mon_actual": float(mon["actual"].sum()),
        "mon_variance": float(mon["variance"].sum()),
    }
    ok = (
        totals["combined_budget"] == totals["mon_budget"]
        and totals["combined_actual"] == totals["mon_actual"]
        and totals["combined_variance"] == totals["mon_variance"]
    )
    return ok, totals


def top_5_over_budget(combined, min_budget):
    """
    This function finds the top 5 entries in the combined DataFrame
    where the variance is greater than 0, indicating that the actual
    amount exceeded the budgeted amount.
    """
    combined_over_budget = combined[
        (combined["amount_budget"] >= min_budget) & (combined["variance"] > 0)
    ]
    combined_over_budget = combined_over_budget.sort_values(
        "variance_pct", ascending=False
    ).head(5)

    return combined_over_budget


def top_5_under_budget(combined, min_budget):
    """
    This function finds the top 5 entries in the combined DataFrame
    where the variance is greater than 0, indicating that the actual
    amount exceeded the budgeted amount.
    """
    combined_under_budget = combined[
        (combined["amount_budget"] >= min_budget) & (combined["variance"] < 0)
    ]
    combined_under_budget = combined_under_budget.sort_values(
        "variance_pct", ascending=True
    ).head(5)

    return combined_under_budget


# now let's work on generating the Excel report


def write_detail_sheet(writer: pd.ExcelWriter, combined: pd.DataFrame) -> None:
    wb = writer.book
    ws_name = "Detail"
    cols = [
        "month",
        "category",
        "subcategory",
        "amount_budget",
        "amount_actual",
        "variance",
        "variance_pct",
    ]
    df = combined[cols].copy()
    df.to_excel(writer, sheet_name=ws_name, index=False)
    ws = writer.sheets[ws_name]

    f_header = wb.add_format({"bold": True})
    f_money = wb.add_format({"num_format": "£#,##0", "align": "right"})
    f_pct = wb.add_format({"num_format": "0.0%", "align": "right"})

    # Header styling + basic widths
    for c, name in enumerate(df.columns):
        ws.write(0, c, name, f_header)
        ws.set_column(c, c, 16)

    # Number formats
    money_cols = {"amount_budget", "amount_actual", "variance"}
    pct_cols = {"variance_pct"}
    for c, name in enumerate(df.columns):
        if name in money_cols:
            ws.set_column(c, c, 16, f_money)
        elif name in pct_cols:
            ws.set_column(c, c, 12, f_pct)

    # Conditional formatting on variance col
    var_idx = df.columns.get_loc("variance")
    last_row = len(df)
    ws.conditional_format(
        1,
        var_idx,
        last_row,
        var_idx,
        {
            "type": "cell",
            "criteria": ">",
            "value": 0,
            "format": wb.add_format({"font_color": "#9C0006"}),
        },
    )
    ws.conditional_format(
        1,
        var_idx,
        last_row,
        var_idx,
        {
            "type": "cell",
            "criteria": "<",
            "value": 0,
            "format": wb.add_format({"font_color": "#006100"}),
        },
    )


def write_by_category_sheet(writer: pd.ExcelWriter, cat: pd.DataFrame) -> None:
    wb = writer.book
    ws_name = "By Category"
    df = cat.reset_index(drop=True).copy()
    df.to_excel(writer, sheet_name=ws_name, index=False)
    ws = writer.sheets[ws_name]

    f_header = wb.add_format({"bold": True})
    f_money = wb.add_format({"num_format": "£#,##0", "align": "right"})
    f_pct = wb.add_format({"num_format": "0.0%", "align": "right"})

    for c, name in enumerate(df.columns):
        ws.write(0, c, name, f_header)
        ws.set_column(c, c, 16)
        if name in {"budget", "actual", "variance"}:
            ws.set_column(c, c, 16, f_money)
        elif name == "variance_pct":
            ws.set_column(c, c, 12, f_pct)


def write_by_month_sheet(writer: pd.ExcelWriter, mon_chrono: pd.DataFrame) -> None:
    wb = writer.book
    ws_name = "By Month"
    df = mon_chrono.reset_index(drop=True).copy()
    df.to_excel(writer, sheet_name=ws_name, index=False)
    ws = writer.sheets[ws_name]

    f_header = wb.add_format({"bold": True})
    f_money = wb.add_format({"num_format": "£#,##0", "align": "right"})
    f_pct = wb.add_format({"num_format": "0.0%", "align": "right"})

    for c, name in enumerate(df.columns):
        ws.write(0, c, name, f_header)
        ws.set_column(c, c, 16)
        if name in {"budget", "actual", "variance"}:
            ws.set_column(c, c, 16, f_money)
        elif name == "variance_pct":
            ws.set_column(c, c, 12, f_pct)


def write_top_drivers_sheet(
    writer: pd.ExcelWriter, top_over: pd.DataFrame, top_under: pd.DataFrame
) -> None:
    wb = writer.book
    ws_name = "Top Drivers"
    ws = wb.add_worksheet(ws_name)
    writer.sheets[ws_name] = ws

    f_header = wb.add_format({"bold": True})
    f_money = wb.add_format({"num_format": "£#,##0", "align": "right"})
    f_pct = wb.add_format({"num_format": "0.0%", "align": "right"})
    f_date = wb.add_format({"num_format": "yyyy-mm-dd"})  # <- add this

    def _write_table(
        start_row: int, start_col: int, title: str, df: pd.DataFrame
    ) -> int:
        ws.write(start_row, start_col, title, f_header)
        r0, c0 = start_row + 1, start_col
        df = df.reset_index(drop=True).copy()

        # Ensure month is datetime for correct Excel rendering
        if "month" in df.columns:
            df["month"] = pd.to_datetime(df["month"])

        # headers
        for c, name in enumerate(df.columns):
            ws.write(r0, c0 + c, name, f_header)

        # values
        for i in range(len(df)):
            for c, name in enumerate(df.columns):
                val = df.iloc[i, c]
                if name == "month" and pd.notna(val):
                    # write as a real Excel datetime
                    ws.write_datetime(
                        r0 + 1 + i, c0 + c, pd.to_datetime(val).to_pydatetime(), f_date
                    )
                else:
                    ws.write(r0 + 1 + i, c0 + c, val)

        # widths + number formats
        for c, name in enumerate(df.columns):
            ws.set_column(c0 + c, c0 + c, 16)
            if name in {"amount_budget", "amount_actual", "variance"}:
                ws.set_column(c0 + c, c0 + c, 16, f_money)
            elif name == "variance_pct":
                ws.set_column(c0 + c, c0 + c, 12, f_pct)
            elif name == "month":
                ws.set_column(c0 + c, c0 + c, 14, f_date)

        return r0 + 1 + len(df)

    next_row = _write_table(0, 0, "Top 5 Over Budget (by variance)", top_over)
    _ = _write_table(next_row + 2, 0, "Top 5 Under Budget (by variance)", top_under)


def build_report(
    out_path: Path,
    combined: pd.DataFrame,
    cat: pd.DataFrame,
    mon_chrono: pd.DataFrame,
    top_over: pd.DataFrame,
    top_under: pd.DataFrame,
) -> None:
    with pd.ExcelWriter(
        out_path, engine="xlsxwriter", datetime_format="yyyy-mm-dd"
    ) as writer:
        write_detail_sheet(writer, combined)
        write_by_category_sheet(writer, cat)
        write_by_month_sheet(writer, mon_chrono)
        write_top_drivers_sheet(writer, top_over, top_under)


if __name__ == "__main__":
    BASE = Path(r"C:\Users\cwill\Documents\Python\Data_Projects\Data\Raw")
    budget_path = BASE / "budget.csv"
    actuals_path = BASE / "actuals.csv"

    budget, actuals = load_inputs(budget_path, actuals_path)
    combined = compute_combined(budget, actuals)

    cat = category_investigation(combined)
    mon_chrono, mon_diag = month_investigation(combined)

    ok, totals = sanity_check(combined, mon_chrono)
    print("Sanity check OK:", ok, "| Totals:", totals)

    top_over = top_5_over_budget(combined, min_budget=1.0)
    top_under = top_5_under_budget(combined, min_budget=1.0)

    out_path = Path(
        r"C:\Users\cwill\Documents\Python\Data_Projects\projects\1. beginner\03-excel-report-generator\Budget_vs_Actuals_Report.xlsx"
    )
    build_report(out_path, combined, cat, mon_chrono, top_over, top_under)
    print(f"Report written to: {out_path}")
