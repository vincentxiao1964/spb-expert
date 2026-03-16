#! /usr/bin/env python3
# Written by Martin v. Löwis <loewis@informatik.hu-berlin.de>

import struct
import sys
import ast

def generate_mo(po_file, mo_file):
    messages = {}
    
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    section = None
    msgid = b''
    msgstr = b''

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.startswith('msgid '):
            if section == 'msgstr':
                messages[msgid] = msgstr
                msgid = b''
                msgstr = b''
            section = 'msgid'
            try:
                s = line[6:].strip()
                msgid += ast.literal_eval(s).encode('utf-8')
            except:
                pass 
        elif line.startswith('msgstr '):
            section = 'msgstr'
            try:
                s = line[7:].strip()
                msgstr += ast.literal_eval(s).encode('utf-8')
            except:
                pass
        elif line.startswith('"'):
            try:
                s = ast.literal_eval(line)
                if section == 'msgid':
                    msgid += s.encode('utf-8')
                elif section == 'msgstr':
                    msgstr += s.encode('utf-8')
            except:
                pass

    if section == 'msgstr':
        messages[msgid] = msgstr

    keys = sorted(messages.keys())
    offsets = []
    ids = b''
    strs = b''
    
    for id in keys:
        msg = messages[id]
        o_off = len(ids)
        ids += id + b'\0'
        o_len = len(id)
        t_off = len(strs)
        strs += msg + b'\0'
        t_len = len(msg)
        offsets.append((o_len, o_off, t_len, t_off))

    magic = 0x950412de
    revision = 0
    nstrings = len(keys)
    off_o_table = 28
    off_t_table = 28 + nstrings * 8
    start_data = off_t_table + nstrings * 8
    
    with open(mo_file, 'wb') as f:
        f.write(struct.pack('<I', magic))
        f.write(struct.pack('<I', revision))
        f.write(struct.pack('<I', nstrings))
        f.write(struct.pack('<I', off_o_table))
        f.write(struct.pack('<I', off_t_table))
        f.write(struct.pack('<I', 0))
        f.write(struct.pack('<I', 0))
        
        for o_len, o_off, t_len, t_off in offsets:
            f.write(struct.pack('<II', o_len, start_data + o_off))
            
        for o_len, o_off, t_len, t_off in offsets:
            f.write(struct.pack('<II', t_len, start_data + len(ids) + t_off))
            
        f.write(ids)
        f.write(strs)

    print(f"Compiled {len(keys)} messages to {mo_file}")

if __name__ == '__main__':
    if len(sys.argv) == 3:
        generate_mo(sys.argv[1], sys.argv[2])
    else:
        generate_mo(r'd:\spb-expert9\locale\zh_Hans\LC_MESSAGES\django.po', r'd:\spb-expert9\locale\zh_Hans\LC_MESSAGES\django.mo')
