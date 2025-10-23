"""
Clinical Trials Analytics Dashboard

This Streamlit dashboard provides an interactive visualization of clinical trial analytics.
It displays comprehensive analysis including:
- Summary statistics and key metrics
- Site performance comparisons
- Age group analysis
- Temporal trends and patterns
- Correlation analysis
- Automated insights and recommendations

The dashboard uses the analytics module for data processing and presents results
through interactive charts, tables, and visualizations.
"""

import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy import stats
from datetime import datetime

# Import analytics functions from the analytics module
from analytics import (
    load_data, 
    calculate_summary_statistics, 
    site_performance_analysis, 
    age_group_analysis, 
    temporal_analysis, 
    correlation_analysis, 
    get_key_insights
)



# =============================================================================
# DATA LOADING AND INITIALIZATION
# =============================================================================

# Load and preprocess the clinical trial data
df = load_data()

# Calculate summary statistics for the dashboard
summary_stats = calculate_summary_statistics(df)

# =============================================================================
# DASHBOARD HEADER AND SUMMARY STATISTICS
# =============================================================================

# Set the main dashboard title
st.title("Clinical Trials Dashboard")

# Display summary statistics section
st.write("## Summary Statistics")

# Show total patient count
st.write("### Total Patients:", summary_stats['total_patients'])

# Display patients per site with both table and chart
st.write("### Patients per Site:")
patients_per_site_df = pd.DataFrame(summary_stats['patients_per_site'])
st.write(patients_per_site_df)  # Show the data table
st.bar_chart(patients_per_site_df.set_index("trial_site"))  # Show bar chart

# Display average patient age
st.write("### Average Age:", int(summary_stats['average_age']))
# =============================================================================
# VISUALIZATIONS AND CHARTS
# =============================================================================

# Create age distribution histogram with average line
fig = px.histogram(
    df,
    x="age",
    nbins=10,
    title="Age Distribution of Patients",
    color_discrete_sequence=["#636EFA"]
)
fig.update_layout(
    xaxis_title="Age",
    yaxis_title="Count",
    title_x=0.5
)
# Add vertical line showing average age
fig.add_vline(x=df["age"].mean(), line_dash="dash", line_color="red",
              annotation_text=f"Avg: {df['age'].mean():.1f}", annotation_position="top left")
st.plotly_chart(fig, use_container_width=True)

# Display completion rate statistics
st.write("### Completion Rate:", summary_stats['completion_rate'], "%")

# Create completion status pie chart
completion_count = df["completed_trial"].value_counts().reset_index()
completion_count.columns = ["Status", "Count"]
completion_count["Status"] = completion_count["Status"].map({True: "Completed", False: "Not Completed"})
completion_fig = px.pie(
    completion_count,
    names = "Status",
    values = "Count",
    title="Completion Rate",
    hole=0.4,
    color_discrete_sequence=["#008000", "#FF0000"]
)
st.plotly_chart(completion_fig)

# Display adverse event rate statistics
st.write("### Adverse Event Rate:", summary_stats['adverse_event_rate'], "%")

# Create adverse event pie chart
adverse_event_count = df["adverse_event"].value_counts().reset_index()
adverse_event_count.columns = ["Adverse Event", "Count"]
adverse_event_count["Adverse Event"] = adverse_event_count["Adverse Event"].map({False: "No", True: "Yes"})
adverse_event_fig = px.pie(
    adverse_event_count,
    names = "Adverse Event",
    values = "Count",
    title="Adverse Event Rate",
    hole=0.4,
    color_discrete_sequence=["#FF0000", "#008000"]
)
st.plotly_chart(adverse_event_fig)

# Display completion rates stratified by adverse event status
st.write("### Completion Rate (Adverse Event = True):", round(summary_stats['completion_rate_with_ae'], 2))
st.write("### Completion Rate (Adverse Event = False):", round(summary_stats['completion_rate_without_ae'], 2))

# Create comparison bar chart for completion rates with/without adverse events
completion_compare = pd.DataFrame({
    "Adverse Event": ["Yes", "No"],
    "Completion Rate (%)": [summary_stats['completion_rate_with_ae'], summary_stats['completion_rate_without_ae']]
})

fig = px.bar(
    completion_compare,
    x="Adverse Event",
    y="Completion Rate (%)",
    color="Adverse Event",
    text=completion_compare["Completion Rate (%)"].round(1).astype(str) + "%",
    title="Completion Rate: With vs Without Adverse Events",
    color_discrete_sequence=["#FF4136", "#2ECC40"]
)
fig.update_traces(textposition="outside")
fig.update_layout(showlegend=False, yaxis_range=[0, 100])
st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# ADVANCED ANALYSIS SECTION
# =============================================================================

# Add separator and section title
st.write("---")
st.title("Advanced Analysis & Insights")

# Calculate all advanced analytics metrics
site_performance = site_performance_analysis(df)
age_analysis = age_group_analysis(df)
temporal_stats = temporal_analysis(df)
correlation_matrix = correlation_analysis(df)
key_insights = get_key_insights(df)

# Convert dictionaries to DataFrames for visualization
# This is necessary because the analytics functions return dictionaries,
# but Streamlit visualizations work better with DataFrames
site_performance_df = pd.DataFrame.from_dict(site_performance, orient='index')
age_analysis_df = pd.DataFrame.from_dict(age_analysis, orient='index')
temporal_stats_df = pd.DataFrame.from_dict(temporal_stats, orient='index')
correlation_df = pd.DataFrame.from_dict(correlation_matrix, orient='index')

