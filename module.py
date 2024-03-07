import numpy as np
import pandas as pd

import config


# configuration
is_utc = config.is_utc
df_teacher_sheet_name = config.df_trainer_sheet_name
month = config.month
path_trainer_data = config.path_trainer_data


map_col = {
    "Student": "Student Name",
    "Student Name": "Student Name",
    "username": "Student Code",
    "Student Code": "Student Code",
    "Service Type": "Student Membership",
    "Center": "Student Center",
    "Center Name": "Student Center",
    "Result": "Student Result",
    "Class Type": "Class Type",
    "Type of Class\nAll Class": "Class Type",
    "startdate": "Class Date",
    "Class Startdate": "Class Date",
    "Unit/Level": "Class Unit",
    "ClassDescription": "Class Description",
    "Description": "Class Description",
    "Class Start Time": "Class Time",
    "Duration": "Class Duration",
    "Unit": "Class Unit",
    "Teacher": "Teacher",
}


def convert_to_gmt_plus_7(
    df: pd.DataFrame, column: str, is_utc: bool = is_utc
) -> pd.Series:
    """
        Convert date to GMT+7 if date is in UTC.
        Data from Ken is in UTC but data from Coco is in UTC+7.

    Args:
        df (pd.DataFrame)
        column (str): Column to process.
        is_utc (bool, optional): True if column is in UTC. Defaults to is_utc.

    Returns:
        pd.Series: Converted time.
    """

    if is_utc == True:  # if df is in UTC
        dates = pd.to_datetime(df[column], utc=True).dt.tz_convert("Asia/Jakarta")
    else:  # if df is already in local time
        dates = pd.to_datetime(df[column])
    return dates


def create_class_time(df: pd.DataFrame):
    """
        Create time column if not already available,
        then convert to %H:%M format,
        then convert to categorical for sorting.

    Args:
        df (pd.DataFrame)

    Returns:
        pd.CategoricalDtype: Clean and formatted class time.
    """
    hours = pd.date_range(
        start="2023-01-01", end="2023-01-02", freq="30 min", inclusive="left"
    )
    hours = [hour.strftime("%H:%M") for hour in hours]
    hours_cat = pd.CategoricalDtype(hours, ordered=True)

    if "class_time" in df.columns:
        class_time = df["class_time"].astype(hours_cat)
    else:
        class_time = df["class_date"].dt.strftime("%H:%M")
        class_time = class_time.astype(hours_cat)

    # note: this is to make sure that there is no NaN in hours column
    # debugged at 2023-04-05 with Lintang
    if class_time.isna().sum() > 0:
        raise Exception("There are NaNs in hours col.")

    return class_time


def clean_teacher_name(df: pd.DataFrame):
    """
        Clean teacher name and remove duplicated name.
        # ! If duplicated, always choose the longest name.

    Args:
        dataframe (pd.DataFrame)

    Returns:
        series: Cleaned name.
    """

    teachers = (
        df["teacher"]
        .str.replace("\(.*\)", "", regex=True)
        .str.replace("   ", " ", regex=False)
        .str.replace("  ", " ", regex=False)
        .str.strip()
        .str.title()
        # replace duplicated names
        .replace(
            {
                "Azhar Rahul": "Azhar Rahul Finaya",
                "Handayani Risma": "Handayani Khaerunisyah Risma",
                "Kartikasari Prettya": "Kartikasari Prettya Nur",
                "Ramadhan Ira Ragil": "Ramadhani Ira",
                "S Allan": "Santiago Allan",
                "Gandhama Jesita": "Ghandama Jesita",
                "Istiqomah Diah": "Toluhula Diah Istiqomah",
                "Putri Tiara": "Setiawan Tiara Putri",
                "Ratnasari Handayani Hamsah": "Hamsah Handayani Ratnasari",
                "Hamsah Ratnasari Handayani": "Hamsah Handayani Ratnasari",
                "Kaleb Arthur Mordechai": "Mordechai Kaleb Arthur",
                "Mordechai Arthur Kaleb": "Mordechai Kaleb Arthur",
                "Bushey Michael James": "Bushey James Michael",
            }
        )
    )
    return teachers


