"""
Transition Analysis Script
Analyzes state transitions and power changes
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Paths
OUTPUT_DIR = Path("../output") if Path("../output").exists() else Path("output")
DATA_PATH = OUTPUT_DIR / "reports" / "cleaned_data.csv"

def analyze_transitions(df):
    """Analyze state transitions"""
    print("=" * 60)
    print("TRANSITION ANALYSIS")
    print("=" * 60)
    
    # Find transitions
    df['StateChanged'] = df['Status'] != df['Status'].shift(1)
    transitions = df[df['StateChanged']].copy()
    transitions['PrevStatus'] = df['Status'].shift(1)
    transitions['PowerBefore'] = df['Power [W]'].shift(1)
    transitions['PowerJump'] = transitions['Power [W]'] - transitions['PowerBefore']
    
    print(f"\n✓ Found {len(transitions)} state transitions")
    
    print("\n--- All Transitions ---")
    for i, row in transitions.iterrows():
        if pd.notna(row['PrevStatus']):
            print(f"\n{transitions.index.get_loc(i)}. Time: {row['Timings']} ({row['TimeSeconds']}s)")
            print(f"   FROM: {row['PrevStatus']}")
            print(f"   TO: {row['Status']}")
            print(f"   Power: {row['PowerBefore']:.3f}W → {row['Power [W]']:.3f}W")
            print(f"   Jump: {'+' if row['PowerJump'] >= 0 else ''}{row['PowerJump']:.3f}W")
    
    # Transition statistics
    print("\n--- Transition Statistics ---")
    print(f"Average power jump: {transitions['PowerJump'].mean():.3f} W")
    print(f"Max power increase: {transitions['PowerJump'].max():.3f} W")
    print(f"Max power decrease: {transitions['PowerJump'].min():.3f} W")
    
    # Save transitions
    output_path = OUTPUT_DIR / "reports" / "transitions.csv"
    transitions_export = transitions[['Timings', 'TimeSeconds', 'PrevStatus', 'Status', 
                                      'PowerBefore', 'Power [W]', 'PowerJump']].copy()
    transitions_export.to_csv(output_path, index=False)
    print(f"\n✓ Transitions saved to: {output_path}")
    
    return transitions

if __name__ == "__main__":
    if not DATA_PATH.exists():
        print(f"Error: Run 01_data_exploration.py first!")
        sys.exit(1)
    
    df = pd.read_csv(DATA_PATH)
    transitions = analyze_transitions(df)
    
    print("\n" + "=" * 60)
    print("TRANSITION ANALYSIS COMPLETE")
    print("=" * 60)
