lines = []
msgOffset = 37 # Offset to the start of the flag snippets

with open("server.log") as f:
    for line in f:
        # Only lines with a flag part
        if "FLAGPART" in line:
            # Only save the flag snippet
            lines.append(line[msgOffset:].strip())

flag = ""

for snipped in lines:
    # Only append the snippets which are not already part of the flag
    if snipped not in flag:
        flag += snipped

print(flag)
