cmake_minimum_required(VERSION 3.5)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})

project(testbench_dvconchallenge CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT DEFINED ENV{SYSTEMC_HOME})

    find_package(SystemCLanguage REQUIRED)

    add_executable(testbench_dvconchallenge
            src/main.cpp)
    target_link_libraries(testbench_dvconchallenge SystemC::systemc)

else()
    find_package(SystemC REQUIRED)
    add_executable(testbench_dvconchallenge 
            src/main.cpp)
    target_include_directories(testbench_dvconchallenge PUBLIC ${SystemC_INCLUDE_DIRS} ${SCV_INCLUDE_DIRS})
    target_link_directories(testbench_dvconchallenge PUBLIC ${SCV_LIBRARY_DIRS} ${SystemC_LIBRARY_DIRS})
    target_link_libraries(testbench_dvconchallenge PUBLIC ${SCV_LIBRARIES} ${SystemC_LIBRARIES})
endif()