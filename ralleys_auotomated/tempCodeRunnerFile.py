
    mgb = (
        zone_data[zone_data["Party"] == "MGB"]
        .set_index("Category")
        .reindex(categories)["Percentage (%)"]
        .fillna(0)
    )