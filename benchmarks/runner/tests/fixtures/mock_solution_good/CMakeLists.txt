cmake_minimum_required(VERSION 3.16)
project(MuonScintillator)

find_package(Geant4 REQUIRED)
include(${Geant4_USE_FILE})

include_directories(${PROJECT_SOURCE_DIR}/include)
file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)

add_executable(muonScintillator main.cc ${sources})
target_link_libraries(muonScintillator ${Geant4_LIBRARIES})
