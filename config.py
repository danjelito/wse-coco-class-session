from pathlib import Path
from dotenv import load_dotenv
import os


load_dotenv()  # load secret env variable for trainer data

path_raw_data = Path("input/2024/2024-03")  # raw attendance data
month = 3  # specify to obtain current month data only
df_trainer_sheet_name = "2024-03"  # sheet name in trainer data
is_utc = False  # specify if date is in utc (data from ken)
is_mutiple_files = True  # multiple files or one file
path_trainer_data = os.getenv("path_trainer_data")  # path for trainer data


# map centers
# ! update if there are new centers
class CenterMap:
    def __init__(self) -> None:
        self.center_area = {
            "PP": "JKT 1",
            "SDC": "JKT 1",
            "KG": "JKT 1",
            "GC": "JKT 2",
            "LW": "JKT 2",
            "BSD": "JKT 2",
            "TBS": "JKT 2",
            "CP": "JKT 2",
            "KK": "JKT 3",
            "CBB": "JKT 3",
            "SMB": "JKT 3",
            "DG": "BDG",
            "PKW": "SBY",
            "HO": "HO",
            "Street Talk": "Street Talk",
            "Corporate": "Corporate",
            "Online Center": "Online Center",
            "Curioo": "Curioo",
            "RST": "RST",
            "NST": "NST",
        }

    def get_center(self) -> set:
        """Return set of centers."""
        return set(k for k, v in self.center_area.items())

    def get_area(self) -> set:
        """Return list of areas."""
        return set(v for k, v in self.center_area.items())

    def get_center_area_map(self) -> dict:
        """Returns center: area"""
        return self.center_area

    def lookup_area(self, center) -> set:
        """Return area of inputted center."""
        if center not in self.center_area.keys():
            raise ValueError(
                f"Center {center} is not a valid center. Select one of {set(self.center_area.keys())}"
            )
        return self.center_area[center]

    def lookup_centers(self, area) -> set:
        """Return centers of inputted area."""
        if area not in self.center_area.values():
            raise ValueError(
                f"Area {area} is not a valid area. Select one of {set(self.center_area.values())}"
            )
        return set(k for k, v in self.center_area.items() if v == area)


# jkt_1 = ["PP", "SDC", "KG"]
# jkt_2 = ["GC", "LW", "BSD", "TBS"]
# jkt_3 = ["KK", "CBB", "SMB"]
# bdg = ["DG"]
# sby = ["PKW"]
# centers = jkt_1 + jkt_2 + jkt_3 + bdg + sby
# map_centers = {
#     "JKT 1": jkt_1,
#     "JKT 2": jkt_2,
#     "JKT 3": jkt_3,
#     "BDG": bdg,
#     "SBY": sby,
# }
