import module
import config

center_map = config.CenterMap()  # initialize center map class


def test_online_class_is_online_location(df_att_clean):
    """
    Class location online should have class area online.
    """

    assert (
        df_att_clean.loc[
            df_att_clean["class_location"] == "Online", "class_area"
        ].unique()
        == "Online"
    ).all()


def test_class_with_online_name_is_online_location(df_att_clean):
    """
    Class that has online should have online location.
    """

    filter_ = df_att_clean["class_type"].str.contains("Online")
    assert (df_att_clean.loc[filter_, "class_location"] != "Online").sum() == 0


def test_class_center_match_with_class_area(df_att_clean):
    """
    Class center should match with the correct area.
    """

    for center, area in center_map.get_center_area_map().items():
        df = df_att_clean.loc[df_att_clean["class_location"] == center]
        area_in_df = df["class_area"].unique()
        # some old centers are gone, for example KG
        if len(df) == 0:
            continue
        assert len(area_in_df) == 1, f"class location {center} has multiple areas: {area_in_df}"
        assert area_in_df == area, f"class location {center} has wrong area in DF: {area_in_df})"


def test_teacher_center_match_with_teacher_area(df_att_clean):
    """
    Teacher center should match with the correct area.
    """

    for center, area in center_map.get_center_area_map().items():
        df = df_att_clean.loc[df_att_clean["teacher_center"] == center]
        area_in_df = df["teacher_area"].unique()
        # some old centers are gone, for example KG
        if len(df) == 0:
            continue
        assert len(area_in_df) == 1, f"teacher center {center} has multiple areas: {area_in_df}"
        assert area_in_df == area, f"teacher center {center} has wrong area in DF: {area_in_df})"


def test_no_class_time_is_missing(df_att_clean):
    """
    Class should have time.
    """

    assert len(df_att_clean.loc[df_att_clean["class_time"].isna()]) == 0


def test_shared_account_et_is_mapped(df_att_raw):
    """
    Teacher that use shared account should have map in module.shared_acc_et_map
    because scheduling team sometimes does not put the complete name
    for example in description there is 'uzli' which should be mapped to 'Ainiyah Uzlifatul'.
    """

    teacher_contains_online = df_att_raw["Teacher"].str.lower().str.contains("online")
    lower_than_eq_20 = df_att_raw["Teacher"].str.extract("(\d+)")[0].astype(float) <= 20

    list_et_shared = (
        df_att_raw.loc[(teacher_contains_online & lower_than_eq_20), "Description"]
        .str.split("-")
        .str[-1]
        .str.strip()
        .str.lower()
        .fillna("Blank")
        .unique()
        .tolist()
    )
    map_et_shared = module.shared_acc_et_map.keys()
    unmapped = []
    for et in list_et_shared:
        if et == "Blank":
            continue
        elif et not in map_et_shared:
            print(et)
            unmapped.append(et)
    assert len(unmapped) == 0, f"Some ET in shared accouns are unmapped: {unmapped}."


def test_shared_account_class_is_mapped(df_att_clean):
    """
    All class that is taught by teacher using share account must be mapped to real teacher.
    """

    mask = (
        (
            df_att_clean[["teacher_center", "teacher_area", "teacher_position"]]
            == "Shared Account"
        )
        .astype(float)
        .sum(axis=1)
        .astype(bool)
    )
    shared_acc = df_att_clean[mask]

    if len(shared_acc) > 0:
        for teacher in shared_acc["teacher"]:
            print(teacher)

    assert (
        len(shared_acc) == 0
    ), "Some teachers have center/area/position == Shared Account."


def test_goc_class_have_goc_mode(df_att_clean):
    """
    GOC class should have GOC mode.
    """

    if "Global Online Center" in df_att_clean["student_center"].unique():
        assert (
            df_att_clean.loc[
                df_att_clean["student_center"] == "Global Online Center", "class_mode"
            ].unique()
            == "GOC"
        )


def test_teacher_pos_is_complete(df_att_clean):
    """
    All trainer should have position.
    """

    teacher_pos_na = df_att_clean["teacher_position"].isna()
    list_techer_pos_na = df_att_clean.loc[(teacher_pos_na), "teacher"].unique()

    if len(list_techer_pos_na) > 0:
        for teacher in list_techer_pos_na:
            print(teacher)
    assert len(list_techer_pos_na) == 0, "Some teachers have null position."


def test_student_membership_is_mapped(df_att_clean):
    """
    There should only be three memberships.
    """
    memberships = sorted(df_att_clean["student_membership"].unique())
    assert memberships == [
        "Deluxe",
        "GO",
        "VIP",
    ], f"There are unknown membership: {memberships}"


def test_one_code_is_one_name(df_clean, code_col, name_col):
    """One code must have one name only."""

    count_multiple = (df_clean
        .groupby(code_col)    
        .agg(count_student_name=(name_col, "nunique"))
        .reset_index()
        .loc[lambda df_: df_["count_student_name"] > 1, code_col]
        .tolist()
    )
    assert not count_multiple, f"Some codes have multiple names: {count_multiple}"
