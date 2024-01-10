import module


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


def test_class_center_match_with_class_area(df_att_clean, map_centers):
    """
    Class center should match with the correct area.
    """

    for area, centers in map_centers.items():
        assert (
            df_att_clean.loc[
                df_att_clean["class_location"].isin(centers), "class_area"
            ].unique()
            == area
        ).all()


def test_teacher_center_match_with_teacher_area(df_att_clean, map_centers):
    """
    Teacher center should match with the correct area.
    """

    for area, centers in map_centers.items():
        assert (
            df_att_clean.loc[
                df_att_clean["teacher_center"].isin(centers), "teacher_area"
            ].unique()
            == area
        ).all()


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
        .unique()
    )
    map_et_shared = module.shared_acc_et_map.keys()
    unmapped = []
    for et in list_et_shared:
        if et not in map_et_shared:
            print(et)
            unmapped.append(et)
    assert len(unmapped) == 0, "Some ET in shared accouns are unmapped."


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

    assert sorted(df_att_clean["student_membership"].unique()) == [
        "Deluxe",
        "GO",
        "VIP",
    ]
