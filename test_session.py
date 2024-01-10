def test_online_class_in_online_location(df_session):
    """
    Class online should have class location online.
    """

    filter_ = df_session["class_type"].str.contains("Online") | df_session["class_type_grouped"].str.contains("Online")
    assert (df_session.loc[filter_, "class_location"] != "Online").sum() == 0


def test_booking_higher_than_eq_attendance(df_session):
    """
    Booking should be >= attendance.
    """

    assert (df_session['class_booking'] < df_session['class_attendance']).sum() == 0


def test_vip_class_mapped(df_session):
    """
    VIP should have only one-on-one and VPG class.
    """

    vips= [
        'One-on-one',
        'Online One-on-one',
        'Online VPG',
        'VPG']
    assert sorted((df_session.loc[df_session['class_service'] == 'VIP', 'class_type_grouped']).unique()) == vips


def test_class_service_mapped(df_session):
    """
    There should be only three class service.
    """

    assert sorted(df_session['class_service'].unique()) == ['Deluxe', 'Deluxe & Go', 'VIP']