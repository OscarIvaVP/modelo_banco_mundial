
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


DAMS = ('Guavio', 'Garagoa')

DAM_OP = (
    ('../data/Reservoirs/Guavio_dam.csv', '2000-1-1', '2014-12-31'),
    ('../data/Reservoirs/Bata_dam.csv', '1977-5-1', '2021-12-31')
    
    )

INFLOW_GR2M = (
    ('../input/streamflow/historical/observed_monthly_flows_cmd.csv', 'Guavio'),  
    ('../input/streamflow/historical/observed_monthly_flows_cmd.csv', 'Garagoa')
    )
 
    
for i, reservoir in enumerate(DAMS):

    inflow = pd.read_csv(INFLOW_GR2M[i][0], index_col='Date',
                         usecols=['Date', INFLOW_GR2M[i][1]],
                         parse_dates=True)
                      
    inflow = inflow.truncate(before=DAM_OP[i][1], after=DAM_OP[i][2], copy=False)
    inflow_month = inflow.resample('M').mean()/10**6
    
    inflow_month['month_total'] = [inflow_month.values[x][0] * inflow_month.index.day[x] for x in range(len(inflow_month))]
    iam_flow_m = inflow_month['month_total'].groupby(inflow_month.index.month).mean()
    iam_flow_q25 = inflow_month['month_total'].groupby(inflow_month.index.month).quantile(0.25)
    iam_flow_q75 = inflow_month['month_total'].groupby(inflow_month.index.month).quantile(0.75)
    
    if reservoir == 'Garagoa':
        dam_op = pd.read_csv(DAM_OP[i][0], index_col='Date', 
                    usecols=['Date', 'Volumen m3', 'Turbinado'],
                    parse_dates=True, encoding='ISO-8859-1')
        
        dam_op = dam_op.truncate(before=DAM_OP[i][1], after=DAM_OP[i][2], copy=False)
        dam_op_month = dam_op['Volumen m3'].resample('M').mean()/10**6
        
        
        iam_dam_op_m = dam_op_month.groupby(dam_op_month.index.month).mean()
        iam_dam_op_q25 = dam_op_month.groupby(dam_op_month.index.month).quantile(0.25)
        iam_dam_op_q75 = dam_op_month.groupby(dam_op_month.index.month).quantile(0.75)
        
        fig, ax = plt.subplots(1,1)
        ax.plot(np.arange(1,13),iam_dam_op_m, 'k')
        ax.fill_between(np.arange(1,13),iam_dam_op_q25,iam_dam_op_q75, iam_dam_op_q75>iam_dam_op_q25, color='gray', alpha=0.2)


        ax.plot(np.arange(1,13),iam_flow_m,'b')
        ax.fill_between(np.arange(1,13),iam_flow_q25,iam_flow_q75, iam_flow_q75>iam_flow_q25, color='b', alpha=0.2)
        
        
        plt.show()
        
    elif reservoir == 'Guavio':
        dam_op = pd.read_csv(DAM_OP[i][0], index_col='Date', 
                    usecols=['Date', 'Volumen Útil Diario m3'],
                    parse_dates=True, encoding='ISO-8859-1')
        
        dam_op = dam_op.truncate(before=DAM_OP[i][1], after=DAM_OP[i][2], copy=False)
        dam_op.replace(0,np.nan, inplace=True)
        dam_op_month = dam_op['Volumen Útil Diario m3'].resample('M').sum()/10**6
        
        
        iam_dam_op_m = dam_op_month.groupby(dam_op_month.index.month).mean() * 0.945
        iam_dam_op_q25 = dam_op_month.groupby(dam_op_month.index.month).quantile(0.25) * 0.945
        iam_dam_op_q75 = dam_op_month.groupby(dam_op_month.index.month).quantile(0.75) * 0.945
        
        fig, ax = plt.subplots(1,1)
        ax.plot(np.arange(1,13),iam_dam_op_m, 'k')
        ax.fill_between(np.arange(1,13),iam_dam_op_q25,iam_dam_op_q75, iam_dam_op_q75>iam_dam_op_q25, color='gray', alpha=0.2)


        ax.plot(np.arange(1,13),iam_flow_m,'b')
        ax.fill_between(np.arange(1,13),iam_flow_q25,iam_flow_q75, iam_flow_q75>iam_flow_q25, color='b', alpha=0.2)
        
        
        plt.show()    
        sadf
        
    
    #if reservoir == 'Guavio':
    
    #    # For Guavio, the turbined flow is not available and must be estimated 
    #    # through mass balance (evap and precip over the lake are disregarded)
        
    #    # S_t+1 = S_t + Q_t - Turb_t - Spill_t
    #    # -->
    #    # turb_flow = S_t+1 - S_t - Q_t + Spill_t
    
    
    #   # Read the file 
    #    dam_op = pd.read_csv(DAM_OP[i][0], index_col='date', 
    #                usecols=['date', 'Volumen Útil Diario m3', 
    #                    'Vertimientos Volumen m3'],
    #                parse_dates=True, encoding='ISO-8859-1')
            
    #    dam_op.rename(columns={
    #        'Volumen Útil Diario m3': 'Volume (m3)',
    #        'Vertimientos Volumen m3': 'Spill (m3d-1)'},
    #        inplace=True)
    #    
    #    dam_op = dam_op.truncate(before=DAM_OP[i][1], after=DAM_OP[i][2], copy=False)
    #    dam_op_month = dam_op.resample('M').mean()
    #    
    #    turb = dam_op_month['Volume (m3)'][1:].values \
    #         - dam_op_month['Volume (m3)'][:-1].values \
    #         - inflow_month[INFLOW_GR2M[i][1]][:-1].values #\
    #         #+ dam_op_month['Spill (m3d-1)'][:-1].values
    #    asd = dam_op_month['Volume (m3)'][1:].values \
    #         - dam_op_month['Volume (m3)'][:-1].values
    #    sadf
        
    
    
    
    
    
    
                         
    
    

    