def create_class_mode(df: pd.DataFrame):
    """
        Create class mode either offline or online.
        If class contains string 'online', then class_mode = 'Online'.
        If teacher center == 'International' then GOC

    Args:
        df (pd.DataFrame)

    Returns:
        series: class_mode
    """
    conditions = [
        # GOC
        df["student_center"] == "Global Online Center",
        df["teacher_center"] == "International",
        # if class name container "online" then online class
        df["class_type"].str.lower().str.contains("online", regex=False, na=False),
        # else, offline class
        True,
    ]
    choices = ["GOC", "GOC", "Online", "Offline"]

    classes = np.select(conditions, choices, default="Error")
    return classes


def create_attend(df: pd.DataFrame):
    """
        Create attend / not attend col.

    Args:
        df (pd.DataFrame)

    Returns:
        pd.Series: Attend/not attend.
    """
    attend = [
        "Continue",
        "Passed",
        "Repeat",
    ]  # note: these results are considered attending. other that this, not attend
    attendances = np.where(df["student_result"].isin(attend), "Attend", "Not Attend")
    return attendances


def create_student_membership(df: pd.DataFrame):
    """
        Create series marking student membership type.
        Standard Deluxe can join online and offline class.
        Standard GO can only join online class.
        # note: as per 2023-02-08, CAD has put (GO) in all GO members, making it possible to separate GO.

    Args:
        df (pd.DataFrame)

    Returns:
        memberships
    """
    membership_contains_std = df["student_membership"] == "Standard"
    membership_contains_vip = df["student_membership"] == "VIP"
    name_contains_dlx = (
        df["student_name"].str.upper().str.contains("(DLX", regex=False, na=False)
    )
    name_contains_go = (
        df["student_name"].str.upper().str.contains("(GO", regex=False, na=False)
    )
    mask_deluxe_1 = (~name_contains_go) & membership_contains_std
    mask_deluxe_2 = (~name_contains_go) & name_contains_dlx

    # mar 2024
    # there is one vip members who are incorrectly assigned into deluxe
    name_dekki = df["student_name"].str.upper().str.contains("DEKKI", regex=False, na=False)
    code_8184 = df["student_code"].str.contains("8184", regex=False, na=False)

    conditions = [
        (name_dekki & code_8184), 
        name_contains_go,  # if name contains go then go member
        mask_deluxe_1,  # if name not contain go and membership contains dlx then dlx
        mask_deluxe_2,  # if name not contain go and name contains dlx then dlx
        membership_contains_vip,  # if membership contains VIP
    ]
    choices = ["VIP", "GO", "Deluxe", "Deluxe", "VIP"]
    memberships = np.select(conditions, choices, default="Error")

    return memberships


def create_duration(df: pd.DataFrame):
    """
        DF from Ken does not contain duration.
        If there is no duration column, then infer that all classes is 1h.

    Args:
        df (pd.DataFrame)

    Returns:
        series
    """

    if "class_duration" in df.columns:
        # if duration is in minute
        if df["class_duration"].max() >= 60:
            durations = df["class_duration"] / 60
        # if duration is in hour
        else:
            durations = df["class_duration"]
    else:
        # if there is no duration
        durations = 1
    return durations


def load_df_teacher(df_teacher_sheet_name: str = df_teacher_sheet_name):
    """
        Teacher df to get teacher center and area

    Args:
        sheet_name (str): sheet_name per month

    Returns:
        pd.DataFrame
    """
    df_teacher = pd.read_excel(
        io=path_trainer_data,
        sheet_name=df_teacher_sheet_name,
        usecols=["coco_teacher_name", "teacher_center", "teacher_area", "teacher_position"],
    )
    return df_teacher


