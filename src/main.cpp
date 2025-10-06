/**
 * main.cpp
 */

 #include <systemc>
 #include <fstream>  // Add this for CSV output
 #include <iomanip>  // Add this for formatting
 
 // Power constants for each state (in Watts)
 const double POWER_OFFICE = 1.0357;
 const double POWER_NOT_AT_WORK = 1.0215;
 const double POWER_REMOTE = 1.0284;
 const double POWER_OFFICE_BT = 1.0960;
 const double POWER_REMOTE_BT = 1.1500;
 const double POWER_NOT_AT_WORK_BT = 1.0925;
 const double POWER_DEFAULT = 1.0;
 
 // Measured ground truth values from analysis
 const double MEASURED_TOTAL_ENERGY = 4262.89;  // Joules
 const double MEASURED_AVG_POWER = 1.0349;      // Watts
 const double MEASURED_DURATION = 4119.0;       // Seconds
 
 // Per-state measured energy (from energy_analysis.csv)
 const double MEASURED_ENERGY_STATE[6] = {
     3840.36,  // State 0: Office
     268.66,   // State 1: Not at Work
     131.64,   // State 2: Remote
     10.96,    // State 3: Office BT
     6.90,     // State 4: Remote BT
     4.37      // State 5: Not at Work BT
 };
 
 // Per-state measured duration (from state_characterization.csv)
 const int MEASURED_DURATION_STATE[6] = {
     3708,  // State 0: Office
     263,   // State 1: Not at Work
     128,   // State 2: Remote
     10,    // State 3: Office BT
     6,     // State 4: Remote BT
     4      // State 5: Not at Work BT
 };
 
 SC_MODULE(TestbenchModule) {
     sc_core::sc_port<sc_core::sc_signal_in_if<int>> status_input;
     double powerEstimation = 0.0;
     double energyEstimation = 0.0;
     
     int previous_status = -1;
     sc_core::sc_time last_transition_time;
     int transition_count = 0;
     
     // Per-state tracking
     double state_energy[6] = {0.0};
     double state_duration[6] = {0.0};  // Changed to double for seconds
 
     SC_CTOR(TestbenchModule) : status_input("input") {
         SC_THREAD(processing);
         sensitive << status_input;
         dont_initialize();
     }
 
     void processing() {
         last_transition_time = sc_core::sc_time_stamp();
         previous_status = -1;
         
         while (true) {
             int status = status_input->read();
             sc_core::sc_time current_time = sc_core::sc_time_stamp();
             
             if (previous_status >= 0) {
                 sc_core::sc_time duration = current_time - last_transition_time;
                 double duration_sec = duration.to_seconds();
                 
                 double prev_power = getPowerForState(previous_status);
                 double energy_increment = prev_power * duration_sec;
                 
                 // Accumulate total energy
                 energyEstimation += energy_increment;
                 
                 // Track per-state statistics
                 if (previous_status >= 0 && previous_status < 6) {
                     state_energy[previous_status] += energy_increment;
                     state_duration[previous_status] += duration_sec;
                 }
                 
                 std::cout << "State " << previous_status 
                          << " consumed " << energy_increment << " J"
                          << " (Total: " << energyEstimation << " J)" << std::endl;
             }
             
             powerEstimation = getPowerForState(status);
             
             std::cout << "Transitioned to state " << status 
                      << " (Power: " << powerEstimation << " W)" << std::endl;
             
             transition_count++;
             previous_status = status;
             last_transition_time = current_time;
             
             wait();
         }
     }
     
     void finalizeEnergy() {
         if (previous_status >= 0) {
             sc_core::sc_time final_time = sc_core::sc_time_stamp();
             sc_core::sc_time duration = final_time - last_transition_time;
             double duration_sec = duration.to_seconds();
             
             double final_power = getPowerForState(previous_status);
             double final_energy = final_power * duration_sec;
             
             energyEstimation += final_energy;
             
             // Track final state
             if (previous_status >= 0 && previous_status < 6) {
                 state_energy[previous_status] += final_energy;
                 state_duration[previous_status] += duration_sec;
             }
             
             std::cout << "Final state " << previous_status 
                      << " consumed " << final_energy << " J" << std::endl;
             std::cout << "Total Energy: " << energyEstimation << " J" << std::endl;
         }
     }
     
     void validateResults() {
         double error = std::abs(energyEstimation - MEASURED_TOTAL_ENERGY);
         double error_percent = (error / MEASURED_TOTAL_ENERGY) * 100.0;
         
         std::cout << "\n=== VALIDATION ===" << std::endl;
         std::cout << "Expected energy: " << MEASURED_TOTAL_ENERGY << " J" << std::endl;
         std::cout << "Calculated energy: " << energyEstimation << " J" << std::endl;
         std::cout << "Error: " << error << " J (" << error_percent << "%)" << std::endl;
         
         if (error_percent < 1.0) {
             std::cout << "✓ PASS: Within 1% tolerance" << std::endl;
         } else {
             std::cout << "✗ FAIL: Exceeds 1% tolerance" << std::endl;
         }
     }
     
     void generateValidationCSV() {
         std::ofstream csv_file("model_vs_measurement.csv");
         
         if (!csv_file.is_open()) {
             std::cerr << "Error: Could not create validation CSV file" << std::endl;
             return;
         }
         
         csv_file << std::fixed << std::setprecision(6);
         
         // === OVERALL METRICS ===
         csv_file << "=== OVERALL METRICS ===\n";
         csv_file << "Metric,Measured,Model,Error,Error_Percent\n";
         
         // Total energy
         double energy_error = energyEstimation - MEASURED_TOTAL_ENERGY;
         double energy_error_pct = (energy_error / MEASURED_TOTAL_ENERGY) * 100.0;
         csv_file << "Total Energy (J)," << MEASURED_TOTAL_ENERGY << "," 
                 << energyEstimation << "," << energy_error << "," 
                 << energy_error_pct << "\n";
         
         // Average power
         double model_avg_power = energyEstimation / MEASURED_DURATION;
         double power_error = model_avg_power - MEASURED_AVG_POWER;
         double power_error_pct = (power_error / MEASURED_AVG_POWER) * 100.0;
         csv_file << "Average Power (W)," << MEASURED_AVG_POWER << "," 
                 << model_avg_power << "," << power_error << "," 
                 << power_error_pct << "\n";
         
         // Duration
         csv_file << "Duration (s)," << MEASURED_DURATION << "," 
                 << MEASURED_DURATION << ",0.0,0.0\n";
         
         // Transitions
         csv_file << "Transitions," << "10," << transition_count - 1 << "," 
                 << (transition_count - 1 - 10) << ",0.0\n";
         
         csv_file << "\n";
         
         // === PER-STATE METRICS ===
         csv_file << "=== PER-STATE ENERGY (Joules) ===\n";
         csv_file << "State,State_Name,Measured,Model,Error,Error_Percent\n";
         
         const char* state_names[6] = {
             "At Work (Office)",
             "Not at Work",
             "At Work (Remote)",
             "Office Bluetooth",
             "Remote Bluetooth",
             "Not at Work Bluetooth"
         };
         
         double total_state_energy_error = 0.0;
         for (int i = 0; i < 6; i++) {
             double state_error = state_energy[i] - MEASURED_ENERGY_STATE[i];
             double state_error_pct = (MEASURED_ENERGY_STATE[i] > 0) ? 
                 (state_error / MEASURED_ENERGY_STATE[i]) * 100.0 : 0.0;
             
             csv_file << i << "," << state_names[i] << "," 
                     << MEASURED_ENERGY_STATE[i] << "," 
                     << state_energy[i] << "," 
                     << state_error << "," 
                     << state_error_pct << "\n";
             
             total_state_energy_error += std::abs(state_error);
         }
         
         csv_file << "\n";
         
         // === PER-STATE DURATION ===
         csv_file << "=== PER-STATE DURATION (seconds) ===\n";
         csv_file << "State,State_Name,Measured,Model,Error,Error_Percent\n";
         
         for (int i = 0; i < 6; i++) {
             double duration_error = state_duration[i] - MEASURED_DURATION_STATE[i];
             double duration_error_pct = (MEASURED_DURATION_STATE[i] > 0) ? 
                 (duration_error / MEASURED_DURATION_STATE[i]) * 100.0 : 0.0;
             
             csv_file << i << "," << state_names[i] << "," 
                     << MEASURED_DURATION_STATE[i] << "," 
                     << state_duration[i] << "," 
                     << duration_error << "," 
                     << duration_error_pct << "\n";
         }
         
         csv_file << "\n";
         
         // === SUMMARY STATISTICS ===
         csv_file << "=== SUMMARY STATISTICS ===\n";
         csv_file << "Metric,Value\n";
         csv_file << "Total Energy Error (J)," << std::abs(energy_error) << "\n";
         csv_file << "Total Energy Error (%)," << std::abs(energy_error_pct) << "\n";
         csv_file << "Per-State Energy Error Sum (J)," << total_state_energy_error << "\n";
         csv_file << "Model Status," << (std::abs(energy_error_pct) < 1.0 ? "PASS" : "FAIL") << "\n";
         
         csv_file.close();
         
         std::cout << "\n✓ Validation CSV generated: model_vs_measurement.csv" << std::endl;
     }
 
 private:
     double getPowerForState(int state) {
         switch(state) {
             case 0: return POWER_OFFICE;
             case 1: return POWER_NOT_AT_WORK;
             case 2: return POWER_REMOTE;
             case 3: return POWER_OFFICE_BT;
             case 4: return POWER_REMOTE_BT;
             case 5: return POWER_NOT_AT_WORK_BT;
             default: return POWER_DEFAULT;
         }
     }
 };
 
 SC_MODULE(QUEUE) {
     sc_core::sc_port<sc_core::sc_signal_out_if<int>> status_out;
     
     SC_CTOR(QUEUE) : status_out("out") {
         SC_THREAD(generateRealisticSequence);
     }
     
     void generateRealisticSequence() {
         // Based on actual measurement data
         status_out->write(1); wait(10, sc_core::SC_SEC);
         status_out->write(0); wait(143, sc_core::SC_SEC);
         status_out->write(4); wait(6, sc_core::SC_SEC);
         status_out->write(2); wait(128, sc_core::SC_SEC);
         status_out->write(0); wait(84, sc_core::SC_SEC);
         status_out->write(5); wait(4, sc_core::SC_SEC);
         status_out->write(1); wait(231, sc_core::SC_SEC);
         status_out->write(0); wait(2526, sc_core::SC_SEC);
         status_out->write(3); wait(10, sc_core::SC_SEC);
         status_out->write(0); wait(955, sc_core::SC_SEC);
         status_out->write(1); wait(22, sc_core::SC_SEC);
         
         std::cout << "Test sequence complete" << std::endl;
     }
 };
 
 int sc_main(int argc, char* argv[]) {
     sc_core::sc_set_time_resolution(1.0, sc_core::SC_SEC);
 
     sc_core::sc_signal<int> signal;
 
     QUEUE queue("queue");
     TestbenchModule testbench("testbench");
     queue.status_out(signal);
     testbench.status_input(signal);
 
     std::cout << "Simulation started..." << std::endl;
     sc_core::sc_start(4119, sc_core::SC_SEC);
     
     testbench.finalizeEnergy();
     testbench.validateResults();
     testbench.generateValidationCSV();  // Generate CSV after validation
     
     std::cout << "Simulation finished." << std::endl;
     std::cout << "-----------------------------" << std::endl << std::endl;
 
     std::cout << "Calculated Average Power: " << testbench.powerEstimation << " W" << std::endl;
     std::cout << "Calculated Average Energy: " << testbench.energyEstimation << " J" << std::endl;
     
     return 0;
 }