# Coco Class Session and Attendance

## Data Source:

Core Course from account jak and inoo, class attendance. Export four times; 1x center class and 1x center students for each account.

## External Dependency:

1. Coco trainer data: consists of teacher data which includes center and working days. Each month, tell TO to fill in the working days of each ET then copy it into local file on input/coco_trainer_data.xlsx.

## How to Use:

1. Copy all attendance files into directory data/{month}/raw.
2. Set the configuration on config.py.
3. Run main.ipynb. This will output two files: raw data per attendance and raw data per session.

## Usage:

1. The output of this processor is used as raw data for experience management report.
