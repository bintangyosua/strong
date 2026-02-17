import marimo

__generated_with = "0.19.1"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # GYM/EXERCISES DASHBOARD
    """)
    return


@app.cell(hide_code=True)
def _(exercise_muscle_mapping, mo):
    unique_muscles = sorted(
        {
            muscle
            for muscles in exercise_muscle_mapping.values()
            for muscle in muscles
        }
    )

    target_filter = mo.ui.multiselect(
        options=["All"] + unique_muscles, value=["All"]
    )
    return (target_filter,)


@app.cell
def _(mo, target_filter):
    mo.md(f"""
    Filter Target Otot: {target_filter}
    """)
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo

    import pandas as pd
    import random
    from datetime import datetime, timedelta

    import matplotlib.pyplot as plt
    import seaborn as sns
    import altair as alt

    import io
    import urllib.request

    sns.set_theme(style="whitegrid")

    import warnings

    warnings.filterwarnings("ignore")
    return alt, io, mo, pd, urllib


@app.cell(hide_code=True)
def _():
    exercise_muscle_mapping = {
        "Chest Press Machine": ["Chest", "Triceps", "Front Delts"],
        "Chest Fly": ["Chest"],
        "Pull Up": ["Lats", "Upper Back", "Biceps"],
        "Lat Pulldown": ["Lats", "Upper Back", "Biceps"],
        "Row Machine": ["Middle Back", "Lats", "Biceps"],
        "Cable Row": ["Middle Back", "Lats", "Biceps"],
        "Straight Arm Pulldown": ["Lats"],
        "Lateral Raise Machine": ["Side Delts"],
        "Cable Lateral Raise": ["Side Delts"],
        "Reverse Fly Rear Delt": ["Rear Delts", "Upper Back"],
        "Rear Delt Cable": ["Rear Delts"],
        "Overhead Cable Tricep Extension": ["Triceps (Long Head)"],
        "Tricep Pushdown": ["Triceps"],
        "Preacher Curl": ["Biceps"],
        "Bayesian Cable Curl": ["Biceps (Long Head)"],
        "Hammer Cable Curl": ["Brachialis", "Biceps"],
        "Wrist Cable Curl": ["Forearms (Flexors)"],
        "Reverse Wrist Cable Curl": ["Forearms (Extensors)"],
        "Leg Press": ["Quads", "Glutes"],
        "Leg Curl (Hamstring)": ["Hamstrings"],
        "Leg Extension": ["Quads"],
        "Hip Abduction (Outer/Glutes)": ["Glutes (Medius)"],
        "Hip Adduction (Inner)": ["Adductors"],
        "Seated Calf Raise": ["Calves (Soleus)"],
        "Hanging Leg Raise": ["Abs", "Hip Flexors"],
        "Cable Crunch": ["Abs"],
    }
    return (exercise_muscle_mapping,)


@app.cell(hide_code=True)
def _(exercise_muscle_mapping, io, pd, urllib):
    url = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vQkEhaXHJpiqlW8VvZ6QQuBov_taXgCh3Bs5daNOVthaL90-CykW-N1LsY5jmlFmdETmq5LvrW1dhen/pub?gid=248463957&single=true&output=csv"

    with urllib.request.urlopen(url) as response:
        csv_text = response.read().decode("utf-8")

    df = pd.read_csv(io.StringIO(csv_text))

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df["Set"] = df["Set"].astype(int)
    df["Reps"] = df["Reps"].astype(int)
    df["Beban (kg)"] = df["Beban"].astype(float)
    df["Datetime"] = pd.to_datetime(df["Date"])
    df["Week"] = df["Datetime"].dt.to_period("W").apply(lambda x: x.start_time)

    df = df.drop(["Email Address", "Beban"], axis=1)

    df["Target Otot"] = df["Exercise"].map(exercise_muscle_mapping)
    df["Target Otot"] = df["Exercise"].apply(
        lambda x: exercise_muscle_mapping.get(x, ["Unknown"])[0]
    )

    df["Volume"] = df["Set"] * df["Reps"] * df["Beban (kg)"]
    df["Total_Reps"] = df["Set"] * df["Reps"]
    df["Weighted_Load"] = df["Beban (kg)"] * df["Total_Reps"]
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Display Data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.1 Display per Day
    """)
    return


