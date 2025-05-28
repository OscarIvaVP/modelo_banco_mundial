
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Loop over the different realizations used in the CST
iam_all_real = pd.DataFrame()

for r in range(1,6):
    file = pd.read_csv(
        f'../input/streamflow/CST/Metarunoff_R{r}_DT0_DP100.csv',
        index_col='Date', parse_dates=True)
    
    # Aggregate to monthly
    file_monthly = file.resample('ME').sum()

    # Calculate the average monthly flow for each month
    iam = file_monthly.groupby([file_monthly.index.month]).mean()

    # Concatenate the results with the other realizations
    iam_all_real = pd.concat([iam_all_real, iam], axis=1)

# Calculate the average across realizations for all basins
iam_avg_real = pd.DataFrame(columns=file.columns)
for b in file.columns:
    iam_avg_real[b] = iam_all_real[b].mean(axis=1)


# Calculate the envrionmental flows (i.e., minimum flow requirement to be maintained)
# Following Resolution 200.41-10.1398 (2010), this flow equals 25% of the average dry season flow.
# The dry season is defined as the average of the flows in January, February, March, and December.
Qenv = pd.DataFrame(index=iam_avg_real.columns, columns=['Qenv_monthly_m3', 'Qenv_daily_m3', 'Qenv_monthly_Mm3', 'Qenv_daily_Mm3'])
Qenv['Qenv_monthly_m3'] = iam_avg_real.loc[[1,2,3,12],:].mean() * 0.25
Qenv['Qenv_daily_m3'] = Qenv['Qenv_monthly_m3'] / 30.5
Qenv['Qenv_monthly_Mm3'] = Qenv['Qenv_monthly_m3'] / 10**6
Qenv['Qenv_daily_Mm3'] = Qenv['Qenv_daily_m3'] / 10**6
Qenv.index.name = 'Catchment'
Qenv.to_csv('../input/parameters/minimum_flows_CST.csv')


