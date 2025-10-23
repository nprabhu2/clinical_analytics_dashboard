"""
Clinical Trials Analytics

This module contains all the core analytics functions for analyzing clinical trial data.
It provides functions to load, process, and analyze clinical trial data including:
- Summary statistics
- Site performance analysis
- Age group analysis
- Temporal trends
- Correlation analysis
- Key insights generation

All functions return structured data (dictionaries) that can be consumed by both
the REST API and Streamlit dashboard.
"""

import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
import logging
import os
from typing import Dict, List, Tuple, Optional


def load_data(file_path="data/clinical_trials.csv"):
    """
    Load and preprocess clinical trial data from CSV file with simple error handling.
    
    Args:
        file_path (str): Path to the CSV file to load. Defaults to "data/clinical_trials.csv"
    
    This function:
    1. Reads the clinical trials CSV file
    2. Handles null values and missing data gracefully
    3. Drops rows and columns with missing data
    4. Converts enrollment_date to datetime format
    5. Creates age groups for analysis (18-30, 31-50, 51-70, 71-80)
    6. Extracts enrollment month for temporal analysis
    
    Returns:
        pd.DataFrame: Preprocessed clinical trial data with additional columns
    """
    try:
        # Read the clinical trials data from CSV
        df = pd.read_csv(file_path)
        
        # Simple error handling: drop rows and columns with missing data
        original_rows = len(df)
        original_cols = len(df.columns)
        
        # Handle various null representations (None, NaN, "Null", "null", empty strings)
        df = df.replace(['Null', 'null', 'NULL', '', ' '], pd.NA)
        
        # Drop columns that are completely empty
        df = df.dropna(axis=1, how='all')
        
        # Drop rows that have any missing data
        df = df.dropna(axis=0, how='any')
        
        # Log data cleaning results
        if len(df) < original_rows or len(df.columns) < original_cols:
            print(f"Data cleaning: {original_rows} rows -> {len(df)} rows, {original_cols} columns -> {len(df.columns)} columns")
        
        # Convert enrollment_date from string to datetime for proper date handling
        # Use errors='coerce' to handle any remaining invalid dates gracefully
        df['enrollment_date'] = pd.to_datetime(df['enrollment_date'], errors='coerce')
        
        # Convert age to numeric, handling any remaining string values
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        
        # Convert boolean columns, handling various representations
        df['adverse_event'] = df['adverse_event'].astype(str).str.lower().str.strip()
        df['adverse_event'] = df['adverse_event'].isin(['true', '1', 'yes'])
        
        df['completed_trial'] = df['completed_trial'].astype(str).str.lower().str.strip()
        df['completed_trial'] = df['completed_trial'].isin(['true', '1', 'yes'])
        
        # Drop any rows where date or age conversion failed
        df = df.dropna(subset=['enrollment_date', 'age'])
        
        # Create age groups using pandas cut function for categorical analysis
        # Bins: 0-30, 31-50, 51-70, 71-80 (labels correspond to age ranges)
        df['age_group'] = pd.cut(df['age'], bins=[0, 30, 50, 70, 100], labels=['18-30', '31-50', '51-70', '71-80'])
        
        # Extract enrollment month for temporal trend analysis
        df['enrollment_month'] = df['enrollment_date'].dt.month
        
        return df
        
    except Exception as e:
        print(f"Error loading CSV data: {str(e)}")
        raise


def calculate_summary_statistics(df):
    """
    Calculate basic summary statistics for the clinical trial data.
    
    This function computes key metrics including:
    - Total patient count
    - Patient distribution across trial sites
    - Average patient age
    - Overall completion and adverse event rates
    - Completion rates stratified by adverse event status
    
    Args:
        df (pd.DataFrame): Preprocessed clinical trial data
        
    Returns:
        dict: Dictionary containing all summary statistics with rounded values
    """
    # 1. Total number of patients enrolled in the trial
    total_patients = len(df)
    
    # 2. Count patients per trial site for site distribution analysis
    patients_per_site = (df.groupby("trial_site")["patient_id"].count().reset_index(name="patient_count"))
    
    # 3. Calculate average age of all patients
    average_age = df["age"].mean()
    
    # 4. Calculate overall trial completion rate (percentage)
    completion_rate = df["completed_trial"].mean() * 100
    
    # 5. Calculate overall adverse event rate (percentage)
    adverse_event_rate = df["adverse_event"].mean() * 100
    
    # 6. Calculate completion rate for patients who experienced adverse events
    # This helps understand if adverse events impact trial completion
    completion_rate_with_ae = df[df["adverse_event"] == True]["completed_trial"].mean() * 100
    
    # 7. Calculate completion rate for patients who did NOT experience adverse events
    # This provides a baseline for comparison
    completion_rate_without_ae = df[df["adverse_event"] == False]["completed_trial"].mean() * 100
    
    # Return structured dictionary with all statistics
    return {
        'total_patients': int(total_patients),
        'patients_per_site': patients_per_site.to_dict('records'),  # Convert to list of dicts for JSON serialization
        'average_age': round(average_age, 1),
        'completion_rate': round(completion_rate, 1),
        'adverse_event_rate': round(adverse_event_rate, 1),
        'completion_rate_with_ae': round(completion_rate_with_ae, 1),
        'completion_rate_without_ae': round(completion_rate_without_ae, 1)
    }