@app.cell(hide_code=True)
def _(df, target_filter):
    filtered_df = df[
        df["Target Otot"].apply(
            lambda x: (
                "All" in target_filter.value
                or any(muscle in x for muscle in target_filter.value)
            )
        )
    ]

    filtered_df.sort_values(by="Timestamp", ascending=False)
    return (filtered_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.2 Display per Week
    """)
    return


@app.cell(hide_code=True)
def _(filtered_df):
    weekly_df = (
        filtered_df.explode("Target Otot")
        .groupby(["Week", "Exercise", "Target Otot"], as_index=False)
        .agg(
            {
                "Weighted_Load": "sum",
                "Total_Reps": "sum",
                "Set": "sum",
                "Volume": "sum",
            }
        )
    )

    weekly_df["Beban_Efektif"] = (
        weekly_df["Weighted_Load"] / weekly_df["Total_Reps"]
    ).round(2)

    weekly_df
    return (weekly_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Scatter Plot Progress per Week
    """)
    return


@app.cell(hide_code=True)
def _(alt, weekly_df):
    _chart = (
        alt.Chart(weekly_df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Week:T",
                title="Date",
                axis=alt.Axis(
                    format="%d %b %Y", values=weekly_df["Week"].unique().tolist()
                ),
            ),
            y=alt.Y("Beban_Efektif:Q", title="Average Load (kg)"),
            color=alt.Color(
                "Exercise:N", legend=alt.Legend(title="Exercise", orient="right")
            ),
            tooltip=["Exercise", "Target Otot", "Week", "Beban_Efektif"],
        )
    )

    _chart
    return


@app.cell(hide_code=True)
def _(weekly_df):
    muscle_volume = (
        weekly_df.explode("Target Otot")
        .groupby(["Week", "Target Otot"], as_index=False)
        .agg({"Volume": "sum", "Beban_Efektif": "mean"})
        .sort_values(by="Volume", ascending=False)
    )

    muscle_volume
    return (muscle_volume,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Stacked Bar & Scatter Plot Chart Volume Progress per Week
    """)
    return


@app.cell(hide_code=True)
def _(alt, muscle_volume):
    _chart = (
        alt.Chart(muscle_volume)
        .mark_bar()
        .encode(
            y=alt.Y("Target Otot:N", sort="-x", title="Target Muscle"),
            x=alt.X("Volume:Q", title="Total Volume (kg)", stack="zero"),
            color=alt.Color("Week:T", title="Week"),
            tooltip=["Target Otot", "Week", "Volume"],
        )
        .properties(title="Weekly Training Volume per Muscle Group")
    )

    _chart
    return


@app.cell(hide_code=True)
def _(alt, weekly_df):
    (
        alt.Chart(weekly_df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Week:T",
                title="Week",
                axis=alt.Axis(
                    format="%d %b %Y", values=weekly_df["Week"].unique().tolist()
                ),
            ),
            y=alt.Y("Volume:Q", title="Total Volume"),
            color=alt.Color(
                "Exercise:N", legend=alt.Legend(title="Exercise", orient="right")
            ),
            tooltip=["Exercise", "Target Otot", "Week", "Beban_Efektif"],
        )
    )
    return


@app.cell(hide_code=True)
def _(filtered_df):
    daily_df = filtered_df.groupby(
        ["Date", "Exercise", "Target Otot"], as_index=False
    ).agg(
        Total_Reps=("Total_Reps", "sum"),
        Total_Weighted_Load=("Weighted_Load", "sum"),
    )

    daily_df["Beban_Efektif"] = (
        daily_df["Total_Weighted_Load"] / daily_df["Total_Reps"]
    )
    return (daily_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Scatter Plot Beban Efektif per Day
    """)
    return


@app.cell(hide_code=True)
def _(alt, daily_df):
    (
        alt.Chart(daily_df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Date:T",
                title="Date",
            ),
            y=alt.Y("Beban_Efektif:Q", title="Beban_Efektif"),
            color=alt.Color(
                "Exercise:N", legend=alt.Legend(title="Exercise", orient="right")
            ),
            tooltip=["Exercise", "Target Otot", "Beban_Efektif"],
        )
    )
    return


if __name__ == "__main__":
    app.run()
