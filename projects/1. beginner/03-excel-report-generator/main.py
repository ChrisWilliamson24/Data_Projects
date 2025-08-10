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
