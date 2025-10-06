# DVCon Europe 2025 SystemC Modeling Challenge
In this repository you find the elements and data that is requrired to pass this challenge. Allowing you to get a good standing and introduction to the elements. Please visit the Website of the DVCon Challenge: [https://dvconchallenge.de/](https://dvconchallenge.de/)

# Table of Contents

[toc]

# How to get started

We offer you two ways to get started. One way is that you already have SystemC installed, then please skip to [direct usage](#2-direct-usage). In the other way, we offer you the usage of the package manager [conan](https://conan.io/).

## Packagemanager Usage

To use conan you might use the follwing commands. Preferable you will use the debug mode.

```bash
mkdir build && cd build
conan install .. -s build_type=Debug
conan build .. -s build_type=Debug
```

Now you are able to build and test your files.

## Direct usage

We require at least SystemC 2.3.4. Also please set the variable SYSTEMC_HOME for cmake. If that is done, you can run the following commands.

```bash
mkdir build && cd build
cmake ..
make
```

# Power Model Characterization

This section describes how the power model was derived from measurement data and implemented in SystemC.

## Overview

The power model is based on actual measurement data from a smartwatch tracking employee activity states. The characterization process involved:
1. Data exploration and cleaning
2. State characterization and power analysis
3. Transition analysis
4. Model validation

## Data Analysis Scripts

The `analysis/` directory contains Python scripts for data characterization:

### 1. Data Exploration (`01_data_exploration.py`)

**Purpose:** Initial exploration and cleaning of raw measurement data

**Key Functions:**
- Loads raw CSV data from `DVConChallengeLongTimeMeasurement_2.csv`
- Cleans and validates timestamps
- Identifies state transitions
- Generates summary statistics
- Creates visualizations:
  - Power timeline
  - Cumulative energy consumption
  - Time distribution across states

**Outputs:**
- `output/reports/cleaned_data.csv` - Cleaned dataset
- `output/reports/data_summary.txt` - Statistical summary
- Timeline and distribution plots

### 2. State Characterization (`02_state_characterization.py`)

**Purpose:** Characterize power consumption for each device state

**Key Analysis:**
- Calculates mean power consumption per state
- Analyzes power stability (standard deviation)
- Computes energy contribution by state
- Identifies Bluetooth activity patterns

**State Power Values Extracted:**
```cpp
State 0 (Office):           1.0357 W
State 1 (Not at Work):      1.0215 W
State 2 (Remote):           1.0284 W
State 3 (Office Bluetooth): 1.0960 W
State 4 (Remote Bluetooth): 1.1500 W
State 5 (Not Work BT):      1.0925 W
```

**Outputs:**
- `output/reports/state_characterization.csv` - Per-state statistics
- `output/reports/energy_analysis.csv` - Energy breakdown
- Power histogram and energy contribution plots

### 3. Transition Analysis (`03_transition_analysis.py`)

**Purpose:** Analyze state transition patterns and durations

**Analysis:**
- Counts state transitions
- Computes dwell times (how long device stays in each state)
- Identifies transition sequences
- Validates energy calculations

**Outputs:**
- `output/reports/transitions.csv` - Transition matrix
- Transition pattern visualizations

### 4. Summary Dashboard (`04_summary_dashboard.py`)

**Purpose:** Generate comprehensive visualization dashboard

**Creates:**
- Multi-panel summary dashboard
- Combined timeline and energy plots
- State distribution comparisons
- Bluetooth activity analysis

### 5. Code Generation (`05_generate_code.py`)

**Purpose:** Auto-generate SystemC code snippets from characterized data

**Generates:**
- `getPowerForState()` function with measured values
- State constants
- Realistic test sequences based on actual transitions

**Output Example:**
```cpp
const double POWER_OFFICE = 1.0357;  // State 0
const double POWER_NOT_AT_WORK = 1.0215;  // State 1
// ... etc
```

## Running the Analysis

To reproduce the characterization:

```bash
cd analysis
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run all analyses
./run_all.sh

# Or run individually
python scripts/01_data_exploration.py
python scripts/02_state_characterization.py
python scripts/03_transition_analysis.py
python scripts/04_summary_dashboard.py
python scripts/05_generate_code.py
```

## Model Construction

### Power Model Implementation

The SystemC model implements energy calculation using the fundamental physics equation:

**Energy = Power × Time**

Key implementation details:

1. **State Power Values:** Global constants derived from measurement data
2. **Energy Accumulation:** Calculate energy for each state transition
3. **Final State Handling:** Account for energy in the last state before simulation end
4. **Validation:** Compare against ground truth (4262.89 J from measurements)

### Model Structure

```cpp
// Power characterization (from measurements)
const double POWER_OFFICE = 1.0357 W;
// ... other states

// Energy calculation (Physics: E = P × t)
if (previous_status >= 0) {
    sc_time duration = current_time - last_transition_time;
    double prev_power = getPowerForState(previous_status);
    double energy_increment = prev_power × duration.to_seconds();
    energyEstimation += energy_increment;
}
```

### Test Sequence

The realistic test sequence was extracted from actual measurement data:
- 10 state transitions
- 4119 seconds total duration
- Matches real-world usage pattern

### Validation Results

The model achieves excellent accuracy:
- **Expected Energy:** 4262.89 J (from measurements)
- **Calculated Energy:** 4262.9 J (from model)
- **Error:** 0.0053 J (0.000124% - virtually perfect)
- **Status:** ✓ PASS (within 1% tolerance)

## Key Insights from Characterization

1. **Power Consumption:** Office state (1.0357 W) has highest base consumption
2. **Bluetooth Impact:** Adds ~5-12% power overhead depending on state
3. **Dominant States:** Office work sessions consume most total energy
4. **Model Accuracy:** Proper time-weighted energy calculation is critical

## References

- Measurement data: `analysis/data/DVConChallengeLongTimeMeasurement_2.csv`
- State mapping: `analysis/data/DVConChallengeLongTimeMeasurement_States.csv`
- Generated plots: `analysis/output/plots/`
- Characterization reports: `analysis/output/reports/`

# Next steps

1. Implement your strategy for the hackathon.
2. Send your model to us.

# More Information

Please visit the [guide for participants ](https://dvconchallenge.de/index.php/guide-for-participants/)at our website.
