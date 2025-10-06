"""
Data Exploration Script
Loads and validates the measurement data, prints basic statistics
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
DATA_DIR = Path("../data") if Path("../data").exists() else Path("data")
OUTPUT_DIR = Path("../output") if Path("../output").exists() else Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    """Load and clean the measurement data"""
    csv_path = DATA_DIR / "DVConChallengeLongTimeMeasurement_States.csv"
    
    print("=" * 60)
    print("LOADING DATA")
    print("=" * 60)
    print(f"Reading: {csv_path}")
    
    # Read CSV with correct settings
    df = pd.read_csv(csv_path, sep=';', decimal=',')
    
    print(f"✓ Loaded {len(df)} rows")
    print(f"✓ Columns: {df.columns.tolist()}")
    
    return df

def clean_data(df):
    """Clean and process the data"""
    print("\n" + "=" * 60)
    print("CLEANING DATA")
    print("=" * 60)
    
    # Convert time to seconds
    def time_to_seconds(time_str):
        try:
            h, m, s = time_str.split(':')
            return int(h) * 3600 + int(m) * 60 + int(s)
        except:
            return None
    
    df['TimeSeconds'] = df['Timings'].apply(time_to_seconds)
    
    # Remove rows with missing data
    df_clean = df[
        df['TimeSeconds'].notna() & 
        df['Status'].notna() & 
        df['Power [W]'].notna()
    ].copy()
    
    df_clean['Status'] = df_clean['Status'].str.strip()
    
    print(f"✓ Valid data points: {len(df_clean)}")
    print(f"✓ Removed {len(df) - len(df_clean)} invalid rows")
    print(f"✓ Time range: {df_clean['Timings'].iloc[0]} to {df_clean['Timings'].iloc[-1]}")
    print(f"✓ Duration: {df_clean['TimeSeconds'].iloc[-1]} seconds ({df_clean['TimeSeconds'].iloc[-1]/60:.1f} minutes)")
    
    return df_clean

def explore_data(df):
    """Print exploration statistics"""
    print("\n" + "=" * 60)
    print("DATA EXPLORATION")
    print("=" * 60)
    
    print("\n--- Unique States ---")
    states = df['Status'].unique()
    for i, state in enumerate(states, 1):
        count = len(df[df['Status'] == state])
        percentage = count / len(df) * 100
        print(f"{i}. {state}")
        print(f"   Samples: {count} ({percentage:.2f}%)")
    
    print("\n--- Power Statistics ---")
    print(f"Mean power: {df['Power [W]'].mean():.4f} W")
    print(f"Min power: {df['Power [W]'].min():.4f} W")
    print(f"Max power: {df['Power [W]'].max():.4f} W")
    print(f"Std dev: {df['Power [W]'].std():.6f} W")
    
    print("\n--- Voltage Statistics ---")
    print(f"Voltage: {df['Voltage [V]'].mean():.2f} V (constant)")
    
    # Save summary
    summary_path = OUTPUT_DIR / "reports" / "data_summary.txt"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(summary_path, 'w') as f:
        f.write("DATA SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total samples: {len(df)}\n")
        f.write(f"Duration: {df['TimeSeconds'].iloc[-1]} seconds\n")
        f.write(f"Sampling rate: 1 Hz\n")
        f.write(f"Number of states: {len(states)}\n")
        f.write(f"\nMean power: {df['Power [W]'].mean():.4f} W\n")
        f.write(f"Total energy: {df['Power [W]'].sum():.2f} J\n")
    
    print(f"\n✓ Summary saved to: {summary_path}")
    
    return df

if __name__ == "__main__":
    df = load_data()
    df_clean = clean_data(df)
    df_explored = explore_data(df_clean)
    
    # Save cleaned data
    output_path = OUTPUT_DIR / "reports" / "cleaned_data.csv"
    df_explored.to_csv(output_path, index=False)
    print(f"\n✓ Cleaned data saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("EXPLORATION COMPLETE")
    print("=" * 60)