def site_performance_analysis(df):
    """
    Perform advanced site performance analysis comparing all trial sites.
    
    This function analyzes each trial site's performance by calculating:
    - Total number of patients enrolled
    - Completion rates and counts
    - Adverse event rates and counts
    - Average patient age
    - Sites are ranked by completion rate (highest to lowest)
    
    Args:
        df (pd.DataFrame): Preprocessed clinical trial data
        
    Returns:
        dict: Dictionary with site names as keys and performance metrics as values
    """
    # Group data by trial site and calculate multiple aggregations
    site_stats = df.groupby('trial_site').agg({
        'patient_id': 'count',           # Count total patients per site
        'completed_trial': ['sum', 'mean'],  # Sum and mean of completions
        'adverse_event': ['sum', 'mean'],    # Sum and mean of adverse events
        'age': 'mean'                    # Average age per site
    }).round(3)
    
    # Flatten column names for easier access
    site_stats.columns = ['total_patients', 'completed_count', 'completion_rate', 'ae_count', 'ae_rate', 'avg_age']
    
    # Convert rates to percentages for better readability
    site_stats['completion_rate'] = site_stats['completion_rate'] * 100
    site_stats['ae_rate'] = site_stats['ae_rate'] * 100
    
    # Sort sites by completion rate (best performing first)
    site_stats = site_stats.sort_values('completion_rate', ascending=False)
    
    # Convert to dictionary format for JSON serialization
    return site_stats.to_dict('index')


def age_group_analysis(df):
    """
    Perform detailed analysis of clinical trial outcomes by age groups.
    
    This function analyzes how different age groups perform in the trial by calculating:
    - Patient count per age group
    - Completion rates by age group
    - Adverse event rates by age group
    - Age statistics (min, max, average) for each group
    
    Age groups: 18-30, 31-50, 51-70, 71-80
    
    Args:
        df (pd.DataFrame): Preprocessed clinical trial data with age_group column
        
    Returns:
        dict: Dictionary with age groups as keys and performance metrics as values
    """
    # Group data by age group and calculate multiple aggregations
    age_analysis = df.groupby('age_group').agg({
        'patient_id': 'count',           # Count patients in each age group
        'completed_trial': 'mean',       # Completion rate per age group
        'adverse_event': 'mean',         # Adverse event rate per age group
        'age': ['min', 'max', 'mean']    # Age statistics for each group
    }).round(3)
    
    # Flatten column names for easier access
    age_analysis.columns = ['count', 'completion_rate', 'ae_rate', 'min_age', 'max_age', 'avg_age']
    
    # Convert rates to percentages for better readability
    age_analysis['completion_rate'] = age_analysis['completion_rate'] * 100
    age_analysis['ae_rate'] = age_analysis['ae_rate'] * 100
    
    # Convert to dictionary format for JSON serialization
    return age_analysis.to_dict('index')


def temporal_analysis(df):
    """
    Analyze temporal trends in clinical trial enrollment and outcomes.
    
    This function examines how trial metrics change over time by analyzing:
    - Monthly enrollment patterns
    - Completion rates by enrollment month
    - Adverse event rates by enrollment month
    
    This helps identify seasonal patterns, enrollment trends, and whether
    enrollment timing affects trial outcomes.
    
    Args:
        df (pd.DataFrame): Preprocessed clinical trial data with enrollment_month column
        
    Returns:
        dict: Dictionary with months as keys and temporal metrics as values
    """
    # Group data by enrollment month and calculate aggregations
    monthly_stats = df.groupby('enrollment_month').agg({
        'patient_id': 'count',           # Count enrollments per month
        'completed_trial': 'mean',       # Completion rate per month
        'adverse_event': 'mean'          # Adverse event rate per month
    }).round(3)
    
    # Rename columns for clarity
    monthly_stats.columns = ['enrollments', 'completion_rate', 'ae_rate']
    
    # Convert rates to percentages for better readability
    monthly_stats['completion_rate'] = monthly_stats['completion_rate'] * 100
    monthly_stats['ae_rate'] = monthly_stats['ae_rate'] * 100
    
    # Convert to dictionary format for JSON serialization
    return monthly_stats.to_dict('index')


