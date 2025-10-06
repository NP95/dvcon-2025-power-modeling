"""
State Characterization Script
Analyzes power consumption for each state and generates characterization table
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Paths
OUTPUT_DIR = Path("../output") if Path("../output").exists() else Path("output")
DATA_PATH = OUTPUT_DIR / "reports" / "cleaned_data.csv"

def characterize_states(df):
    """Characterize power consumption for each state"""
    print("=" * 60)
    print("STATE CHARACTERIZATION")
    print("=" * 60)
    
    # Group by status
    state_stats = df.groupby('Status').agg({
        'Power [W]': ['count', 'mean', 'std', 'min', 'max'],
        'TimeSeconds': 'count'
    }).round(6)
    
    state_stats.columns = ['Count', 'Avg_Power_W', 'Std_Dev', 'Min_Power_W', 'Max_Power_W', 'Duration_s']
    state_stats = state_stats.sort_values('Count', ascending=False)
    
    # Calculate percentages and energy
    total_samples = len(df)
    state_stats['Percentage'] = (state_stats['Count'] / total_samples * 100).round(2)
    state_stats['Energy_J'] = (state_stats['Avg_Power_W'] * state_stats['Count']).round(2)
    state_stats['CV_percent'] = ((state_stats['Std_Dev'] / state_stats['Avg_Power_W']) * 100).round(3)
    
    print("\n--- Power Characterization Table ---")
    print(state_stats.to_string())
    
    # Save to CSV
    output_path = OUTPUT_DIR / "reports" / "state_characterization.csv"
    state_stats.to_csv(output_path)
    print(f"\n✓ Characterization saved to: {output_path}")
    
    # Create SystemC code snippet
    print("\n--- SystemC Implementation ---")
    print("\ndouble getPowerForState(int state) {")
    print("    switch(state) {")
    for i, (state_name, row) in enumerate(state_stats.iterrows()):
        power = row['Avg_Power_W']
        comment = f"// {state_name[:30]}"
        if len(state_name) > 30:
            comment += "..."
        print(f"        case {i}: return {power:.4f};  {comment}")
    print("        default: return 1.0;")
    print("    }")
    print("}")
    
    # Save code snippet
    code_path = OUTPUT_DIR / "reports" / "getPowerForState.cpp"
    with open(code_path, 'w') as f:
        f.write("double getPowerForState(int state) {\n")
        f.write("    switch(state) {\n")
        for i, (state_name, row) in enumerate(state_stats.iterrows()):
            power = row['Avg_Power_W']
            f.write(f"        case {i}: return {power:.4f};  // {state_name}\n")
        f.write("        default: return 1.0;\n")
        f.write("    }\n")
        f.write("}\n")
    
    print(f"\n✓ Code snippet saved to: {code_path}")
    
    return state_stats

if __name__ == "__main__":
    if not DATA_PATH.exists():
        print(f"Error: Run 01_data_exploration.py first!")
        sys.exit(1)
    
    df = pd.read_csv(DATA_PATH)
    state_stats = characterize_states(df)
    
    print("\n" + "=" * 60)
    print("CHARACTERIZATION COMPLETE")
    print("=" * 60)
