# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: PID.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='PID.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\tPID.proto\"A\n\x03PID\x12\x13\n\x0bPID_channel\x18\x01 \x01(\x05\x12\x0b\n\x03k_p\x18\x02 \x01(\x02\x12\x0b\n\x03k_i\x18\x03 \x01(\x02\x12\x0b\n\x03k_d\x18\x04 \x01(\x02\x62\x06proto3')
)




_PID = _descriptor.Descriptor(
  name='PID',
  full_name='PID',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='PID_channel', full_name='PID.PID_channel', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='k_p', full_name='PID.k_p', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='k_i', full_name='PID.k_i', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='k_d', full_name='PID.k_d', index=3,
      number=4, type=2, cpp_type=6, label=1,
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
  serialized_start=13,
  serialized_end=78,
)

DESCRIPTOR.message_types_by_name['PID'] = _PID
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

PID = _reflection.GeneratedProtocolMessageType('PID', (_message.Message,), dict(
  DESCRIPTOR = _PID,
  __module__ = 'PID_pb2'
  # @@protoc_insertion_point(class_scope:PID)
  ))
_sym_db.RegisterMessage(PID)


# @@protoc_insertion_point(module_scope)