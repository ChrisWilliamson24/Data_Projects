import pandas as pd

# get our data
budget = pd.read_csv(
    r"C:\Users\cwill\Documents\Python\Data_Projects\Data\Raw\budget.csv",
    parse_dates=["month"],
)
actuals = pd.read_csv(
    r"C:\Users\cwill\Documents\Python\Data_Projects\Data\Raw\actuals.csv",
    parse_dates=["month"],
)

# take a look at our data
print(budget.head())
print(actuals.head())

print(budget.shape)
print(actuals.shape)

print(budget.dtypes)
print(actuals.dtypes)

# lets group the two tables so that we reduce the rows and have them grouped together
gb = budget.groupby(["month", "category", "subcategory"])["amount"].sum().reset_index()
print(gb.head())

ga = actuals.groupby(["month", "category", "subcategory"])["amount"].sum().reset_index()
print(ga.head())

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

print(combined.head())

# category investigation

cat = combined.groupby("category").agg(
    budget=("amount_budget", "sum"),
    actual=("amount_actual", "sum"),
    variance=("variance", "sum"),
)

cat["variance_pct"] = cat["variance"] / cat["budget"].replace(0, pd.NA)

cat = cat.sort_values("variance", ascending=False)

print(cat.head())

# month investigation

mon = combined.groupby("month", as_index=False).agg(
    budget=("amount_budget", "sum"),
    actual=("amount_actual", "sum"),
    variance=("variance", "sum"),
)
mon["variance_pct"] = mon["variance"] / mon["budget"].replace(0, pd.NA)

mon_chrono = mon.sort_values("month", ascending=True)
mon_diag = mon.sort_values("variance", ascending=False)

# quick sanity check for the grouped data
sum_check = (
    combined["amount_budget"].sum() == mon["budget"].sum()
    and combined["amount_actual"].sum() == mon["actual"].sum()
    and combined["variance"].sum() == mon["variance"].sum()
)
if not sum_check:
    print("Warning: Budget amounts do not match across tables!")
else:
    print("Totals match across tables.")

# find the top 5 entries with the highest variance percentage
combined_over_budget = combined[combined["variance"] > 0]
combined_over_budget = combined_over_budget.sort_values(
    "variance_pct", ascending=False
).head(5)

print(combined_over_budget.head())

# check for missing values and check the data types
print(combined_over_budget.isna().sum())
print(combined_over_budget.dtypes)
