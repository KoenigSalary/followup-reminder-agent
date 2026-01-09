✅ Module 2: utils/safe_keys.py
python
Copy code
def unique_key(prefix: str, idx: int, task_id):
    """Always unique Streamlit widget key for a row render."""
    tid = str(task_id) if task_id not in [None, "", "nan"] else "noid"
    return f"{prefix}_{idx}_{tid}"
