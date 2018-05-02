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

L_UNK12 = Label(0x50, 1, "Beam ID")
L_UNK13 = Label(0x51, 6, "Unknown field")

L_UNK14 = Label(0x53, 1, "Unknown field")
L_UNK15 = Label(0x54, 6, "Unknown field")

L_UNK16 = Label(0x56, 1, "Unknown field")
L_UNK17 = Label(0x57, 1, "Unknown field")

L_UNK18 = Label(0x98, 4, "Unknown field")
L_UNK19 = Label(0x99, 4, "Unknown field")
L_UNK20 = Label(0x9a, 4, "Unknown field")
L_UNK21 = Label(0x9b, 4, "Unknown field")
L_UNK22 = Label(0x9c, 4, "Unknown field")
L_UNK23 = Label(0x9d, 4, "Unknown field")
L_UNK24 = Label(0x9e, 4, "Unknown field")
L_UNK25 = Label(0x9f, 4, "Unknown field")
L_DATA = Label(0xa0, 4, "Data length Bytes")

L_END = Label(0x21, 0, "HEADER END")

FIELDS = [ L_SAMPLE, L_MS, L_XUTM, L_YUTM, L_GPS1,
        L_GPS2, L_DEPTH, L_UNK3, L_UNK4,
        L_UNK5, L_UNK6, L_UNK7, L_UNK8,
        L_UNK9, L_UNK10, L_UNK11,
        L_UNK12, L_UNK13, L_UNK14, L_UNK15,
        L_UNK16, L_UNK17, L_UNK18, L_UNK19,
        L_UNK20, L_UNK21, L_UNK22, L_UNK23,
        L_UNK24, L_UNK25, L_DATA, L_END]
FIELD_MAP = {}
for field in FIELDS:
    FIELD_MAP[field.opc] = field

## every record seems to start with these 4 bytes
HEADER = b'\xc0\xde\xab!'

def parse_record(record):
    p = 0 #Pointer to next byte to read

    head = record[p:p+len(HEADER)]
    p += len(HEADER)
    assert(head == HEADER)

    body = None
    bodylen = 0
    found_end = False

    print()
    while not found_end:
        opc = record[p]
        p += 1
        field = FIELD_MAP.get(opc, None)
        if field:
            rawdata = record[p:p+field.len]
            data = int.from_bytes(rawdata, byteorder='big')
            p += field.len
            print("FIELD '{:<20}' ({:02X}): {} (0x{:X})".format(field.name, field.opc, data, data, field.len))
            if field == L_DATA:
                bodylen = data
            elif field == L_END:
                found_end = True
        else:
            ## we don't know how to decode this. image data? TODO
            ## for now print length of remaining data
            print("HELP WE DON'T KNOW WHAT TO DO")
            print("DATA {} ({} Bytes)".format(opc, len(record[p:])))
            break
    body = record[p:]
    #print("BODY LEN: {}".format(len(body)))
    assert(len(body) == bodylen)
    return body


IDXFILE = "Rec00009/B004.IDX"
SONFILE = "Rec00009/B004.SON"
#IDXFILE = "R00001/B001.idx"
#SONFILE = "R00001/B001.SON"

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

bodies = [parse_record(record) for record in records]
partitions = []
last_len = 0
for body in bodies:
    l = len(body)
    if l != last_len:
        partitions.append([body])
        last_len = l
    else:
        partitions[-1].append(body)

from PIL import Image
for part in partitions:
    h = len(part)
    w = len(part[0])
    print(h, w)
    data = b''.join(part)
    #im = Image.frombytes("L", (w,h), data)
    #im.show()
