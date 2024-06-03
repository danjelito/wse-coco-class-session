# Coco Class Session and Attendance

## Data Source:

Core Course from account jak and inoo, class attendance. Export four times; 1 center class and 1 center students for each account.

## External Dependency:

1. Coco trainer data: consists of teacher data which includes center and working days. Each month, tell TO to fill in the working days of each ET then copy it into local file (/home/anj/Documents/wse-local/2. Experience/dependencies/Trainer Working Days (Sync with Local).xlsx).

## How to Use:

1. Download attendance files.
2. Copy all attendance files into directory input/{year}/{month}.
3. Complete the coco trainer data for that month.
4. Set the configuration on config.py.
5. IMPORTANT: Specify path to Coco trainer data in `./.env`.
6. Run main.ipynb. This will output two files: raw data per attendance and raw data per session.

## Usage:

1. The output of this processor is used as raw data for experience management report.

## TODO: 