def create_class_location_1(df: pd.DataFrame):
    """create class location from description

    Args:
        df (dataframe)

    Returns:
        series: class location
    """

    class_locations = (
        df.loc[:, "class_description"]
        .str.lower()
        .str.replace(" at ", " @", regex=False)  # replace at with @
        # .str.replace('at ', ' @', regex= False) # replace at with @
        .str.replace("@ ", "@", regex=False)  # remove space after at
        .str.replace("@ work", "at work", regex=False)  # remove @ for recharge class
        .str.replace("@hour", "at time", regex=False)  # remove @ for time
        .str.replace("(@\d)", "at time", regex=True)  # remove @ for time
        # replace other odd value
        .str.replace(
            "@paddington|@conversationalists|@is|@the|@to|@these|@work|@would|@complaining",
            "at other",
            regex=True,
        )
        .str.replace(
            "@i|@wse|@pancar|@haris|@harris|@a|@paddington|@do|@padingtton",
            "at other",
            regex=True,
        )
        .str.replace("pacific place", "pp", regex=False)
        .str.replace("sedayu city", "sdc", regex=False)
        .str.replace("kelapa gading", "kg", regex=False)
        .str.replace("gandaria city", "gc", regex=False)
        .str.replace("gandaira city", "gc", regex=False)
        .str.replace("gandaira", "gc", regex=False)
        .str.replace("living world", "lw", regex=False)
        .str.replace("tb simatupang", "tbs", regex=False)
        .str.replace("simatupang", "tbs", regex=False)
        .str.replace("kota kasablanka", "kk", regex=False)
        .str.replace("kokas", "kk", regex=False)
        .str.replace("cibubur", "cbb", regex=False)
        .str.replace("pakuwon", "pkw", regex=False)
        .str.replace("dago", "dg", regex=False)
        .str.extract("(@\w*)")
        .replace("@", np.nan)[0]
        .str.replace("@", "")
        .str.upper()
    )
    return class_locations


def create_class_location_2(df: pd.DataFrame):
    """
        Create class location from teacher center
        provided that class is offline but class location is not in description.

    Args:
        df (dataframe)

    Returns:
        series: class location
    """

    class_locations = np.where(
        (df["class_mode"] == "Offline") & ~(df["class_location"].isin(config.centers)),
        df["teacher_center"],
        df["class_location"],
    )
    return class_locations


def create_class_location_3(df: pd.DataFrame, month=month):
    """create class location for moving ET.
    # ! Currently unused.

    Args:
        df (dataframe)

    Returns:
        series: class location
    """

    # daniel sat PP -> SDC
    # jason thu sat SDC -> PP
    mask_daniel = (
        (df["teacher"] == "Bradshaw Daniel")
        & (df["class_mode"] == "Offline")  # daniel
        & (df["class_date"].dt.day_name().isin(["Saturday"]))  # offline class
        & (df["class_description"].str.contains("@") == False)  # saturday
        & (  # no class loc description
            df["class_description"].str.contains(" at ") == False
        )
    )
    mask_jason = (
        (df["teacher"] == "Gereau Jason Jarett")
        & (df["class_mode"] == "Offline")  # jason
        & (  # offline class
            df["class_date"].dt.day_name().isin(["Thursday", "Saturday"])
        )
        & (df["class_description"].str.contains("@") == False)  # thu and sat
        & (  # no class loc description
            df["class_description"].str.contains(" at ") == False
        )
    )
    if (month == 10) | (month == 11) | (month == 12) | (month == 1) | (month == 2):
        class_locations = np.select(
            condlist=[mask_daniel, mask_jason],
            choicelist=["SDC", "PP"],
            default=df["class_location"],
        )
    else:
        class_locations = df["class_location"]
    return class_locations


def assert_class_location_online(df: pd.DataFrame):
    """Assert that class_location for online class is 'Online'

    Args:
        df (pd.DataFrame)

    Returns:
        pd.Series
    """

    class_locations = np.where(
        df["class_mode"] == "Online", "Online", df["class_location"]
    )
    return class_locations


def create_class_location_area(df: pd.DataFrame):
    """Group class location per area

    Args:
        df (pd.DataFrame)

    Returns:
        pd.Series
    """

    class_location_area = np.select(
        condlist=[
            df["class_location"].isin(config.jkt_1),
            df["class_location"].isin(config.jkt_2),
            df["class_location"].isin(config.jkt_3),
            df["class_location"].isin(config.bdg),
            df["class_location"].isin(config.sby),
            df["class_location"] == "Online",
        ],
        choicelist=["JKT 1", "JKT 2", "JKT 3", "BDG", "SBY", "Online"],
        default="Error",
    )
    return class_location_area


