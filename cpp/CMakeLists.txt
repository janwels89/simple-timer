cmake_minimum_required(VERSION 3.14)
project(SimpleTimer VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Options
option(BUILD_DESKTOP_MOCKS "Build with desktop mocks instead of real hardware drivers" ON)
option(BUILD_TESTS "Build tests" ON)

# Add external dependencies
include(FetchContent)

# cpp-httplib (header-only HTTP server library)
FetchContent_Declare(
    httplib
    GIT_REPOSITORY https://github.com/yhirose/cpp-httplib.git
    GIT_TAG v0.14.3
)

# nlohmann/json (header-only JSON library)
FetchContent_Declare(
    json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.3
)

# stb_image_write (header-only image writer)
FetchContent_Declare(
    stb
    GIT_REPOSITORY https://github.com/nothings/stb.git
    GIT_TAG master
)

FetchContent_MakeAvailable(httplib json stb)

# Collect source files
set(SOURCES
    src/utils/Platform.cpp
    src/utils/Logger.cpp
    src/timer/TimerController.cpp
    src/timer/TimerModes.cpp
    src/display/DisplayController.cpp
    src/input/InputController.cpp
    src/output/OutputController.cpp
    src/http/ApiServer.cpp
    src/controller/AppController.cpp
)

# Add mock or real device sources based on build type
if(BUILD_DESKTOP_MOCKS)
    list(APPEND SOURCES
        mocks/MockGPIO.cpp
        mocks/MockSH1106.cpp
    )
    add_compile_definitions(BUILD_DESKTOP_MOCKS)
else()
    list(APPEND SOURCES
        src/device/GPIO.cpp
        src/device/SH1106.cpp
    )
endif()

# Main executable
add_executable(simple-timer src/main.cpp ${SOURCES})

target_include_directories(simple-timer PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${stb_SOURCE_DIR}
)

target_link_libraries(simple-timer PRIVATE
    nlohmann_json::nlohmann_json
    httplib::httplib
    pthread
)

# Link libgpiod for Raspberry Pi builds
if(NOT BUILD_DESKTOP_MOCKS)
    find_library(GPIOD_LIBRARY gpiod REQUIRED)
    target_link_libraries(simple-timer PRIVATE ${GPIOD_LIBRARY})
endif()

# Tests
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Install targets
install(TARGETS simple-timer DESTINATION bin)
