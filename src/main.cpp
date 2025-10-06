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

    SC_CTOR(TestbenchModule) : status_input("input") {
        SC_THREAD(processing);
        sensitive << status_input; // triggered by value change on the channel
        dont_initialize();
    }

    void processing() {
        while (true) {
            int status = status_input->read();
            //TODO to be filled by you!

            switch(status) {
                case 0: //Boot Status
                    std::cout << "Booting" << std::endl;
                    powerEstimation += 1.6;
                    break;
                case 1: //Not Available
                    std::cout << "Employee not available" << std::endl;
                    powerEstimation += 1.35;
                    break;
                case 2: //Available
                    std::cout << "Employee available" << std::endl;
                    break;
                case 3: //At University
                    std::cout << "Employee somewhere" << std::endl;
                    break;
                case 4: //Bluetooth
                    std::cout << "Bluetooth package received and sent" << std::endl;
                    energyEstimation += 2.1;
                    break;
            }

            wait();
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
    sc_core::sc_event_queue eq;
    int status = -1;
    sc_core::sc_port<sc_core::sc_signal_out_if<int>> status_out;

    SC_CTOR(QUEUE) : status_out("out"){
        SC_THREAD(trigger);
        SC_THREAD(catch_eq);
        sensitive << eq; // cach_eq() will be triggered by event queue eq
        dont_initialize(); // don't run catch_eq() during initialization phase
    }

    void trigger(){
        while (true) {
            eq.notify(1, sc_core::SC_SEC);
            eq.notify(100, sc_core::SC_SEC);
            eq.notify(3600, sc_core::SC_SEC);
            eq.notify(3602, sc_core::SC_SEC);
            wait(3602, sc_core::SC_SEC); // another round
        }
    }

    void catch_eq(){
        while (true) {
            status_out->write(status);

            if(status==4)
                status=1;
            else
                status++;

            wait(); // wait for eq
        }
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
    sc_core::sc_start(1296000, sc_core::SC_SEC);
	std::cout << "Simulation finished." << std::endl;
    std::cout << "-----------------------------" << std::endl << std::endl;

    std::cout << "Calculated Average Power: "<<testbench.powerEstimation<<" W"<<std::endl;
    std::cout << "Calculated Average Energy: "<<testbench.energyEstimation<<" J"<<std::endl;
	return 0;
}


