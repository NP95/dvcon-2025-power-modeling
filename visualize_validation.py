"""
visualize_validation.py
Visualizes model vs. measurement comparison from SystemC model output
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Configuration
CSV_FILE = "model_vs_measurement.csv"
OUTPUT_DIR = Path("validation_plots")
OUTPUT_DIR.mkdir(exist_ok=True)

def parse_validation_csv(filename):
    """Parse the multi-section CSV file"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    sections = {}
    current_section = None
    section_data = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('==='):
            # Save previous section
            if current_section and section_data:
                sections[current_section] = section_data
            # Start new section
            current_section = line.strip('= ')
            section_data = []
        elif line and current_section:
            section_data.append(line)
    
    # Save last section
    if current_section and section_data:
        sections[current_section] = section_data
    
    return sections

def parse_section_to_df(section_lines):
    """Convert section lines to DataFrame"""
    from io import StringIO
    data = '\n'.join(section_lines)
    return pd.read_csv(StringIO(data))

def plot_overall_metrics(df_overall):
    """Plot overall metrics comparison"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Filter out non-numeric metrics
    df_plot = df_overall[df_overall['Metric'].str.contains('Energy|Power')].copy()
    
    metrics = df_plot['Metric'].values
    measured = df_plot['Measured'].values
    model = df_plot['Model'].values
    
    x = np.arange(len(metrics))
    width = 0.35
    
    # Bar chart comparison
    ax1.bar(x - width/2, measured, width, label='Measured', color='#3498db', alpha=0.8)
    ax1.bar(x + width/2, model, width, label='Model', color='#e74c3c', alpha=0.8)
    
    ax1.set_xlabel('Metric', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Value', fontsize=12, fontweight='bold')
    ax1.set_title('Overall Metrics: Measured vs Model', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Error percentage chart
    errors = df_plot['Error_Percent'].abs().values
    colors = ['#27ae60' if e < 0.01 else '#f39c12' if e < 0.1 else '#e74c3c' for e in errors]
    
    ax2.bar(x, errors, color=colors, alpha=0.8)
    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='1% Threshold')
    ax2.set_xlabel('Metric', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Absolute Error (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Error Percentage by Metric', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(metrics, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_yscale('log')  # Log scale to see small errors
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'overall_metrics_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated: overall_metrics_comparison.png")

def plot_state_energy(df_states):
    """Plot per-state energy comparison"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    states = df_states['State_Name'].values
    measured = df_states['Measured'].values
    model = df_states['Model'].values
    errors = df_states['Error'].values
    
    x = np.arange(len(states))
    width = 0.35
    
    # Energy comparison
    ax1.bar(x - width/2, measured, width, label='Measured', color='#3498db', alpha=0.8)
    ax1.bar(x + width/2, model, width, label='Model', color='#e74c3c', alpha=0.8)
    
    ax1.set_xlabel('State', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Energy (Joules)', fontsize=12, fontweight='bold')
    ax1.set_title('Per-State Energy: Measured vs Model', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(states, rotation=45, ha='right', fontsize=9)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add percentage labels
    for i, (m, mdl) in enumerate(zip(measured, model)):
        total_measured = measured.sum()
        pct = (m / total_measured) * 100
        ax1.text(i, max(m, mdl), f'{pct:.1f}%', ha='center', va='bottom', fontsize=8)
    
    # Error bars
    colors = ['#27ae60' if e >= 0 else '#e74c3c' for e in errors]
    ax2.bar(x, errors, color=colors, alpha=0.8)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    
    ax2.set_xlabel('State', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Error (Joules)', fontsize=12, fontweight='bold')
    ax2.set_title('Per-State Energy Error (Model - Measured)', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(states, rotation=45, ha='right', fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'state_energy_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated: state_energy_comparison.png")

def plot_state_duration(df_duration):
    """Plot per-state duration comparison"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    states = df_duration['State_Name'].values
    measured = df_duration['Measured'].values
    model = df_duration['Model'].values
    
    x = np.arange(len(states))
    width = 0.35
    
    # Duration comparison
    ax1.bar(x - width/2, measured, width, label='Measured', color='#9b59b6', alpha=0.8)
    ax1.bar(x + width/2, model, width, label='Model', color='#f39c12', alpha=0.8)
    
    ax1.set_xlabel('State', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Duration (seconds)', fontsize=12, fontweight='bold')
    ax1.set_title('Per-State Duration: Measured vs Model', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(states, rotation=45, ha='right', fontsize=9)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Pie chart of time distribution
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c']
    ax2.pie(measured, labels=states, autopct='%1.1f%%', startangle=90, 
            colors=colors, textprops={'fontsize': 9})
    ax2.set_title('Time Distribution by State', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'state_duration_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated: state_duration_comparison.png")

def plot_error_heatmap(df_energy, df_duration):
    """Create error heatmap for all metrics"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    states = df_energy['State_Name'].values
    
    # Combine errors
    energy_errors = df_energy['Error_Percent'].values
    duration_errors = df_duration['Error_Percent'].values
    
    # Create matrix
    error_matrix = np.array([energy_errors, duration_errors])
    
    im = ax.imshow(error_matrix, cmap='RdYlGn_r', aspect='auto', vmin=-1, vmax=1)
    
    # Set ticks
    ax.set_xticks(np.arange(len(states)))
    ax.set_yticks(np.arange(2))
    ax.set_xticklabels(states, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(['Energy Error %', 'Duration Error %'])
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Error Percentage', rotation=270, labelpad=20)
    
    # Add text annotations
    for i in range(2):
        for j in range(len(states)):
            text = ax.text(j, i, f'{error_matrix[i, j]:.3f}%',
                          ha="center", va="center", color="black", fontsize=8)
    
    ax.set_title('Error Heatmap: Model vs Measured', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'error_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated: error_heatmap.png")

def create_summary_dashboard(sections):
    """Create comprehensive summary dashboard"""
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Parse data
    df_overall = parse_section_to_df(sections['OVERALL METRICS'])
    df_energy = parse_section_to_df(sections['PER-STATE ENERGY (Joules)'])
    df_duration = parse_section_to_df(sections['PER-STATE DURATION (seconds)'])
    
    # 1. Overall metrics
    ax1 = fig.add_subplot(gs[0, :])
    df_plot = df_overall[df_overall['Metric'].str.contains('Energy|Power')]
    metrics = df_plot['Metric'].values
    measured = df_plot['Measured'].values
    model = df_plot['Model'].values
    x = np.arange(len(metrics))
    width = 0.35
    ax1.bar(x - width/2, measured, width, label='Measured', color='#3498db', alpha=0.8)
    ax1.bar(x + width/2, model, width, label='Model', color='#e74c3c', alpha=0.8)
    ax1.set_title('Overall Metrics Comparison', fontweight='bold', fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 2. State energy
    ax2 = fig.add_subplot(gs[1, 0])
    states = df_energy['State_Name'].values
    x = np.arange(len(states))
    width = 0.35
    ax2.bar(x - width/2, df_energy['Measured'].values, width, label='Measured', 
            color='#3498db', alpha=0.8)
    ax2.bar(x + width/2, df_energy['Model'].values, width, label='Model', 
            color='#e74c3c', alpha=0.8)
    ax2.set_title('Per-State Energy', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Energy (J)', fontsize=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(states, rotation=45, ha='right', fontsize=8)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. State duration
    ax3 = fig.add_subplot(gs[1, 1])
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c']
    ax3.pie(df_duration['Measured'].values, labels=states, autopct='%1.1f%%',
            startangle=90, colors=colors, textprops={'fontsize': 8})
    ax3.set_title('Time Distribution', fontweight='bold', fontsize=12)
    
    # 4. Energy errors
    ax4 = fig.add_subplot(gs[2, 0])
    colors_err = ['#27ae60' if e >= 0 else '#e74c3c' for e in df_energy['Error'].values]
    ax4.bar(x, df_energy['Error'].values, color=colors_err, alpha=0.8)
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax4.set_title('Energy Error by State', fontweight='bold', fontsize=12)
    ax4.set_ylabel('Error (J)', fontsize=10)
    ax4.set_xticks(x)
    ax4.set_xticklabels(states, rotation=45, ha='right', fontsize=8)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Error percentages
    ax5 = fig.add_subplot(gs[2, 1])
    error_pcts = df_energy['Error_Percent'].abs().values
    colors_pct = ['#27ae60' if e < 0.01 else '#f39c12' if e < 0.1 else '#e74c3c' 
                  for e in error_pcts]
    ax5.bar(x, error_pcts, color=colors_pct, alpha=0.8)
    ax5.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='1% Threshold')
    ax5.set_title('Error Percentage by State', fontweight='bold', fontsize=12)
    ax5.set_ylabel('|Error| (%)', fontsize=10)
    ax5.set_xticks(x)
    ax5.set_xticklabels(states, rotation=45, ha='right', fontsize=8)
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.set_yscale('log')
    
    fig.suptitle('DVCon Challenge - Model Validation Dashboard', 
                 fontsize=16, fontweight='bold')
    
    plt.savefig(OUTPUT_DIR / 'validation_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated: validation_dashboard.png")

def print_summary_report(sections):
    """Print text summary of validation results"""
    df_overall = parse_section_to_df(sections['OVERALL METRICS'])
    df_summary = parse_section_to_df(sections['SUMMARY STATISTICS'])
    
    print("\n" + "="*60)
    print("VALIDATION SUMMARY REPORT")
    print("="*60)
    
    # Overall metrics
    print("\n--- Overall Metrics ---")
    for _, row in df_overall.iterrows():
        if 'Energy' in row['Metric'] or 'Power' in row['Metric']:
            print(f"{row['Metric']}:")
            print(f"  Measured: {row['Measured']:.6f}")
            print(f"  Model:    {row['Model']:.6f}")
            print(f"  Error:    {row['Error']:.6f} ({row['Error_Percent']:.6f}%)")
    
    # Summary statistics
    print("\n--- Summary Statistics ---")
    for _, row in df_summary.iterrows():
        print(f"{row['Metric']}: {row['Value']}")
    
    print("\n" + "="*60)

def main():
    print("="*60)
    print("Model vs Measurement Visualization")
    print("="*60)
    
    # Check if CSV exists
    if not Path(CSV_FILE).exists():
        print(f"Error: {CSV_FILE} not found!")
        print("Run the SystemC simulation first to generate the CSV file.")
        return
    
    print(f"\nReading: {CSV_FILE}")
    
    # Parse CSV
    sections = parse_validation_csv(CSV_FILE)
    
    # Parse each section
    df_overall = parse_section_to_df(sections['OVERALL METRICS'])
    df_energy = parse_section_to_df(sections['PER-STATE ENERGY (Joules)'])
    df_duration = parse_section_to_df(sections['PER-STATE DURATION (seconds)'])
    
    print(f"Output directory: {OUTPUT_DIR}/\n")
    
    # Generate plots
    plot_overall_metrics(df_overall)
    plot_state_energy(df_energy)
    plot_state_duration(df_duration)
    plot_error_heatmap(df_energy, df_duration)
    create_summary_dashboard(sections)
    
    # Print summary
    print_summary_report(sections)
    
    print(f"\n✓ All plots saved to: {OUTPUT_DIR}/")
    print("="*60)

if __name__ == "__main__":
    main()