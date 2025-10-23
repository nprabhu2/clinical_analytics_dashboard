"""
Clinical Trial Data Generator

This script generates synthetic clinical trial data for analysis and testing purposes.
It creates realistic patient data including:
- Patient IDs, trial sites, enrollment dates
- Patient ages, adverse event status, trial completion status

The data is generated with controlled randomness using seeds for reproducibility.
"""

from faker import Faker
import random
import csv
import os
from datetime import datetime, timedelta

# Initialize Faker for generating realistic data
fake = Faker()

# Set seeds for reproducible data generation
random.seed(42)
Faker.seed(42)

# Configuration parameters
n_records = 40  # Number of patient records to generate
output_file = "data/clinical_trials.csv"  # Output file path

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Define trial sites for the clinical trial
trial_sites = ["Boston", "Chicago", "New York", "San Francisco", "Dallas"]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def random_date(start_date, end_date):
    """
    Generate a random date between start_date and end_date.
    
    Args:
        start_date (datetime): Start date for enrollment period
        end_date (datetime): End date for enrollment period
        
    Returns:
        datetime: Random date within the specified range
    """
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# =============================================================================
# DATA GENERATION CONFIGURATION
# =============================================================================

# Define enrollment period for the clinical trial
start_date = datetime(2024, 1, 1)  # Trial start date
end_date = datetime(2024, 6, 30)   # Trial end date

# =============================================================================
# DATA GENERATION AND CSV CREATION
# =============================================================================

# Create CSV file with clinical trial data
with open(output_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    
    # Write CSV header row
    writer.writerow([
        "patient_id", "trial_site", "enrollment_date",
        "age", "adverse_event", "completed_trial"
    ])

    # Generate patient records
    for i in range(1, n_records + 1):
        # Generate patient ID with zero-padding (P001, P002, etc.)
        patient_id = f"P{i:03d}"
        
        # Randomly assign trial site
        trial_site = random.choice(trial_sites)
        
        # Generate random enrollment date within the trial period
        enrollment_date = random_date(start_date, end_date).strftime("%Y-%m-%d")
        
        # Generate patient age (18-80 years old)
        age = random.randint(18, 80)

        # Generate adverse event status (approximately 30% of patients)
        adverse_event = random.random() < 0.3

        # Generate completion status with realistic probabilities
        # Patients with adverse events have lower completion rates
        if adverse_event:
            completed_trial = random.random() < 0.7  # 70% completion if adverse event
        else:
            completed_trial = random.random() < 0.9  # 90% completion otherwise

        # Write patient record to CSV
        writer.writerow([
            patient_id, trial_site, enrollment_date,
            age, str(adverse_event).lower(), str(completed_trial).lower()
        ])

# =============================================================================
# COMPLETION MESSAGE
# =============================================================================

print(f"✅ CSV file '{output_file}' created successfully with {n_records} records.")