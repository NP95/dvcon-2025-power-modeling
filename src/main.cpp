/**
 * main.cpp
 *
 *  Created on: 10.07.2024
 *      Author: herzog
 */


#include <systemc>

// Power constants for each state (in Watts)
const double POWER_OFFICE = 1.0357;           // State 0: At Work (Office)
const double POWER_NOT_AT_WORK = 1.0215;      // State 1: Not at Work
const double POWER_REMOTE = 1.0284;           // State 2: At Work (Remote)
const double POWER_OFFICE_BT = 1.0960;        // State 3: Office Bluetooth
const double POWER_REMOTE_BT = 1.1500;        // State 4: Remote Bluetooth
const double POWER_NOT_AT_WORK_BT = 1.0925;   // State 5: Not at Work Bluetooth
const double POWER_DEFAULT = 1.0;             // Default power value

/**
 * Testbench Module
 */
SC_MODULE(TestbenchModule) {
    sc_core::sc_port<sc_core::sc_signal_in_if<int>> status_input;
    double powerEstimation = 0.0;
    double energyEstimation = 0.0;
    
    // Add these new tracking variables
    int previous_status = -1;
    sc_core::sc_time last_transition_time;
    int transition_count = 0;
    
    // Statistics arrays
    double state_energy[6] = {0.0};
    sc_core::sc_time state_duration[6];

    SC_CTOR(TestbenchModule) : status_input("input") {
        SC_THREAD(processing);
        sensitive << status_input; // triggered by value change on the channel
        dont_initialize();
    }

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

private:
    // Add this function but DON'T use it yet
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

/**
 * An example for the queue, that we are using for the triggering of the Testmodule that you will implement.
 */
SC_MODULE(QUEUE) {
    sc_core::sc_port<sc_core::sc_signal_out_if<int>> status_out;
    
    SC_CTOR(QUEUE) : status_out("out") {
        SC_THREAD(generateRealisticSequence);
    }
    
    void generateRealisticSequence() {
        // Based on actual measurement data
        status_out->write(1); wait(10, sc_core::SC_SEC);    // Not at Work
        status_out->write(0); wait(143, sc_core::SC_SEC);   // Office
        status_out->write(4); wait(6, sc_core::SC_SEC);     // Remote BT
        status_out->write(2); wait(128, sc_core::SC_SEC);   // Remote
        status_out->write(0); wait(84, sc_core::SC_SEC);    // Office
        status_out->write(5); wait(4, sc_core::SC_SEC);     // Not Work BT
        status_out->write(1); wait(231, sc_core::SC_SEC);   // Not at Work
        status_out->write(0); wait(2526, sc_core::SC_SEC);  // Office (long)
        status_out->write(3); wait(10, sc_core::SC_SEC);    // Office BT
        status_out->write(0); wait(955, sc_core::SC_SEC);   // Office
        status_out->write(1); wait(22, sc_core::SC_SEC);    // Not at Work
        
        std::cout << "Test sequence complete" << std::endl;
    }
};


int sc_main(int argc, char* argv[]) {
	sc_core::sc_set_time_resolution(1.0, sc_core::SC_SEC);

    sc_core::sc_signal<int> signal;

	QUEUE queue("queue"); // instantiate object
	TestbenchModule testbench("testbench");
    queue.status_out(signal);
    testbench.status_input(signal);


	std::cout << "Simulation started..." << std::endl;
    sc_core::sc_start(4119, sc_core::SC_SEC);
    
    // Add this line
    testbench.finalizeEnergy();
    testbench.validateResults();  // Add this
    
	std::cout << "Simulation finished." << std::endl;
    std::cout << "-----------------------------" << std::endl << std::endl;

    std::cout << "Calculated Average Power: "<<testbench.powerEstimation<<" W"<<std::endl;
    std::cout << "Calculated Average Energy: "<<testbench.energyEstimation<<" J"<<std::endl;
	return 0;
}


