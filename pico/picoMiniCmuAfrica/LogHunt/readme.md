# Write-Up: Log Hunt

This write-up will walk you through my thought process on the challenge and the decisions I made. I hope you will learn a thing or two!

## Basic Information

- CTF: picoMini CMU-Africa
- Category: General Skills
- Difficulty: Easy

## Description

Our server seems to be leaking pieces of a secret flag in its logs. The parts are scattered and sometimes repeated. Can you reconstruct the original flag?

Download the logs and figure out the full flag from the fragments.

## Approach

At first we download the provided log file and check with `file` what it is to get a first impression.

```bash
wget https://challenge-files.picoctf.net/.../server.log

file server.log
server.log: ASCII text
```

So just a plain text log file. The next step is to simply open it and look at it.

```bash
cat server.log
[1990-08-09 10:00:10] INFO FLAGPART: picoCTF{us3_
[1990-08-09 10:00:16] WARN Disk space low
[1990-08-09 10:00:19] DEBUG Cache cleared
[1990-08-09 10:00:23] WARN Disk space low
[1990-08-09 10:00:25] INFO Service restarted
```

We see a log entry containing a part of the flag. But how many lines do we actually have to go through?

```bash
cat server.log | wc -l
2348
```

So scrolling and finding the flag parts manually is not really practical with 2348 lines. Let's find just the lines containing a `FLAGPART`.

```bash
grep FLAGPART server.log
[1990-08-09 10:00:10] INFO FLAGPART: picoCTF{us3_
[1990-08-09 10:02:55] INFO FLAGPART: y0urlinux_
[1990-08-09 10:05:54] INFO FLAGPART: sk1lls_
[1990-08-09 10:05:55] INFO FLAGPART: sk1lls_
[1990-08-09 10:10:54] INFO FLAGPART: cedfa5fb}
[1990-08-09 10:10:58] INFO FLAGPART: cedfa5fb}
[1990-08-09 10:11:06] INFO FLAGPART: cedfa5fb}
[1990-08-09 11:04:27] INFO FLAGPART: picoCTF{us3_
...
```

We find the flag split across multiple flag parts, which again occur multiple times. But they are in the correct order, it seems.

For solving the challenge, we now know:
- The flag is split into multiple parts
- Parts are repeated multiple times
- We need to extract and combine them in the correct order

We could copy and paste the flag parts together into one flag and be done. But since this would be manual, let's automate it and write a small Python script that does that for us.

For the script, we need to know the offset in the line where the part starts. We check how long the prefix is, since it is the same for all lines.

```bash
echo "[1990-08-09 10:00:10] INFO FLAGPART: " | wc -m
38
```

So the flag part starts after character 38. In the script we use `37`, since indexing starts at 0.

The script does the following:
- read in only the lines containing `FLAGPART`
- only take the flag content of it
- concatenate line by line, but only parts that are not already contained in the result flag → no duplicates

### Final Script

```python
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
```

### Console Output

```text
picoCTF{...}
```

## Takeaway

When we deal with large log files, always look for anomalies and patterns first and reduce the data using tools like `grep`. Once the structure is clear, scripting the solution is often faster and more reliable than manual work.