cmake_minimum_required(VERSION 2.8)
project(mechatronics)
find_package(Protobuf REQUIRED)

set(INSTALL_DIR install)

install(DIRECTORY Sub mechOS Proto DESTINATION ${INSTALL_DIR})
add_subdirectory(Proto)
