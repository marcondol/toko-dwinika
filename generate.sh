#!/bin/bash

rm -f *.zip

python main.py  --jenisdata order
python main.py  --jenisdata orderdetail

# Get the current year and month
year=$(date +%Y)
month=$(date +%m)

# Set the start date (first day of the month)
#start_date="$year-$month-01"
start_date=$(date -d "last month" +"%Y-%m-1")

# Set the end date (today)
end_date=$(date +%Y-%m-%d)

# Loop through each day from the start date to the end date
current_date=$start_date

while [ "$current_date" != "$end_date" ]; do
  # Print the current date
  echo "$current_date"
  python main.py --jenisdata tax-10 --date "$current_date"
  # Increment the date by one day (using a more portable method)
  current_date=$(date -I -d "$current_date + 1 day")

done

# Print the end date
echo "$end_date"

echo "Script completed."
