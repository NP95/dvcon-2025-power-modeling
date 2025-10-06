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

# Next steps

1. Implement your strategy for the hackathon.
2. Send your model to us.

# More Information

Please visit the [guide for participants ](https://dvconchallenge.de/index.php/guide-for-participants/)at our website.
