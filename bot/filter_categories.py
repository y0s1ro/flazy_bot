import json

def filter_dict(d):
    """
    Recursively remove any dict nodes where 'Status' is False or 'False'.
    Returns a filtered dict or None if the node should be dropped.
    """
    if not isinstance(d, dict):
        return d

    status = d.get("Status")
    # Treat string "False", lowercase or boolean False as removal
    if status in [False, "False", "false"]:
        return None

    newd = {}
    for key, val in d.items():
        # Keep the Status field if True
        if key == "Status":
            newd[key] = val
            continue

        if isinstance(val, dict):
            filtered = filter_dict(val)
            if filtered is not None:
                newd[key] = filtered
        else:
            newd[key] = val

    return newd


def filter():
    # Load the JSON file
    with open("bot/cfg/categories.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter top-level categories
    filtered = {}
    for cat_name, cat_val in data.items():
        filtered_cat = filter_dict(cat_val)
        if filtered_cat is not None:
            filtered[cat_name] = filtered_cat

    # Save the filtered data
    with open("bot/cfg/filtered_categories.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print("Filtered categories written to 'filtered_categories.json'")

