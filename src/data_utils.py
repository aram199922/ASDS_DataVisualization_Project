import os
import pandas as pd

DATE_COLS = ["date_found", "adoptable_from", "posted"]
BEHAVIOR_COLS = ["likes_people", "likes_children", "get_along_males", "get_along_females", "get_along_cats"]
AGE_GROUPS = ["Young (0-5y)", "Adult (5-10y)", "Senior (10+y)"]
SIZE_ORDER = ["small", "medium", "large"]
BEHAVIOR_ORDER = ["Limited Social", "Social", "Highly Social"]
SEASON_ORDER = ["Winter", "Spring", "Summer", "Fall"]

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_SRC_DIR, "..", "_output", "processed_dogs.csv")

_dataframe_cache = None


def _classify_behavior(row):
    positive = (row[BEHAVIOR_COLS] == "yes").sum()
    if positive >= 4:
        return "Highly Social"
    elif positive == 3:
        return "Social"
    return "Limited Social"


def load_data() -> pd.DataFrame:
    global _dataframe_cache
    if _dataframe_cache is not None:
        return _dataframe_cache

    df = pd.read_csv(DATA_PATH)

    threshold = len(BEHAVIOR_COLS) - 1
    df = df[(df[BEHAVIOR_COLS] == "unknown").sum(axis=1) < threshold]

    for col in DATE_COLS:
        df[col] = pd.to_datetime(df[col])

    df["waiting_days"] = (df["adoptable_from"] - df["date_found"]).dt.days
    df = df[df["waiting_days"] >= 0]
    df["delayed"] = (df["waiting_days"] > 0).astype(int)

    df["behavior_score"] = df[BEHAVIOR_COLS].apply(lambda row: (row == "yes").sum(), axis=1)
    df["behavior_score_name"] = "Score_" + df["behavior_score"].astype(str)
    df["behavior_category"] = df.apply(_classify_behavior, axis=1)
    df["behavior_category"] = pd.Categorical(
        df["behavior_category"], categories=BEHAVIOR_ORDER, ordered=True
    )

    df["behavioral_profile"] = (
        df["likes_people"].astype(str) + "_" +
        df["get_along_cats"].astype(str) + "_" +
        df["neutered"].astype(str)
    ).str.lower()

    df["age_group"] = pd.cut(df["age"], bins=[0, 5, 10, 100], labels=AGE_GROUPS)

    df["month_found"] = df["date_found"].dt.month
    df["quarter_found"] = df["date_found"].dt.quarter
    df["season_found"] = df["month_found"].map({
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Fall", 10: "Fall", 11: "Fall",
    })

    _dataframe_cache = df
    return df