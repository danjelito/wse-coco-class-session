from pathlib import Path

# ! path for raw attendance data
path = Path("data/12 dec 2023")

# ! specify to obtain current month data only
month = 12

# ! specify df_teacher sheet name
df_teacher_sheet_name = str(path.stem)

# specify if date is in utc (data from ken)
is_utc = False

# specify if the data has 2 headers (data from coco)
has_headers = True

# multiple files from coco that need to be concatted
is_mutiple_files = True
