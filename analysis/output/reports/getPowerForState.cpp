double getPowerForState(int state) {
    switch(state) {
        case 0: return 1.0357;  // At Work (In the Office)
        case 1: return 1.0215;  // Not at Work
        case 2: return 1.0284;  // At Work (Not in the office)
        case 3: return 1.0960;  // At Work (In the Office) Bluetooth
        case 4: return 1.1500;  // At Work (Not in the office) Bluetooth
        case 5: return 1.0925;  // Not at Work Bluetooth
        default: return 1.0;
    }
}
