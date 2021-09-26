# # Patient Online - Geographic Analysis
# #### Developed by: Mary Amanuel
# #### Contact: mary.amanuel@nhsx.nhs.uk
# #### Last Updated: 25th September 2021

import pandas as pd
import os
import plotly
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as pyo
import numpy as np
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
nhs_colours = ['#00A499', '#FFB81C', '#7C2855']

# ### Patient Online  - August 2021 Data 

POMI = pd.read_csv('data/POMI 2017_2021/POMI_APR2021_to_AUG2021.csv', sep = ',')
POMI


POMI['report_period_end'] = pd.to_datetime(POMI['report_period_end'])
POMI['ccg_name'] = POMI['ccg_name'].replace(['NHS Herefordshire CCG'],'NHS Herefordshire and Worcestershire CCG')
POMI['ccg_name'] = POMI['ccg_name'].replace(['NHS Herts Valley CCG'],'NHS Herts Valleys CCG')
POMI['ccg_name'] = POMI['ccg_name'].str.upper()
POMI['practice_name'] = POMI['practice_name'].str.upper()


POMI_pivot =  pd.pivot_table(POMI, index = ['report_period_end', 'ccg_name', 'practice_name', 'region_code', ], columns = 'field', values = 'value')


POMI_filter = POMI_pivot.drop(['New_Pat_Enbld','Pat_Appts_Enbld', 'Pat_DetCodeRec_Enbld','Pat_DetCodeRec_Use','Pat_Presc_Enbld','Sys_Appts_Enbld','Sys_DetCodeRec_Enbld','Sys_Presc_Enbld','Total_Pat_Enbld'], axis=1)
POMI_filter = POMI_filter.reset_index()
POMI_filter

patient_list_size_check = POMI_filter[['report_period_end','patient_list_size']].groupby('report_period_end').sum()
patient_list_size_check 

POMI_filter.report_period_end = POMI_filter.report_period_end.astype(str)
POMI_filter.dtypes

POMI_august_2021 = POMI_filter[POMI_filter['report_period_end'] == '2021-08-31']
POMI_august_2021

POMI_august_2021_cgg = POMI_august_2021[['ccg_name', 'region_code', 'Pat_Appts_Use', 'Pat_Presc_Use', 'patient_list_size']].groupby('ccg_name').sum()
POMI_august_2021_cgg.reset_index()

patient_list_size_check_ccg = POMI_august_2021[['ccg_name','patient_list_size']].groupby('ccg_name').sum()
patient_list_size_check_ccg

POMI_august_2021_cgg['Pat_Presc_Use_per_10000'] = (POMI_august_2021_cgg['Pat_Presc_Use'] / POMI_august_2021_cgg['patient_list_size']) * 10000
POMI_august_2021_cgg['Pat_Appts_Use_per_10000'] = (POMI_august_2021_cgg['Pat_Appts_Use'] / POMI_august_2021_cgg['patient_list_size']) * 10000
POMI_final = POMI_august_2021_cgg.round(2)
POMI_final


# ### Merging CCG CODES / ONS CODES

CCG_APRIL_2021_CODES_ONS = pd.read_csv('data/POMI 2017_2021/Clinical_Commissioning_Groups_(April_2021)_Names_and_Codes_in_England.csv', sep = ',')
CCG_APRIL_2021_CODES_ONS 

CCG_APRIL_2021_CODES_ONS['CCG21NM']= CCG_APRIL_2021_CODES_ONS['CCG21NM'].str.upper()
CCG_APRIL_2021_CODES_ONS

CCG_codes = CCG_APRIL_2021_CODES_ONS.merge(POMI_final, left_on='CCG21NM', right_on ='ccg_name')
data_set_data_wrapper_mapping = CCG_codes.rename(columns={'CCG21NM': 'Name'})
CCG_code_results = data_set_data_wrapper_mapping.sort_values(by='Name', ascending=True)
CCG_code_results

CCG_code_results.to_csv('POMI_CCG_Results_August_2021.csv')

# ### Regional Bar Charts

POMI_august_2021_region = POMI_august_2021[['ccg_name', 'region_code', 'Pat_Appts_Use', 'Pat_Presc_Use', 'patient_list_size']].groupby('region_code').sum()
POMI_august_2021_region.reset_index()

patient_list_size_check_region = POMI_august_2021_region['patient_list_size'].sum()
patient_list_size_check_region 

POMI_august_2021_region['Pat_Presc_Use_per_10000'] = (POMI_august_2021_region['Pat_Presc_Use'] / POMI_august_2021_region['patient_list_size']) * 10000
POMI_august_2021_region['Pat_Appts_Use_per_10000'] = (POMI_august_2021_region['Pat_Appts_Use'] / POMI_august_2021_region['patient_list_size']) * 10000
POMI_region = POMI_august_2021_region.round(2)
region_name = {'Y56': 'London', 'Y58': 'South West', 'Y59': 'South East', 'Y60': 'Midlands', 'Y61': 'East of England', 'Y61': 'East of England', 'Y62': 'North West', 'Y63': 'North East and Yorkshire'}
POMI_region_code_names = POMI_region.reset_index()

POMI_region_code_names['region_name'] = POMI_region_code_names['region_code'].map(region_name)
Region_code_results_presc = POMI_region_code_names.sort_values(by='Pat_Presc_Use_per_10000', ascending=False)
Region_code_results_presc

data0 = go.Bar(
    x = Region_code_results_presc.region_name,
    y = Region_code_results_presc.Pat_Presc_Use_per_10000)

figure = go.Figure(data = data0)
figure.show()

# Write chart to file (.html)
config = {"displayModeBar": False, "displaylogo": False}
plotly_obj = plotly.offline.plot(
    fig, include_plotlyjs=False, output_type="div", config=config
)
with open("_includes/prescriptions.html", "w") as file:
    file.write(plotly_obj)

POMI_region_code_names['region_name'] = POMI_region_code_names['region_code'].map(region_name)
Region_code_results_appts= POMI_region_code_names.sort_values(by='Pat_Appts_Use_per_10000', ascending=False)

data1 = go.Bar(
    x = Region_code_results_appts.region_name,
    y = Region_code_results_appts.Pat_Appts_Use_per_10000)

figure = go.Figure(data = data1)
figure.show()

# Write chart to file (.html)
config = {"displayModeBar": False, "displaylogo": False}
plotly_obj = plotly.offline.plot(
    fig, include_plotlyjs=False, output_type="div", config=config
)
with open("_includes/appointments.html", "w") as file:
    file.write(plotly_obj)

Region_code_results_appts.to_csv('Region_code_results_appts_August_2021.csv')

