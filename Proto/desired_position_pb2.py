# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: desired_position.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='desired_position.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x16\x64\x65sired_position.proto\"\x87\x01\n\x0b\x44\x45SIRED_POS\x12\x0c\n\x04roll\x18\x01 \x01(\x02\x12\r\n\x05pitch\x18\x02 \x01(\x02\x12\x0b\n\x03yaw\x18\x03 \x01(\x02\x12\r\n\x05\x64\x65pth\x18\x04 \x01(\x02\x12\r\n\x05x_pos\x18\x05 \x01(\x02\x12\r\n\x05y_pos\x18\x06 \x01(\x02\x12\x10\n\x08zero_pos\x18\x07 \x01(\x08\x12\x0f\n\x07pos_ref\x18\x08 \x01(\x08\x62\x06proto3')
)




_DESIRED_POS = _descriptor.Descriptor(
  name='DESIRED_POS',
  full_name='DESIRED_POS',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='roll', full_name='DESIRED_POS.roll', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pitch', full_name='DESIRED_POS.pitch', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='yaw', full_name='DESIRED_POS.yaw', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='depth', full_name='DESIRED_POS.depth', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='x_pos', full_name='DESIRED_POS.x_pos', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='y_pos', full_name='DESIRED_POS.y_pos', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='zero_pos', full_name='DESIRED_POS.zero_pos', index=6,
      number=7, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pos_ref', full_name='DESIRED_POS.pos_ref', index=7,
      number=8, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=27,
  serialized_end=162,
)

DESCRIPTOR.message_types_by_name['DESIRED_POS'] = _DESIRED_POS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DESIRED_POS = _reflection.GeneratedProtocolMessageType('DESIRED_POS', (_message.Message,), dict(
  DESCRIPTOR = _DESIRED_POS,
  __module__ = 'desired_position_pb2'
  # @@protoc_insertion_point(class_scope:DESIRED_POS)
  ))
_sym_db.RegisterMessage(DESIRED_POS)


# @@protoc_insertion_point(module_scope)
