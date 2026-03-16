
import os

def fix_po_file(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()

    # Find the corruption point.
    # It likely starts with a sequence that indicates UTF-16LE.
    # We appended using PowerShell >>, so it might have added a BOM or just wide chars.
    
    # Let's search for the last valid line from the original part.
    # "例如：5000美元/月" in UTF-8.
    
    marker = "例如：5000美元/月".encode('utf-8')
    idx = content.find(marker)
    
    if idx == -1:
        print("Could not find marker. File might be fully corrupted or different.")
        return

    # Move past the marker and the closing quote and newline
    # msgstr "..."\n
    # The original file ended with a newline probably.
    
    # Let's try to decode the file as utf-8 up to some point, and utf-16le for the rest.
    # But checking where exactly the corruption starts is key.
    
    # We can try to split the file.
    # The appended part starts with "# Voyage Estimator" in UTF-16LE.
    # UTF-16LE for "#" is 23 00.
    # But PowerShell >> might add a newline before appending.
    
    # Let's look for the sequence corresponding to "# Voyage Estimator" in UTF-16LE.
    # b'#\x00 \x00V\x00o\x00y\x00...'
    
    append_start_sig = b'#\x00 \x00V\x00o\x00y\x00'
    
    split_idx = content.find(append_start_sig)
    
    if split_idx == -1:
        # Maybe it has a BOM?
        # BOM for UTF-16LE is FF FE
        split_idx = content.find(b'\xff\xfe')
    
    if split_idx != -1:
        print(f"Found split at {split_idx}")
        part1 = content[:split_idx]
        part2 = content[split_idx:]
        
        # Part 1 should be UTF-8 (or valid mostly)
        try:
            text1 = part1.decode('utf-8')
        except UnicodeDecodeError:
            # Maybe part1 has some garbage at the end (newlines from PowerShell?)
            # Let's try to decode ignoring errors for the very end
            text1 = part1.decode('utf-8', errors='ignore')

        # Part 2 is UTF-16LE. It might have a BOM at the start.
        # If we found BOM, part2 starts with it.
        try:
            text2 = part2.decode('utf-16le')
        except UnicodeDecodeError:
             print("Failed to decode part2 as utf-16le")
             return

        # Combine
        full_text = text1 + text2
        
        # Write back as UTF-8
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_text)
            
        print("Fixed encoding.")
        
    else:
        print("Could not find appended part signature. Trying to just read as utf-8 (might fail).")
        try:
            content.decode('utf-8')
            print("File is already valid UTF-8.")
        except:
            print("File is invalid UTF-8 and signature not found.")

if __name__ == '__main__':
    fix_po_file(r'd:\spb-expert9\locale\zh_Hans\LC_MESSAGES\django.po')
