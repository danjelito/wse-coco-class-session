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
    """

    vips = ["One-on-one", "Online One-on-one", "Online VPG", "VPG"]
    assert (
        sorted(
            (
                df_session.loc[
                    df_session["class_service"] == "VIP", "class_type_grouped"
                ]
            ).unique()
        )
        == vips
    )


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
    num = df_session.loc[df_session["class_type_grouped"] =="Encounter"].shape[0]
    assert not num, "There are encounter in class_type_grouped"