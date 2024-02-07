from pathlib import Path
from dotenv import load_dotenv
import os


load_dotenv()  # load secret env variable for trainer data

path_raw_data = Path("input/2024/2024-01")  # raw attendance data
month = 1  # specify to obtain current month data only
df_trainer_sheet_name = "2024-01"  # sheet name in trainer data
is_utc = False  # specify if date is in utc (data from ken)
is_mutiple_files = True  # multiple files or one file
path_trainer_data = os.getenv("path_trainer_data")  # path for trainer data

# map centers
# ! update if there are new centers
jkt_1 = ["PP", "SDC", "KG"]
jkt_2 = ["GC", "LW", "BSD", "TBS"]
jkt_3 = ["KK", "CBB", "SMB"]
bdg = ["DG"]
sby = ["PKW"]
centers = jkt_1 + jkt_2 + jkt_3 + bdg + sby
map_centers = {
    "JKT 1": jkt_1,
    "JKT 2": jkt_2,
    "JKT 3": jkt_3,
    "BDG": bdg,
    "SBY": sby,
}
