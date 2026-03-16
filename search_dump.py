
with open('sol_dump.html', 'rb') as f:
    content = f.read()
    # Try decoding as gb18030
    text = content.decode('gb18030', errors='ignore')
    
    if 'detail' in text or 'show.asp' in text:
        print("Found 'detail' or 'show.asp'!")
        lines = text.split('\n')
        for line in lines:
            if 'detail' in line or 'show.asp' in line:
                print(line.strip())
    else:
        print("Not found.")