def correlation_analysis(df):
    """
    Perform correlation analysis between all variables in the clinical trial data.
    
    This function calculates correlations between:
    - Patient age
    - Trial completion status
    - Adverse event occurrence
    - Enrollment month
    - Trial site (using dummy variables)
    
    The analysis helps identify relationships and dependencies between variables,
    which can inform trial design and patient management strategies.
    
    Args:
        df (pd.DataFrame): Preprocessed clinical trial data
        
    Returns:
        dict: Correlation matrix as a nested dictionary
    """
    # Create a copy of the data for correlation analysis
    corr_data = df.copy()
    
    # Convert boolean columns to integers for correlation calculation
    corr_data['completed_trial'] = corr_data['completed_trial'].astype(int)
    corr_data['adverse_event'] = corr_data['adverse_event'].astype(int)
    
    # Ensure enrollment month is available for correlation
    corr_data['enrollment_month'] = corr_data['enrollment_date'].dt.month
    
    # Create dummy variables for trial sites (one-hot encoding)
    # This allows us to include categorical site data in correlation analysis
    site_dummies = pd.get_dummies(corr_data['trial_site'], prefix='site')
    corr_data = pd.concat([corr_data, site_dummies], axis=1)
    
    # Select only numeric columns for correlation analysis
    numeric_cols = ['age', 'completed_trial', 'adverse_event', 'enrollment_month'] + list(site_dummies.columns)
    correlation_matrix = corr_data[numeric_cols].corr()
    
    # Convert correlation matrix to dictionary for JSON serialization
    return correlation_matrix.to_dict()


def get_key_insights(df):
    """
    Generate key insights and actionable recommendations from the clinical trial data.
    
    This function analyzes the data to identify:
    - Best and worst performing trial sites
    - Best and worst performing age groups
    - Provides actionable recommendations based on the analysis
    
    Args:
        df (pd.DataFrame): Preprocessed clinical trial data
        
    Returns:
        dict: Dictionary containing insights and recommendations
    """
    # Get site and age group performance data
    site_performance = site_performance_analysis(df)
    age_analysis = age_group_analysis(df)
    
    # Convert dictionaries back to DataFrames for easier calculations
    site_df = pd.DataFrame.from_dict(site_performance, orient='index')
    age_df = pd.DataFrame.from_dict(age_analysis, orient='index')
    
    # Identify best and worst performing sites (sites are already sorted by completion rate)
    best_site = site_df.index[0]      # First site (highest completion rate)
    worst_site = site_df.index[-1]    # Last site (lowest completion rate)
    
    # Identify best and worst performing age groups
    best_age_group = age_df.loc[age_df['completion_rate'].idxmax()].name
    worst_age_group = age_df.loc[age_df['completion_rate'].idxmin()].name
    
    # Compile insights and recommendations
    return {
        'best_site': {
            'name': best_site,
            'completion_rate': round(site_df.loc[best_site, 'completion_rate'], 1),
            'ae_rate': round(site_df.loc[best_site, 'ae_rate'], 1)
        },
        'worst_site': {
            'name': worst_site,
            'completion_rate': round(site_df.loc[worst_site, 'completion_rate'], 1),
            'ae_rate': round(site_df.loc[worst_site, 'ae_rate'], 1)
        },
        'best_age_group': {
            'name': best_age_group,
            'completion_rate': round(age_df.loc[best_age_group, 'completion_rate'], 1)
        },
        'worst_age_group': {
            'name': worst_age_group,
            'completion_rate': round(age_df.loc[worst_age_group, 'completion_rate'], 1)
        },
        'recommendations': [
            "Investigate why certain sites have lower completion rates",
            "Focus support on underperforming age groups",
            "Monitor temporal trends for seasonal patterns",
            "Analyze correlations to identify key success factors"
        ]
    }


def get_all_analytics():
    """
    Get all analytics in a single function call for comprehensive analysis.
    
    This is a convenience function that runs all analytics functions and returns
    a complete analysis package. Useful for API endpoints that need all data
    or for generating comprehensive reports.
    
    Returns:
        dict: Dictionary containing all analytics results:
            - summary_statistics: Basic trial metrics
            - site_performance: Site comparison analysis
            - age_group_analysis: Age group performance
            - temporal_analysis: Time-based trends
            - correlation_analysis: Variable relationships
            - key_insights: Automated insights and recommendations
    """
    # Load and preprocess the data once
    df = load_data()
    
    # Run all analytics functions and compile results
    return {
        'summary_statistics': calculate_summary_statistics(df),
        'site_performance': site_performance_analysis(df),
        'age_group_analysis': age_group_analysis(df),
        'temporal_analysis': temporal_analysis(df),
        'correlation_analysis': correlation_analysis(df),
        'key_insights': get_key_insights(df)
    }
