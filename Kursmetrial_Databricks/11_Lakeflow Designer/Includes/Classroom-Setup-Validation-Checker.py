# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Common-Python

# COMMAND ----------

########################################
## Setup schema
########################################
schema = 'designer_meeting'

# COMMAND ----------

def check_table(table_name, expected_rows, expected_columns, spot_check=None):
    """
    Quick validation for workshop gold tables.

    Args:
        table_name: fully qualified table name, e.g. "labuser_x.designer_meeting.gold_session_summary".
        expected_rows: int, expected row count.
        expected_columns: list of column names that must exist in the table.
        spot_check: optional. Either a single dict, or a list of dicts, where each dict has:
            key_column     - column to filter on (usually a primary key like meeting_uuid)
            key_value      - value of key_column for the row you want to inspect
            check_column   - column whose value you want to verify
            expected_value - the expected value (use None to assert NULL)

    Prints PASS/FAIL for each check. Returns True if everything passed, else False.

    Example usage (one spot check):
        check_table(
            table_name="labuser_xxx.designer_meeting.gold_session_summary",
            expected_rows=41,
            expected_columns=["meeting_uuid", "session_name", "total_attendees"],
            spot_check={
                "key_column": "meeting_uuid",
                "key_value": "/e3hcn3IRDO17ugBv3bXHg==",
                "check_column": "total_attendees",
                "expected_value": 52,
            },
        )

    Example usage (multiple spot checks):
        check_table(
            table_name="labuser_xxx.designer_meeting.gold_session_summary",
            expected_rows=41,
            expected_columns=["meeting_uuid", "session_name", "total_attendees"],
            spot_check=[
                {
                    "key_column": "meeting_uuid",
                    "key_value": "/e3hcn3IRDO17ugBv3bXHg==",
                    "check_column": "total_attendees",
                    "expected_value": 52,
                },
                {
                    "key_column": "meeting_uuid",
                    "key_value": "qR7xKmN3T5WvYpLd8eZbJA==",
                    "check_column": "total_attendees",
                    "expected_value": None,
                },
            ],
        )
    """
    df = spark.table(table_name)
    results = []

    actual_rows = df.count()
    results.append((
        "Row count",
        actual_rows == expected_rows,
        f"actual={actual_rows}, expected={expected_rows}",
    ))

    actual_columns = df.columns
    missing = [c for c in expected_columns if c not in actual_columns]
    results.append((
        "Columns present",
        not missing,
        "all present" if not missing else f"missing={missing}",
    ))

    if spot_check:
        checks = [spot_check] if isinstance(spot_check, dict) else list(spot_check)
        for i, sc in enumerate(checks, 1):
            key_col = sc["key_column"]
            key_val = sc["key_value"]
            check_col = sc["check_column"]
            expected_val = sc["expected_value"]

            label = f"Spot check {i}" if len(checks) > 1 else "Spot check"

            matched = df.filter(df[key_col] == key_val).collect()
            if not matched:
                results.append((
                    label,
                    False,
                    f"no row found where {key_col} = {key_val!r}",
                ))
            else:
                actual_val = matched[0][check_col]
                results.append((
                    label,
                    actual_val == expected_val,
                    f"where {key_col}={key_val!r}: {check_col} actual={actual_val!r}, expected={expected_val!r}",
                ))

    print("=" * 70)
    print(f"Validating: {table_name}")
    print("=" * 70)
    for name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}: {detail}")
        if name == "Row count" and not ok:
            print("       Hint: row count mismatches usually mean a JOIN problem.")
            print("       Check that you used a LEFT JOIN with the dimension table on the left,")
            print("       so every row from the dimension is preserved even when the fact has no match.")
    print("=" * 70)

    all_passed = all(r[1] for r in results)
    print("All checks passed." if all_passed else "One or more checks failed. Review above.")
    return all_passed
