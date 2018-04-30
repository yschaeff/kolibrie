#!/usr/bin/env python3

import argparse
from collections import namedtuple

Label = namedtuple("Label", "opc len name")

L_SAMPLE = Label(0x80, 4, "Sample number")
L_MS     = Label(0x81, 4, "Time ms")
L_XUTM   = Label(0x82, 4, "x_utm")
L_YUTM   = Label(0x83, 4, "y_utm")
L_GPS1    = Label(0x84, 4, "GPS1 (+speed?)")
L_GPS2    = Label(0x85, 4, "GPS2 (+speed?)")
L_DEPTH = Label(0x86, 4, "Depth m")
L_UNK3 = Label(0x87, 4, "beam? (first is channel name?)")
L_UNK4 = Label(0x88, 4, "freq KHz")
L_UNK5 = Label(0x89, 4, "Unknown field")
L_UNK6 = Label(0x8a, 4, "Unknown field")
L_UNK7 = Label(0x8b, 4, "Unknown field")
L_UNK8 = Label(0x8c, 4, "sentlen")
L_UNK9 = Label(0x8d, 4, "Unknown field")
L_UNK10 = Label(0x8e, 4, "Unknown field")
L_UNK11 = Label(0x8f, 4, "Unknown field")

FIELDS = [ L_SAMPLE, L_MS, L_XUTM, L_YUTM, L_GPS1,
        L_GPS2, L_DEPTH, L_UNK3, L_UNK4,
        L_UNK5, L_UNK6, L_UNK7, L_UNK8,
        L_UNK9, L_UNK10, L_UNK11]
FIELD_MAP = {}
for field in FIELDS:
    FIELD_MAP[field.opc] = field


def parse_record(record):
    HEADER = b'\xc0\xde\xab!'
    p = 0
    head = record[p:p+len(HEADER)]
    p += len(HEADER)
    assert(head == HEADER)
    while True:
        opc = record[p]
        p += 1
        field = FIELD_MAP.get(opc, None)
        if field:
            data = record[p:p+field.len]
            data = int.from_bytes(data, byteorder='big')
            p += field.len
            print("FIELD '{}': {}".format(field.name, data))
        else:
            data = record[p:]
            #print("DATA ({} Bytes): {}".format(len(data), data))
            print("DATA ({} Bytes)".format(len(data)))
            break

IDXFILE = "Rec00009/B004.IDX"
SONFILE = "Rec00009/B004.SON"

Ptr = namedtuple("Ptr", "id offset")
pointers = []
with open(IDXFILE, 'rb') as f_idx:
    while True:
        r1 = f_idx.read(4)
        r2 = f_idx.read(4)
        if not r1 or not r2: break
        idx = int.from_bytes(r1, byteorder='big')
        offset = int.from_bytes(r2, byteorder='big')
        pointers.append(Ptr(idx, offset))

records = []
s = 0
with open(SONFILE, 'rb') as f_son:
    for i, ptr in enumerate(pointers):
        f_son.seek(ptr.offset)
        if i < len(pointers)-1:
            raw = f_son.read(pointers[i+1].offset - ptr.offset)
        else:
            raw = f_son.read()
        records.append(raw)
        s+=len(raw)

for record in records:
    print()
    parse_record(record)
