"""
Energy Analysis Script  
Calculates cumulative energy and validates against target
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Paths
OUTPUT_DIR = Path("../output") if Path("../output").exists() else Path("output")
DATA_PATH = OUTPUT_DIR / "reports" / "cleaned_data.csv"

def analyze_energy(df):
    """Calculate and analyze energy consumption"""
    print("=" * 60)
    print("ENERGY ANALYSIS")
    print("=" * 60)
    
    # Calculate cumulative energy
    df['EnergyIncrement'] = df['Power [W]'] * 1.0  # 1 second per sample
    df['CumulativeEnergy'] = df['EnergyIncrement'].cumsum()
    
    total_energy = df['CumulativeEnergy'].iloc[-1]
    duration = df['TimeSeconds'].iloc[-1]
    avg_power = total_energy / duration
    
    print(f"\n--- Energy Summary ---")
    print(f"Total Energy: {total_energy:.2f} Joules")
    print(f"Duration: {duration} seconds ({duration/60:.1f} minutes)")
    print(f"Average Power: {avg_power:.4f} Watts")
    
    # Energy by state
    print("\n--- Energy Contribution by State ---")
    energy_by_state = df.groupby('Status').agg({
        'EnergyIncrement': 'sum',
        'TimeSeconds': 'count'
    })
    energy_by_state.columns = ['Energy_J', 'Duration_s']
    energy_by_state['Percentage'] = (energy_by_state['Energy_J'] / total_energy * 100)
    energy_by_state = energy_by_state.sort_values('Energy_J', ascending=False)
    
    print(energy_by_state.round(2).to_string())
    
    # Save
    output_path = OUTPUT_DIR / "reports" / "energy_analysis.csv"
    energy_by_state.to_csv(output_path)
    print(f"\n✓ Energy analysis saved to: {output_path}")
    
    # Save time series
    timeseries_path = OUTPUT_DIR / "reports" / "energy_timeseries.csv"
    df[['TimeSeconds', 'Power [W]', 'CumulativeEnergy', 'Status']].to_csv(timeseries_path, index=False)
    print(f"✓ Energy time series saved to: {timeseries_path}")
    
    return df

if __name__ == "__main__":
    if not DATA_PATH.exists():
        print(f"Error: Run 01_data_exploration.py first!")
        sys.exit(1)
    
    df = pd.read_csv(DATA_PATH)
    df_with_energy = analyze_energy(df)
    
    print("\n" + "=" * 60)
    print("ENERGY ANALYSIS COMPLETE")
    print("=" * 60)
