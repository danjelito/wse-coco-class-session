import config


def test_online_class_in_online_location(df_session):
    """
    Class online should have class location online.
    """

    filter_ = df_session["class_type"].str.contains("Online") | df_session[
        "class_type_grouped"
    ].str.contains("Online")
    assert (df_session.loc[filter_, "class_location"] != "Online").sum() == 0


def test_booking_higher_than_eq_attendance(df_session):
    """
    Booking should be >= attendance.
    """

    assert (df_session["class_booking"] < df_session["class_attendance"]).sum() == 0


def test_vip_class_mapped(df_session):
    """
    VIP should have only one-on-one and VPG class.
    In 2023-06 there are VIP members who joined GOC.
    """

    if (
        config.df_trainer_sheet_name == "2023-06"
        # or config.df_trainer_sheet_name == "2023-10"
    ):
        vips = ["GOC", "One-on-one", "Online One-on-one", "Online VPG", "VPG"]
    else:
        vips = ["One-on-one", "Online One-on-one", "Online VPG", "VPG"]

    classes = sorted(
        (
            df_session.loc[df_session["class_service"] == "VIP", "class_type_grouped"]
        ).unique()
    )
    assert classes == vips, f"There are unknown VIP classes: {classes}"


def test_class_service_mapped(df_session):
    """
    There should be only three class service.
    """

    assert sorted(df_session["class_service"].unique()) == [
        "Deluxe",
        "Deluxe & Go",
        "VIP",
    ]


def test_class_type_all_filled(df_session):
    """
    Class type should not be blank.
    """
    na_class_type = df_session.loc[df_session["class_type"].isna()]
    assert not na_class_type.shape[0], f"some class type is na: {na_class_type}"


def test_class_type_grouped_all_filled(df_session):
    """
    Class type grouped should not be blank.
    """
    na_class_type = df_session.loc[df_session["class_type_grouped"].isna()]
    assert not na_class_type.shape[0], f"some class type grouped is na: {na_class_type}"


def test_no_enc_in_class_type_grouped(df_session):
    """
    There should not be encounter in class type grouped.
    """
    num = df_session.loc[df_session["class_type_grouped"] == "Encounter"].shape[0]
    assert num == 0, "There are encounter in class_type_grouped"


def test_class_grouping_is_correct(df_session):
    """Class grouping should be in ["Standard", "VIP", "Other"]."""
    diff =  set(df_session["class_grouping"].unique()) - set(["Standard", "VIP", "Other"])
    assert not diff, f"class_grouping contains unknown columns: {diff}"