def create_class_service(df: pd.DataFrame):
    """
        If class does not contain non-VIP, then it is a VIP class
        If class contains non-VIP and offline, then it is a deluxe class
        If class contains non-VIP and online, then it is a deluxe + go class

    Args:
        df (pd.DataFrame)

    Returns:
        series: class_service
    """

    contains_vip = (
        df["student_membership_grouped"]
        .astype(str)
        .str.contains("VIP", na=False, regex=False)
    )
    contains_non_vip = (
        df["student_membership_grouped"]
        .astype(str)
        .str.contains("Deluxe", na=False, regex=False)
    ) | (
        df["student_membership_grouped"]
        .astype(str)
        .str.contains("GO", na=False, regex=False)
    )
    online = df["class_mode"] == "Online"
    offline = df["class_mode"] == "Offline"
    class_mode_goc = df["class_mode"] == "GOC"
    teacher_center_int = df["teacher_center"] == "International"

    conditions = [
        ~contains_non_vip,  # does not contain non vip -> vip
        (contains_non_vip & offline),  # non-vip & offline -> deluxe
        (contains_non_vip & online),  # non-vip & online -> deluxe and go
        (class_mode_goc | teacher_center_int),
    ]
    choices = ["VIP", "Deluxe", "Deluxe & Go", "Deluxe & Go"]
    class_service = np.select(conditions, choices, default="Error")
    return class_service


def create_class_attendance(df: pd.DataFrame):
    """
        Count the number of students who attend.

    Args:
        df (pd.DataFrame)

    Returns:
        series: class_attendance
    """

    class_attendance = (
        df["student_attendance_grouped"]
        .astype(str)
        .str.replace("Not Attend", "Not", regex=False)
        .str.count("Attend")
    )
    return class_attendance


def create_class_booking(df: pd.DataFrame):
    """Count the number of members who booked the class.

    Args:
        df (pd.DataFrame)

    Returns:
        series: class_bookings
    """

    class_booking = df["student_attendance_grouped"].astype(str).str.count(",") + 1
    return class_booking


def create_class_status(df: pd.DataFrame):
    """
        If class attendance = 0, then class not given

    Args:
        df (pd.DataFrame)

    Returns:
        series: class_status
    """
    class_status = np.where((df["class_attendance"] > 0), "Given", "Not Given")
    return class_status


def create_class_type_grouped(df: pd.DataFrame):
    """
        Convert class type for VIP members to VIP format.
        VIP should only have 2 types of classes: 1:1, VPG.
        2023-03-16 separate offline SC to offline SC and offline CH
        2023-06-14 create separate class for community

    Args:
        df (pd.DataFrame)

    Returns:
        pd.Series: class_type_vip
    """

    # online and offline class
    online = df["class_mode"] == "Online"
    offline = df["class_mode"] == "Offline"

    # class contains only vip members
    only_vip = ~(
        df["student_membership_grouped"]
        .astype(str)
        .str.contains("Deluxe|GO", regex=True, na=False)
    )

    # class description contains vpg
    vpg = df["class_description"].astype(str).str.lower().str.contains("vpg", na=False)

    online_wel = df["class_type"] == "Online Welcome"
    online_adv = df["class_type"] == "Online Advising Session"
    adv = df["class_type"] == "Advising Session"
    fl = df["class_type"] == "First Lesson"

    # chat hour
    chat_hour = (
        df["class_description"]
        .astype(str)
        .str.lower()
        .str.contains("chat hour", regex=False)
    )
    # sc
    social_club = df["class_type"] == "Social Club"

    # community class
    community = (
        df["class_description"]
        .str.lower()
        .str.contains("cre-8|cre 8|cre8|syndicate|re-charge|re charge|recharge|leap")
    )

    # teacher center = international
    international = df["teacher_center"] == "International"

    # online encounter
    online_enc = df["class_type"] == "Online Encounter"

    class_type_vip = np.select(
        condlist=[
            (only_vip & vpg & offline),  # offline vpg
            (only_vip & vpg & online),  # online vpg
            (only_vip & ~vpg & offline),  # offline 1 1
            (only_vip & ~vpg & online),  # online 1 1
            (online_wel),
            (online_adv),
            (adv),
            (fl),
            (offline & community),  # offline comm
            (online & community),  # online comm
            (offline & chat_hour & social_club),  # offline ch
            (online & chat_hour & social_club),  # online ch
            (only_vip & international & online_enc),  # GOC VIP
        ],
        choicelist=[
            "VPG",
            "Online VPG",
            "One-on-one",
            "Online One-on-one",
            "Online First Lesson",
            "Online Advising Session",
            "Advising Session",
            "First Lesson",
            "Community",
            "Online Community",
            "Chat Hour",
            "Online Chat Hour",
            "GOC",
        ],
        default=df["class_type"],
    )
    return class_type_vip