# =============================================================================
# SITE PERFORMANCE ANALYSIS
# =============================================================================

st.write("## Site Performance Analysis")
st.write("### Site Rankings by Completion Rate")

# Create side-by-side comparison of site performance metrics
site_fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Completion Rate by Site', 'Adverse Event Rate by Site'),
    specs=[[{"secondary_y": False}, {"secondary_y": False}]]
)

# Add completion rate bar chart (left subplot)
site_fig.add_trace(
    go.Bar(x=site_performance_df.index, y=site_performance_df['completion_rate'],
           name='Completion Rate (%)', marker_color='#2ECC40'),
    row=1, col=1
)

# Add adverse event rate bar chart (right subplot)
site_fig.add_trace(
    go.Bar(x=site_performance_df.index, y=site_performance_df['ae_rate'],
           name='Adverse Event Rate (%)', marker_color='#FF4136'),
    row=1, col=2
)

# Update layout for better presentation
site_fig.update_layout(height=400, showlegend=False, title_text="Site Performance Comparison")
site_fig.update_xaxes(title_text="Trial Site", row=1, col=1)
site_fig.update_xaxes(title_text="Trial Site", row=1, col=2)
site_fig.update_yaxes(title_text="Completion Rate (%)", row=1, col=1)
site_fig.update_yaxes(title_text="Adverse Event Rate (%)", row=1, col=2)

st.plotly_chart(site_fig, use_container_width=True)

# Display detailed site statistics table
st.write("### Detailed Site Statistics")
st.dataframe(site_performance_df)

# =============================================================================
# AGE GROUP ANALYSIS
# =============================================================================

st.write("## Age Group Analysis")
st.write("### Performance by Age Groups")

# Create side-by-side comparison of age group performance
age_fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Completion Rate by Age Group', 'Adverse Event Rate by Age Group'),
    specs=[[{"secondary_y": False}, {"secondary_y": False}]]
)

# Add completion rate bar chart for age groups (left subplot)
age_fig.add_trace(
    go.Bar(x=age_analysis_df.index, y=age_analysis_df['completion_rate'],
           name='Completion Rate (%)', marker_color='#3498DB'),
    row=1, col=1
)

# Add adverse event rate bar chart for age groups (right subplot)
age_fig.add_trace(
    go.Bar(x=age_analysis_df.index, y=age_analysis_df['ae_rate'],
           name='Adverse Event Rate (%)', marker_color='#E74C3C'),
    row=1, col=2
)

# Update layout for better presentation
age_fig.update_layout(height=400, showlegend=False, title_text="Age Group Performance Analysis")
age_fig.update_xaxes(title_text="Age Group", row=1, col=1)
age_fig.update_xaxes(title_text="Age Group", row=1, col=2)
age_fig.update_yaxes(title_text="Completion Rate (%)", row=1, col=1)
age_fig.update_yaxes(title_text="Adverse Event Rate (%)", row=1, col=2)

st.plotly_chart(age_fig, use_container_width=True)

# Display detailed age group statistics table
st.write("### Age Group Statistics")
st.dataframe(age_analysis_df)

# =============================================================================
# TEMPORAL TRENDS ANALYSIS
# =============================================================================

st.write("## Temporal Trends Analysis")
st.write("### Monthly Enrollment and Performance Trends")

# Create multi-panel temporal analysis visualization
temporal_fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Monthly Enrollments', 'Monthly Completion & Adverse Event Rates'),
    specs=[[{"secondary_y": False}], [{"secondary_y": True}]]
)

# Add monthly enrollment bar chart (top panel)
temporal_fig.add_trace(
    go.Bar(x=temporal_stats_df.index, y=temporal_stats_df['enrollments'],
           name='Enrollments', marker_color='#9B59B6'),
    row=1, col=1
)

# Add monthly completion rate line chart (bottom panel, left y-axis)
temporal_fig.add_trace(
    go.Scatter(x=temporal_stats_df.index, y=temporal_stats_df['completion_rate'],
               mode='lines+markers', name='Completion Rate (%)', line=dict(color='#2ECC40')),
    row=2, col=1
)

# Add monthly adverse event rate line chart (bottom panel, right y-axis)
temporal_fig.add_trace(
    go.Scatter(x=temporal_stats_df.index, y=temporal_stats_df['ae_rate'],
               mode='lines+markers', name='Adverse Event Rate (%)', line=dict(color='#E74C3C')),
    row=2, col=1, secondary_y=True
)

# Update layout for better presentation
temporal_fig.update_layout(height=600, title_text="Temporal Analysis")
temporal_fig.update_xaxes(title_text="Month", row=2, col=1)
temporal_fig.update_yaxes(title_text="Number of Enrollments", row=1, col=1)
temporal_fig.update_yaxes(title_text="Completion Rate (%)", row=2, col=1)
temporal_fig.update_yaxes(title_text="Adverse Event Rate (%)", row=2, col=1, secondary_y=True)

st.plotly_chart(temporal_fig, use_container_width=True)

# =============================================================================
# CORRELATION ANALYSIS
# =============================================================================

st.write("## Correlation Analysis")
st.write("### Variable Relationships Heatmap")

# Create correlation matrix heatmap showing relationships between all variables
corr_fig = px.imshow(correlation_df, 
                     text_auto=True, 
                     aspect="auto",
                     color_continuous_scale='RdBu_r',
                     title="Correlation Matrix: Variable Relationships")

st.plotly_chart(corr_fig, use_container_width=True)



