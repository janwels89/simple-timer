cmake_minimum_required(VERSION 3.14)

# Simple test executable
add_executable(simple-timer-tests
    basic_test.cpp
    ../src/utils/Platform.cpp
    ../src/utils/Logger.cpp
)

target_include_directories(simple-timer-tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../include
    ${CMAKE_CURRENT_SOURCE_DIR}/../src
)

target_link_libraries(simple-timer-tests PRIVATE
    nlohmann_json::nlohmann_json
    pthread
)

add_test(NAME BasicTests COMMAND simple-timer-tests)
