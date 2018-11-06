cmake_minimum_required(VERSION 2.8)
project(mechaProtobuf)

file(GLOB PROTOS "${CMAKE_CURRENT_SOURCE_DIR}/Protos/*.proto")
protobuf_generate_python(PROTO_PY ${PROTOS})

add_custom_target(myTarget ALL DEPENDS ${PROTO_PY})

#install(TARGETS ${PROTO_PY} DESTINATION ${INSTALL_DIR}/Proto/Protos)
