# DVCon Challenge - Incremental Implementation Plan

## Overview
Implement the power model in 8 incremental phases. Each phase adds one feature, includes testing, and ends with a commit.

---

## Phase 1: Add Power Characterization Function
**Goal:** Create the power lookup function with correct values

### Implementation
Add this private method to TestbenchModule (don't change anything else yet):

```cpp
private:
    // Add this function but DON'T use it yet
    double getPowerForState(int state) {
        switch(state) {
            case 0: return 1.0357;  // At Work (Office)
            case 1: return 1.0215;  // Not at Work
            case 2: return 1.0284;  // At Work (Remote)
            case 3: return 1.0960;  // Office Bluetooth
            case 4: return 1.1500;  // Remote Bluetooth
            case 5: return 1.0925;  // Not at Work Bluetooth
            default: return 1.0;
        }
    }
```

### Test
```bash
make
# Should still compile and run exactly as before
./testbench_dvconchallenge
```

### Verify
- ✅ Code compiles without errors
- ✅ Existing functionality unchanged
- ✅ Output same as before

### Commit
```bash
git add -A
git commit -m "feat: Add power characterization function with measured values"
```

---

## Phase 2: Add State Tracking Variables
**Goal:** Add variables to track state transitions (don't use them yet)

### Implementation
Add these member variables to TestbenchModule:

```cpp
SC_MODULE(TestbenchModule) {
    // ... existing code ...
    
    // Add these new tracking variables
    int previous_status = -1;
    sc_core::sc_time last_transition_time;
    int transition_count = 0;
    
    // Statistics arrays
    double state_energy[6] = {0.0};
    sc_core::sc_time state_duration[6];
```

### Test
```bash
make
./testbench_dvconchallenge
```

### Verify
- ✅ Still compiles
- ✅ Runs without crashing
- ✅ Output unchanged

### Commit
```bash
git add -A
git commit -m "feat: Add state tracking variables for power model"
```

---

## Phase 3: Fix Power Assignment (Critical Bug Fix)
**Goal:** Change power from accumulation to assignment

### Implementation
In the processing() method, change ONLY the power assignment lines:

```cpp
switch(status) {
    case 0:
        std::cout << "Booting" << std::endl;
        powerEstimation = 1.6;  // Changed from += to =
        break;
    case 1:
        std::cout << "Employee not available" << std::endl;
        powerEstimation = 1.35;  // Changed from += to =
        break;
    // ... rest stays the same for now
}
```

### Test
```bash
make
./testbench_dvconchallenge
```

### Verify
- ✅ Power value no longer grows infinitely
- ✅ Energy calculation still wrong (that's OK for now)

### Commit
```bash
git add -A
git commit -m "fix: Change power from accumulation to assignment (critical physics fix)"
```

---

## Phase 4: Add Time Tracking
**Goal:** Initialize and update time tracking (but don't calculate energy yet)

### Implementation
Modify the processing() method beginning:

```cpp
void processing() {
    // Initialize time tracking
    last_transition_time = sc_core::sc_time_stamp();
    previous_status = -1;
    
    while (true) {
        int status = status_input->read();
        sc_core::sc_time current_time = sc_core::sc_time_stamp();
        
        // Add debug output to verify time tracking
        if (previous_status >= 0) {
            sc_core::sc_time duration = current_time - last_transition_time;
            std::cout << "DEBUG: State " << previous_status 
                     << " lasted " << duration.to_seconds() << " seconds" << std::endl;
        }
        
        // Existing switch statement here (keep as is)
        switch(status) {
            // ... existing cases ...
        }
        
        // Update tracking variables
        previous_status = status;
        last_transition_time = current_time;
        transition_count++;
        
        wait();
    }
}
```

### Test
```bash
make
./testbench_dvconchallenge
# Should now see "DEBUG: State X lasted Y seconds" messages
```

### Verify
- ✅ Time duration messages appear
- ✅ Durations look reasonable
- ✅ Still runs to completion

### Commit
```bash
git add -A
git commit -m "feat: Add time duration tracking with debug output"
```

---

## Phase 5: Implement Correct Energy Calculation
**Goal:** Calculate energy as Power × Time (the main fix!)

### Implementation
Replace the switch statement in processing() with energy calculation:

```cpp
void processing() {
    last_transition_time = sc_core::sc_time_stamp();
    previous_status = -1;
    
    while (true) {
        int status = status_input->read();
        sc_core::sc_time current_time = sc_core::sc_time_stamp();
        
        // CRITICAL: Calculate energy from PREVIOUS state
        if (previous_status >= 0) {
            sc_core::sc_time duration = current_time - last_transition_time;
            double duration_sec = duration.to_seconds();
            
            // Use the new getPowerForState function
            double prev_power = getPowerForState(previous_status);
            double energy_increment = prev_power * duration_sec;
            
            // Accumulate ENERGY (not power!)
            energyEstimation += energy_increment;
            
            std::cout << "State " << previous_status 
                     << " consumed " << energy_increment << " J"
                     << " (Total: " << energyEstimation << " J)" << std::endl;
        }
        
        // Set current instantaneous power (not accumulate!)
        powerEstimation = getPowerForState(status);
        
        std::cout << "Transitioned to state " << status 
                 << " (Power: " << powerEstimation << " W)" << std::endl;
        
        previous_status = status;
        last_transition_time = current_time;
        
        wait();
    }
}
```

### Test
```bash
make
./testbench_dvconchallenge
# Energy should now accumulate properly!
```

### Verify
- ✅ Energy increases over time
- ✅ Power values match getPowerForState()
- ✅ Energy = Power × Time for each state

### Commit
```bash
git add -A
git commit -m "feat: Implement correct energy calculation (Power × Time)"
```

---

## Phase 6: Add Final State Handling
**Goal:** Account for energy in the last state

### Implementation
Add this public method to TestbenchModule:

```cpp
public:
    void finalizeEnergy() {
        if (previous_status >= 0) {
            sc_core::sc_time final_time = sc_core::sc_time_stamp();
            sc_core::sc_time duration = final_time - last_transition_time;
            double duration_sec = duration.to_seconds();
            
            double final_power = getPowerForState(previous_status);
            double final_energy = final_power * duration_sec;
            
            energyEstimation += final_energy;
            
            std::cout << "Final state " << previous_status 
                     << " consumed " << final_energy << " J" << std::endl;
            std::cout << "Total Energy: " << energyEstimation << " J" << std::endl;
        }
    }
```

Modify sc_main to call it:

```cpp
int sc_main(int argc, char* argv[]) {
    // ... existing setup ...
    
    sc_core::sc_start(1296000, sc_core::SC_SEC);
    
    // Add this line
    testbench.finalizeEnergy();
    
    std::cout << "Simulation finished." << std::endl;
    // ... rest of output ...
}
```

### Test
```bash
make
./testbench_dvconchallenge
# Should now show "Final state X consumed Y J"
```

### Verify
- ✅ Final state energy is calculated
- ✅ Total energy includes last state
- ✅ Energy value more realistic

### Commit
```bash
git add -A
git commit -m "feat: Add final state energy calculation"
```

---

## Phase 7: Add Realistic Test Sequence
**Goal:** Replace dummy test with real measurement sequence

### Implementation
Replace the entire QUEUE module with realistic version:

```cpp
SC_MODULE(QUEUE) {
    sc_core::sc_port<sc_core::sc_signal_out_if<int>> status_out;
    
    SC_CTOR(QUEUE) : status_out("out") {
        SC_THREAD(generateRealisticSequence);
        dont_initialize();
    }
    
    void generateRealisticSequence() {
        // Based on actual measurement data
        status_out->write(1); wait(10, SC_SEC);    // Not at Work
        status_out->write(0); wait(143, SC_SEC);   // Office
        status_out->write(4); wait(6, SC_SEC);     // Remote BT
        status_out->write(2); wait(128, SC_SEC);   // Remote
        status_out->write(0); wait(84, SC_SEC);    // Office
        status_out->write(5); wait(4, SC_SEC);     // Not Work BT
        status_out->write(1); wait(231, SC_SEC);   // Not at Work
        status_out->write(0); wait(2526, SC_SEC);  // Office (long)
        status_out->write(3); wait(10, SC_SEC);    // Office BT
        status_out->write(0); wait(955, SC_SEC);   // Office
        status_out->write(1); wait(22, SC_SEC);    // Not at Work
        
        std::cout << "Test sequence complete" << std::endl;
    }
};
```

Change simulation time in sc_main:

```cpp
// Change from 1296000 to 4119 (actual measurement duration)
sc_core::sc_start(4119, sc_core::SC_SEC);
```

### Test
```bash
make
./testbench_dvconchallenge
# Should run for 4119 seconds with 10 transitions
```

### Verify
- ✅ Simulation runs for 4119 seconds
- ✅ Shows 10 state transitions
- ✅ Energy around 4200-4300 J

### Commit
```bash
git add -A
git commit -m "feat: Add realistic test sequence from measurement data"
```

---

## Phase 8: Add Validation and Statistics
**Goal:** Add final validation against ground truth

### Implementation
Add validation method to TestbenchModule:

```cpp
public:
    void validateResults() {
        double expected_energy = 4262.89;
        double error = std::abs(energyEstimation - expected_energy);
        double error_percent = (error / expected_energy) * 100.0;
        
        std::cout << "\n=== VALIDATION ===" << std::endl;
        std::cout << "Expected energy: " << expected_energy << " J" << std::endl;
        std::cout << "Calculated energy: " << energyEstimation << " J" << std::endl;
        std::cout << "Error: " << error << " J (" << error_percent << "%)" << std::endl;
        
        if (error_percent < 1.0) {
            std::cout << "✓ PASS: Within 1% tolerance" << std::endl;
        } else {
            std::cout << "✗ FAIL: Exceeds 1% tolerance" << std::endl;
        }
    }
```

Call it in sc_main after finalizeEnergy():

```cpp
testbench.finalizeEnergy();
testbench.validateResults();  // Add this
```

### Test
```bash
make
./testbench_dvconchallenge
# Should show PASS with <1% error
```

### Verify
- ✅ Shows validation results
- ✅ Error < 1% (should PASS)
- ✅ Final energy: 4262.89 ± 43 J

### Commit
```bash
git add -A
git commit -m "feat: Add validation against ground truth - Challenge Complete!"
```

---

## Final Verification Checklist

Run final test to ensure everything works:

```bash
make clean
make
./testbench_dvconchallenge
```

Should see:
- [ ] 10 state transitions
- [ ] Energy: ~4263 J
- [ ] "✓ PASS: Within 1% tolerance"
- [ ] Average power: ~1.035 W

## Summary of Commits

1. `feat: Add power characterization function with measured values`
2. `feat: Add state tracking variables for power model`
3. `fix: Change power from accumulation to assignment (critical physics fix)`
4. `feat: Add time duration tracking with debug output`
5. `feat: Implement correct energy calculation (Power × Time)`
6. `feat: Add final state energy calculation`
7. `feat: Add realistic test sequence from measurement data`
8. `feat: Add validation against ground truth - Challenge Complete!`

Each phase builds on the previous one, maintaining a working system throughout the implementation process.