import streamlit as st
import pandas as pd
import logging
import os

from utils_logging import setup_logging
from utils_logging import close_log_handlers
from data_loading import data_loader
from read_yaml_files import read_yamls
## from data_filtering import filter_data
## from tabs.tab_column_summary import tab_column_summary_content
## from tabs.aggregate_summary import tab_aggregate_content
## from tabs.tab_account_stats import tab_account_stats
## from tabs.tab_about_page import tab_about
from select_filters import select_data_filters
## from chart_generator import generate_charts
## from descriptions import generate_descriptions
## from summary_generator import generate_summary

from calc_summary.calc_summary_outputs import generate_summary_outputs
from calc_entity.calc_entity_outputs import generate_entity_outputs

from tabs.tab_market_overview import generate_market_overview_tab
from tabs.tab_loans import generate_loans_tab
from tabs.tab_deposits import generate_deposits_tab
from tabs.tab_other import generate_other_tab

# Setup logging
close_log_handlers()
setup_logging()
logger = logging.getLogger(__name__)
logger.info("This is an info message from main.")

# Set page width
st.set_page_config(layout="wide")

# Create the pickle_files directory if it doesn't exist
pkl_folder_name="pickle_files"
os.makedirs(pkl_folder_name, exist_ok=True)

# Load yaml files if not already loaded
if (
    ('aliases_dict' not in st.session_state or st.session_state.aliases_dict is None) or
    ('color_discrete_map' not in st.session_state or st.session_state.color_discrete_map is None) or
    ('data_config_dict' not in st.session_state or st.session_state.data_config_dict is None) or
    ('date_column' not in st.session_state or st.session_state.date_column is None)
):
    logger.info("Reading yaml from files")

    (
        st.session_state.aliases_dict,
        st.session_state.color_discrete_map,
        st.session_state.data_config_dict,
        st.session_state.date_column
    ) = read_yamls()

else:
    logger.info("Reading yaml from session state")

# Local variable for yaml dictionaries
aliases_dict = st.session_state.aliases_dict
color_discrete_map = st.session_state.color_discrete_map
data_config_dict = st.session_state.data_config_dict
date_column = st.session_state.date_column


# Grouping Columns
company_column = data_config_dict['column_settings']['company_column'] # 'Institution Name'
group_by_columns = [date_column] + [company_column]

# Default Selections
default_company = data_config_dict['column_settings']['default_company'] # 'Macquarie Bank Limited'

# Get data
df_original, df_cleaned, df_summary = data_loader(
    pkl_folder_name=pkl_folder_name,
    data_config_dict=data_config_dict,
    date_column=date_column,
)

# Header
st.write("""
    # APRA - Monthly ADI Statistics (MADIS)
    """)
reporting_date = df_cleaned[date_column].max()
st.write(f"Reporting date: {reporting_date.strftime('%d %B %Y')}") # Present the reporting_date in the format of '30th December 2023'


# Select Data filters
st.write("# Select Data Filters")
st.write("Please make your filtering selections below:")
(
    selected_date,
    selected_company,
    top_x_value,
) = select_data_filters(
    df=df_cleaned,
    date_column=date_column,
    # group_by_columns=group_by_columns,
    company_column=company_column,
    default_company=default_company,
)


# Create summary data outputs
summary_dict = generate_summary_outputs(
    df_summary=df_summary,
    pkl_folder_name=pkl_folder_name,
    date_column=date_column,
    selected_date=selected_date,
    top_x_value=top_x_value,
    data_config_dict=data_config_dict,
)

# Create entity data outputs
entity_dict = generate_entity_outputs(
    df_cleaned=df_cleaned,
    date_column=date_column,
    selected_date=selected_date,
    company_column=company_column,
    selected_company=selected_company,
    top_x_value=top_x_value,
    pkl_folder_name=pkl_folder_name,
    data_config_dict=data_config_dict,
    color_discrete_map=color_discrete_map,
)

# Insert containers separated into tabs:
(
    tab_market,
    tab_loans,
    tab_deposits,
    tab_other,
    tab_about
) = st.tabs([
    "Market Overview",
    "Loans",
    "Deposits",
    "Other",
    "About"
])

# Market Overview Tab
with tab_market:
    generate_market_overview_tab(
        summary_dict=summary_dict,
        date_column=date_column,
        selected_date=selected_date,
    )

# Loans Tab
with tab_loans:
    generate_loans_tab(
        summary_dict=summary_dict,
        date_column=date_column,
        selected_date=selected_date,
        entity_dict=entity_dict,
        data_config_dict=data_config_dict,
    )

# Deposits Tab
with tab_deposits:
    generate_deposits_tab(
        summary_dict=summary_dict,
        date_column=date_column,
        selected_date=selected_date,
        entity_dict=entity_dict,
        data_config_dict=data_config_dict,
    )

# Other Tab
with tab_other:
    generate_other_tab(
        summary_dict=summary_dict,
        date_column=date_column,
        selected_date=selected_date,
        entity_dict=entity_dict,
        data_config_dict=data_config_dict,
    )


# Tab 3 content
with tab_about:
    st.write("Under construction.")
    ## tab_about(
    ##     dfs_dict,
    ##     file_name,
    ## )

close_log_handlers()

