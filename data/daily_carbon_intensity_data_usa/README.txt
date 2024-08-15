Dataset Title: Hourly Carbon Intensity Averages and Distributions for 2022

Description:
This dataset contains processed results of carbon intensity measurements for the year 2022, grouped by hour. Each file in the dataset corresponds to a specific source CSV file and includes statistical summaries such as mean, standard deviation, and selected percentiles (ranging from p0 to p90 in steps of 10 and from p91 to p100 in steps of 1) of carbon intensity averages.

Source Data:
The data were derived from original CSV files containing detailed carbon intensity measurements along with timestamps spanning from 2020 to 2022. Each source file was processed to filter data for 2022, grouped by the hour of measurement.

Data Processing:
1. Filtering to include only data from the year 2022.
2. Grouping data by hour of the day.
3. Calculating the mean and standard deviation of carbon intensity for each hour.
4. Calculating percentiles for each hourly group.
5. Rounding all statistics to two decimal places.

Columns:
1. Hour: Hour of the day (0-23)
2. Mean: Mean carbon intensity for the hour (rounded to two decimal places)
3. Std: Standard deviation of carbon intensity for the hour (rounded to two decimal places)
4. p0 to p90: Percentiles from 0 to 90 at 10-point intervals (rounded to two decimal places)
5. p91 to p100: Percentiles from 91 to 100 at 1-point intervals (rounded to two decimal places)

Usage Notes:
- Each row in the file corresponds to an hour of the day.
- Values are based on local time associated with each measurement.

File Naming Convention:
Each file is named according to its source with an added suffix '_avg_std_dist.csv' to denote that it contains processed data including averages, standard deviations, and distributions.

For example:
- original_filename.csv -> original_filename_avg_std_dist.csv


License:
Open Database License (https://opendatacommons.org/licenses/odbl/)
Attribute to ElectricityMaps; more details are available at https://www.electricitymaps.com/data-portal. 
