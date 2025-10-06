#!/bin/bash

echo "=========================================="
echo "DVCon Challenge - Complete Analysis"
echo "=========================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run all scripts in sequence
echo ""
echo "Step 1: Data Exploration..."
python scripts/01_data_exploration.py
if [ $? -ne 0 ]; then
    echo "Error in data exploration!"
    exit 1
fi

echo ""
echo "Step 2: State Characterization..."
python scripts/02_state_characterization.py
if [ $? -ne 0 ]; then
    echo "Error in state characterization!"
    exit 1
fi

echo ""
echo "Step 3: Transition Analysis..."
python scripts/03_transition_analysis.py
if [ $? -ne 0 ]; then
    echo "Error in transition analysis!"
    exit 1
fi

echo ""
echo "Step 4: Energy Analysis..."
python scripts/04_energy_analysis.py
if [ $? -ne 0 ]; then
    echo "Error in energy analysis!"
    exit 1
fi

echo ""
echo "Step 5: Generating All Plots..."
python scripts/05_generate_all_plots.py
if [ $? -ne 0 ]; then
    echo "Error generating plots!"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ ANALYSIS COMPLETE!"
echo "=========================================="
echo ""
echo "Results:"
echo "  - Plots: output/plots/"
echo "  - Reports: output/reports/"
echo ""
