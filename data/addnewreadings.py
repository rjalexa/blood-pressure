"""
Read a new BP readings CSV log and if it's compatible with new_bp_log.csv
then add the new readings to the latter file but skip existing rows
"""
import sys
import argparse
import csv
import pandas as pd

CURRENT_LOG = "new_bp_log.csv"
MERGED_LOG = "merged.csv"

# if no file argument provided exit saying so
parser = argparse.ArgumentParser(description="Get a new blood pressure log filename.")
parser.add_argument("newlogfilename")
args = parser.parse_args()

# open and read the destination log file into df_dest
try:
    df_dest = pd.read_csv(CURRENT_LOG)
except FileNotFoundError:
    print(
        f"Cumulative CSV {CURRENT_LOG} file not found. Check if you are in the right directory."
    )
    sys.exit(4)
dest_columns = list(df_dest.columns)
dest_rows = len(df_dest)  # how may rows in the original file

# do the same with the log from which to add readings
# as passed on the program arguments
# if file does not exist exit saying so
try:
    df_new = pd.read_csv(args.newlogfilename)
except FileNotFoundError:
    print(f"File {args.newlogfilename} not found. Please check filename.")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print(f"No data. Please check content of file {args.newlogfilename}")
    sys.exit(2)
new_columns = list(df_new.columns)
# if field names are not identical exit saying so
if not new_columns == dest_columns:
    print(
        f"CSV columns are not the same. Please check content of file {args.newlogfilename}"
    )
    sys.exit(3)

# if they are identical merge the new readings only (avoid duplicates)
print(f"New readings taken from {args.newlogfilename} file.")
df_merged = pd.concat([df_dest, df_new]).drop_duplicates()
merged_rows = len(df_merged)

# sort them by Date descending without creating a DateTime column
# df_merged.sort_values(by=["Date"], inplace=True, ascending=False)
# First convert column to datetimes and get positions of sorted values by Series.argsort
# that is used for change ordering with DataFrame.iloc
#
# argsort is a np.array method that returns an array of indices that would sort the array.
# This is passed to iloc which indexes based on integer position
# in this case, based on the indices returned by argsort
df_merged = df_merged.iloc[
    pd.to_datetime(df_merged["Date"], format="%d %b %Y").argsort()[::-1]
]

# write the resulting file
df_merged.to_csv(
    MERGED_LOG, index=False, encoding="utf-8", quotechar='"', quoting=csv.QUOTE_ALL
)

# print about inspecting it and then deleteing new_bp_log.csv and renaming merge.csv to it
# say how many readings were added
new_rows = merged_rows - dest_rows
print(f"{new_rows} new BP readings have been identified and written to {MERGED_LOG}.")
print(
    f"Please inspect {MERGED_LOG} and if all good, delete {CURRENT_LOG} and then rename {MERGED_LOG} to it."
)
sys.exit(0)
