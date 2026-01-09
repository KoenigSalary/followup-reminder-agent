✅ Module 1: 
python
Copy code
import pandas as pd

LEGACY_STATUS_MAP = {
    "COMPLETED": "DONE",
    "CLOSED": "DONE",
    "COMPLETE": "DONE",
    "completed": "DONE",
    "closed": "DONE",
}

COLUMN_ALIASES = {
    "task_text": "Subject",
    "owner": "Owner",
    "deadline": "Due Date",
    "priority": "Priority",
    "status": "Status",
    "cc": "CC",
    "remarks": "Remarks",
    "last_reminder_date": "Last Reminder Date",
}

REQUIRED_COLUMNS = ["Subject", "Owner", "Status", "Priority", "Due Date", "Remarks", "CC"]

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Make df consistent across old/new schemas and remove ghost rows."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # Rename known aliases to canonical names
    for old, new in COLUMN_ALIASES.items():
        if old in df.columns and new not in df.columns:
            df.rename(columns={old: new}, inplace=True)

    # Ensure required cols exist
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Normalize Status
    df["Status"] = (
        df["Status"]
        .replace(LEGACY_STATUS_MAP)
        .fillna("OPEN")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    df.loc[~df["Status"].isin(["OPEN", "DONE"]), "Status"] = "OPEN"

    # Normalize Priority
    df["Priority"] = (
        df["Priority"]
        .fillna("MEDIUM")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    df.loc[~df["Priority"].isin(["URGENT", "HIGH", "MEDIUM", "LOW"]), "Priority"] = "MEDIUM"

    # Remove ghost rows: subject/owner missing or nan-like
    df["Subject"] = df["Subject"].astype(str)
    df["Owner"] = df["Owner"].astype(str)

    df = df[
        df["Subject"].notna()
        & df["Owner"].notna()
        & (df["Subject"].str.strip().str.lower() != "nan")
        & (df["Owner"].str.strip().str.lower() != "nan")
        & (df["Subject"].str.strip() != "")
        & (df["Owner"].str.strip() != "")
    ].copy()

    return df
