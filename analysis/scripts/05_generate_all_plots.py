"""
Complete Plotting Script
Generates all analysis plots with full-resolution data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Paths
OUTPUT_DIR = Path("../output") if Path("../output").exists() else Path("output")
PLOTS_DIR = OUTPUT_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

def load_all_data():
    """Load all processed data"""
    df = pd.read_csv(OUTPUT_DIR / "reports" / "cleaned_data.csv")
    energy_ts = pd.read_csv(OUTPUT_DIR / "reports" / "energy_timeseries.csv")
    state_char = pd.read_csv(OUTPUT_DIR / "reports" / "state_characterization.csv", index_col=0)
    transitions = pd.read_csv(OUTPUT_DIR / "reports" / "transitions.csv")
    
    return df, energy_ts, state_char, transitions

def plot_power_timeline(df, transitions):
    """Plot 1: Power consumption over time"""
    print("Generating Plot 1: Power Timeline...")
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(df['TimeSeconds'], df['Power [W]'], 
            linewidth=0.8, color='#3498db', alpha=0.7)
    
    # Mark transitions
    for _, t in transitions.iterrows():
        if pd.notna(t['TimeSeconds']):
            ax.axvline(x=t['TimeSeconds'], color='red', alpha=0.3, 
                      linestyle='--', linewidth=0.8)
    
    ax.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Power (Watts)', fontsize=12, fontweight='bold')
    ax.set_title('Power Consumption Over Time', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.9, 1.4)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / '01_power_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 01_power_timeline.png")

def plot_cumulative_energy(energy_ts):
    """Plot 2: Cumulative energy"""
    print("Generating Plot 2: Cumulative Energy...")
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(energy_ts['TimeSeconds'], energy_ts['CumulativeEnergy'], 
            linewidth=2, color='#27ae60')
    ax.fill_between(energy_ts['TimeSeconds'], energy_ts['CumulativeEnergy'], 
                     alpha=0.3, color='#27ae60')
    
    ax.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cumulative Energy (Joules)', fontsize=12, fontweight='bold')
    ax.set_title('Total Energy Consumption Over Time', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add final value annotation
    final_energy = energy_ts['CumulativeEnergy'].iloc[-1]
    ax.text(0.95, 0.05, f'Final: {final_energy:.2f} J', 
            transform=ax.transAxes, fontsize=12, 
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / '02_cumulative_energy.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 02_cumulative_energy.png")

def plot_time_distribution(state_char):
    """Plot 3: Time distribution pie chart"""
    print("Generating Plot 3: Time Distribution...")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c']
    
    ax.pie(state_char['Percentage'], labels=state_char.index, autopct='%1.1f%%',
           startangle=90, colors=colors, textprops={'fontsize': 10})
    ax.set_title('Time Distribution by State', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / '03_time_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 03_time_distribution.png")

def plot_state_power_comparison(state_char):
    """Plot 4: Power comparison bar chart"""
    print("Generating Plot 4: State Power Comparison...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c']
    
    bars = ax.bar(range(len(state_char)), state_char['Avg_Power_W'], 
                  color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add error bars
    ax.errorbar(range(len(state_char)), state_char['Avg_Power_W'],
                yerr=[state_char['Avg_Power_W'] - state_char['Min_Power_W'],
                      state_char['Max_Power_W'] - state_char['Avg_Power_W']],
                fmt='none', ecolor='black', capsize=5, alpha=0.5)
    
    ax.set_xlabel('System State', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Power (Watts)', fontsize=12, fontweight='bold')
    ax.set_title('Average Power Consumption by State', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(state_char)))
    ax.set_xticklabels(state_char.index, rotation=45, ha='right', fontsize=9)
    ax.set_ylim(0.9, 1.2)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / '04_state_power_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 04_state_power_comparison.png")

def plot_transition_power_jumps(transitions):
    """Plot 5: Power jumps at transitions"""
    print("Generating Plot 5: Transition Power Jumps...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#e74c3c' if x >= 0 else '#27ae60' for x in transitions['PowerJump']]
    
    bars = ax.bar(range(len(transitions)), transitions['PowerJump'], 
                  color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_xlabel('Transition Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Power Change (Watts)', fontsize=12, fontweight='bold')
    ax.set_title('Power Jumps at State Transitions', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(transitions)))
    ax.set_xticklabels([f'T{i+1}' for i in range(len(transitions))])
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / '05_transition_power_jumps.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 05_transition_power_jumps.png")

def plot_bluetooth_comparison(df):
    """Plot 6: Bluetooth vs non-Bluetooth comparison"""
    print("Generating Plot 6: Bluetooth Comparison...")
    
    bt_data = df[df['Status'].str.contains('Bluetooth', case=False, na=False)]
    non_bt_data = df[~df['Status'].str.contains('Bluetooth', case=False, na=False)]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data = [non_bt_data['Power [W]'].mean(), bt_data['Power [W]'].mean()]
    labels = ['Non-Bluetooth\nStates', 'Bluetooth\nActive States']
    colors = ['#3498db', '#e74c3c']
    
    bars = ax.bar(labels, data, color=colors, alpha=0.7, 
                  edgecolor='black', linewidth=2)
    
    # Add value labels
    for bar, value in zip(bars, data):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.4f} W',
                ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    ax.set_ylabel('Average Power (Watts)', fontsize=12, fontweight='bold')
    ax.set_title('Power Comparison: Bluetooth vs Non-Bluetooth', 
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0.9, 1.2)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add overhead annotation
    overhead = ((data[1] - data[0]) / data[0]) * 100
    ax.text(0.5, 0.95, f'BT Overhead: +{overhead:.2f}%',
            transform=ax.transAxes, fontsize=12,
            ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / '06_bluetooth_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 06_bluetooth_comparison.png")

def plot_energy_contribution(state_char):
    """Plot 7: Energy contribution by state"""
    print("Generating Plot 7: Energy Contribution...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c']
    
    bars = ax.bar(range(len(state_char)), state_char['Energy_J'], 
                  color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('System State', fontsize=12, fontweight='bold')
    ax.set_ylabel('Energy Consumed (Joules)', fontsize=12, fontweight='bold')
    ax.set_title('Total Energy Contribution by State', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(state_char)))
    ax.set_xticklabels(state_char.index, rotation=45, ha='right', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / '07_energy_contribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 07_energy_contribution.png")

def plot_power_histogram(df):
    """Plot 8: Power distribution histogram for main state"""
    print("Generating Plot 8: Power Distribution Histogram...")
    
    # Get main state (most common)
    main_state = df['Status'].value_counts().index[0]
    main_state_data = df[df['Status'] == main_state]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    n, bins, patches = ax.hist(main_state_data['Power [W]'], bins=30, 
                                color='#3498db', alpha=0.7, edgecolor='black')
    
    # Add mean and median lines
    mean_val = main_state_data['Power [W]'].mean()
    median_val = main_state_data['Power [W]'].median()
    
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.4f}W')
    ax.axvline(median_val, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_val:.4f}W')
    
    ax.set_xlabel('Power (Watts)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency (samples)', fontsize=12, fontweight='bold')
    ax.set_title(f'Power Distribution: {main_state}', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add statistics box
    stats_text = f'Samples: {len(main_state_data)}\nStd Dev: {main_state_data["Power [W]"].std():.6f}W\nCV: {(main_state_data["Power [W]"].std()/mean_val*100):.3f}%'
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / '08_power_histogram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 08_power_histogram.png")

def generate_summary_figure(df, energy_ts, state_char):
    """Bonus: Generate a comprehensive summary figure"""
    print("Generating Bonus: Summary Dashboard...")
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 1. Power timeline
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(df['TimeSeconds'], df['Power [W]'], linewidth=0.5, color='#3498db')
    ax1.set_title('Power Timeline', fontweight='bold')
    ax1.set_ylabel('Power (W)')
    ax1.grid(True, alpha=0.3)
    
    # 2. Cumulative energy
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(energy_ts['TimeSeconds'], energy_ts['CumulativeEnergy'], linewidth=2, color='#27ae60')
    ax2.fill_between(energy_ts['TimeSeconds'], energy_ts['CumulativeEnergy'], alpha=0.3, color='#27ae60')
    ax2.set_title('Cumulative Energy', fontweight='bold')
    ax2.set_ylabel('Energy (J)')
    ax2.grid(True, alpha=0.3)
    
    # 3. State power comparison
    ax3 = fig.add_subplot(gs[1, 1])
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c']
    ax3.bar(range(len(state_char)), state_char['Avg_Power_W'], color=colors, alpha=0.7)
    ax3.set_title('Power by State', fontweight='bold')
    ax3.set_ylabel('Power (W)')
    ax3.set_xticks(range(len(state_char)))
    ax3.set_xticklabels(state_char.index, rotation=45, ha='right', fontsize=8)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Energy contribution
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.bar(range(len(state_char)), state_char['Energy_J'], color=colors, alpha=0.7)
    ax4.set_title('Energy Contribution', fontweight='bold')
    ax4.set_ylabel('Energy (J)')
    ax4.set_xlabel('State')
    ax4.set_xticks(range(len(state_char)))
    ax4.set_xticklabels(state_char.index, rotation=45, ha='right', fontsize=8)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Time distribution
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.pie(state_char['Percentage'], labels=state_char.index, autopct='%1.1f%%',
            startangle=90, colors=colors, textprops={'fontsize': 8})
    ax5.set_title('Time Distribution', fontweight='bold')
    
    fig.suptitle('DVCon Challenge - Complete Power Analysis Summary', 
                 fontsize=16, fontweight='bold')
    
    plt.savefig(PLOTS_DIR / '00_summary_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 00_summary_dashboard.png")

if __name__ == "__main__":
    # Check if data exists
    required_files = [
        OUTPUT_DIR / "reports" / "cleaned_data.csv",
        OUTPUT_DIR / "reports" / "energy_timeseries.csv",
        OUTPUT_DIR / "reports" / "state_characterization.csv",
        OUTPUT_DIR / "reports" / "transitions.csv"
    ]
    
    for f in required_files:
        if not f.exists():
            print(f"Error: Missing {f.name}")
            print("Run scripts 01-04 first!")
            sys.exit(1)
    
    print("=" * 60)
    print("GENERATING ALL PLOTS")
    print("=" * 60)
    print(f"Output directory: {PLOTS_DIR}\n")
    
    # Load data
    df, energy_ts, state_char, transitions = load_all_data()
    
    # Generate all plots
    plot_power_timeline(df, transitions)
    plot_cumulative_energy(energy_ts)
    plot_time_distribution(state_char)
    plot_state_power_comparison(state_char)
    plot_transition_power_jumps(transitions)
    plot_bluetooth_comparison(df)
    plot_energy_contribution(state_char)
    plot_power_histogram(df)
    generate_summary_figure(df, energy_ts, state_char)
    
    print("\n" + "=" * 60)
    print("ALL PLOTS GENERATED SUCCESSFULLY")
    print("=" * 60)
    print(f"\n✓ Check {PLOTS_DIR} for all plots")
    print(f"✓ Check {OUTPUT_DIR}/reports for CSV files")
