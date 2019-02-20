# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: navigation_data.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='navigation_data.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x15navigation_data.proto\"q\n\x08NAV_DATA\x12\x0c\n\x04roll\x18\x01 \x01(\x02\x12\r\n\x05pitch\x18\x02 \x01(\x02\x12\x0b\n\x03yaw\x18\x03 \x01(\x02\x12\r\n\x05\x64\x65pth\x18\x04 \x01(\x02\x12\x15\n\rx_translation\x18\x05 \x01(\x02\x12\x15\n\ry_translation\x18\x06 \x01(\x02\x62\x06proto3')
)




_NAV_DATA = _descriptor.Descriptor(
  name='NAV_DATA',
  full_name='NAV_DATA',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='roll', full_name='NAV_DATA.roll', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pitch', full_name='NAV_DATA.pitch', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='yaw', full_name='NAV_DATA.yaw', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='depth', full_name='NAV_DATA.depth', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='x_translation', full_name='NAV_DATA.x_translation', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='y_translation', full_name='NAV_DATA.y_translation', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
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
  serialized_start=25,
  serialized_end=138,
)

DESCRIPTOR.message_types_by_name['NAV_DATA'] = _NAV_DATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

NAV_DATA = _reflection.GeneratedProtocolMessageType('NAV_DATA', (_message.Message,), dict(
  DESCRIPTOR = _NAV_DATA,
  __module__ = 'navigation_data_pb2'
  # @@protoc_insertion_point(class_scope:NAV_DATA)
  ))
_sym_db.RegisterMessage(NAV_DATA)


# @@protoc_insertion_point(module_scope)