shared_acc_et_map = {
    "uzli": "Ainiyah Uzlifatul",
    "alex": "Algar Sinclair Alexander John",
    "anggi": "Ansyahputri Anggita Rizkiarachma",
    "anggita": "Ansyahputri Anggita Rizkiarachma",
    "shafira": "Ayuningtyas Shafira",
    "rahul": "Azhar Rahul Finaya",
    "imelda": "Basuki Imelda",
    "ryan b": "Blasczyk Ryan",
    "ryan": "Blasczyk Ryan",
    "daniel": "Bradshaw Daniel",
    "fairuz": "Fairuz Muhammad",
    "jason": "Gereau Jason Jarett",
    "risma": "Handayani Khaerunisyah Risma",
    "vivi": "Hazisyah Alifia Nur",
    "alifia": "Hazisyah Alifia Nur",
    "tri bekti": "Hundoyo Tri Bekti",
    "tri": "Hundoyo Tri Bekti",
    "madeline": "Jane Quinn Madeline",
    "jack jones": "Jones Jack William Isaac",
    "prettya": "Kartikasari Prettya Nur",
    "derek": "Laurendeau Derek",
    "john lawrence": "Lawrence Moore John",
    "john": "Lawrence Moore John",
    "john moore": "Lawrence Moore John",
    "medi": "Medianti Annisa",
    "eka": "Mustikawati Eka",
    "nadya": "Nasarah Nadya",
    "ruth olivia": "Pakpahan Ruth Olivia Angelina",
    "olivia": "Pakpahan Ruth Olivia Angelina",
    "oliv": "Pakpahan Ruth Olivia Angelina",
    "olive": "Pakpahan Ruth Olivia Angelina",
    "toby": "Phillips Toby",
    "priscill": "Priscilla Yokhebed",
    "priscilla": "Priscilla Yokhebed",
    "priscil": "Priscilla Yokhebed",
    "nova": "Rahmadya Nova Ayu",
    "aurora": "Rifani Aurora Nurhidayah",
    "rifani": "Rifani Aurora Nurhidayah",
    "roger": "Szlatiner Roger Bernad",
    "ade": "Setiadi Sapto",
    "anna": "Tinggogoy Anna Maria",
    "ana": "Tinggogoy Anna Maria",
    # added in july 2023
    # elsa forget to put - in description
    "amir": "Ghazi Amir Hassan",
    "chris s": "Sutcliffe Christopher",
    "under online trainer 6 (62.jak05.o6)": "Bradshaw Daniel",
    "vpg online: feminism (roger)": "Szlatiner Roger Bernad",
    "farida go member (uzli)": "Ainiyah Uzlifatul",
    "vpg online: being tactful (jason)": "Gereau Jason Jarett",
    "chris": "Sutcliffe Christopher",
    "nan": "Blank",
    np.nan: "Blank",
    'up "fame and fortune" (priscill)': "Priscilla Yokhebed",
    "anggi kk": "Ansyahputri Anggita Rizkiarachma",
    "dimas kk": "Pratama Dimas Indra",
    "prettya pkw": "Kartikasari Prettya Nur",
    "priscill (sdc)": "Priscilla Yokhebed",
    "medi (smb)": "Medianti Annisa",
    "uzli pp": "Ainiyah Uzlifatul",
    "jurado": "Jurado Michael John",
    "online social hour: fixing problems (ade)": "Setiadi Sapto",
    "charge meet up: exploring the science of sugar rush (eka dg)": "Mustikawati Eka",
    "online social hour: fixing problems (daniel)": "Bradshaw Daniel",
    "ade sapto": "Setiadi Sapto",
    "daniel (stative verb)": "Bradshaw Daniel",
    "edy junaedi @pp": "Priscilla Yokhebed",
    "adhit": "Reinindra Adhitya",
    "brian": "Johanson Brian",
    "firda": "Fadhilah Firdausa",
    "ratna": "Hamsah Handayani Ratnasari",  # Jul PP, after that SDC
    "ratna (nana)": "Hamsah Handayani Ratnasari",  # Jul PP, after that SDC
    "nana": "Hamsah Handayani Ratnasari",  # Jul PP, after that SDC
    "kaleb": "Mordechai Kaleb Arthur",  # PP
    "imel": "Basuki Imelda",
    "hary @pp imelda": "Basuki Imelda",
    "jack elfrink": "Francis Elfrink Jack",
    "jack": "Jones Jack William Isaac",
    # added in aug 2023
    "grace": "Melody Grace",
    "grace pkw": "Melody Grace",
    "dimas": "Pratama Dimas Indra",
    "ratna sdc": "Hamsah Handayani Ratnasari",
    "dimas indra": "Pratama Dimas Indra",
    "kenny": "Prasheena Kainaz",
    "pre int, online (toby)": "Phillips Toby",
    "james": "Bushey James Michael",
    "indra bestari @gc": "Reinindra Adhitya",
    "covered by adit": "Fairuz Muhammad",
    # added in sep 2023
    "abi @pp replacement": "Gereau Jason Jarett",
    "kenny kk": "Prasheena Kainaz",
    "firda community team": "Fadhilah Firdausa",
    "firda comm team": "Fadhilah Firdausa",
    "tasya pkw": "Murti Gitasya",
    "adit community team": "Reinindra Adhitya",
    "adit comm team": "Reinindra Adhitya",
    "tasya": "Murti Gitasya",
    "tribekti": "Hundoyo Tri Bekti",
    "catherine @pp replacement": "Mordechai Kaleb Arthur",
    "titin @pp replacement": "Mordechai Kaleb Arthur",
    "ani": "Cahyani Ani Rahma",
    "cindy": "Oktavia Cindy",
    # added in dec 2023
    "community team": "Community Team",
    "christy": "Waney Natalia Christy",
    "connor": "Lee Platel Connor",
    "fita": "Saputri Okfitasari Hana",
    "jack jonees": "Jones Jack William Isaac",
    "rozak": "Rozak Abdul Rahman",
    "putri": "Khalisa Fairuz Putri",
    # added in jan 2024
    "okfita": "Saputri Okfitasari Hana",
    "gitasya": "Murti Gitasya",
    "peter": "Mowatt Peter Denis",
    # added in feb 2024
    "comm team": "Community Team",
    "garce": "Melody Grace",
    "nita @ gc replacement": "Fairuz Muhammad",
}


def clean_shared_account_et(df: pd.DataFrame):
    """
    Map ET for classes with shared Coco account.
    After May 2023, some classes use shared account, therefore those
    classes's ET can only be obtained from class description.

    Args:
        df (pd.DataFrame): DF to process

    Returns:
        pd.Series: Mapped ET name for these classes.
    """

    contains_online = df["teacher"].str.lower().str.contains("online")
    more_than_20 = df["teacher"].str.extract("(\d+)")[0].astype(float) > 20  # ooolab
    lower_than_eq_20 = df["teacher"].str.extract("(\d+)")[0].astype(float) <= 20

    conditions = [
        (contains_online & lower_than_eq_20),
    ]
    choices = [
        (
            df["class_description"]
            .str.split("-")
            .str[-1]
            .str.strip()
            .str.lower()
            .map(shared_acc_et_map)
        ),
    ]
    return np.select(conditions, choices, default=df["teacher"])
