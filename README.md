# google_access_share_bot
Telegram bot that will be sharing the accesses to documents with people allowed

#TODO add CI/CD to deploy automatically

For this 

# Working with Kamatera

1. Go to [Kamatera](https://www.kamatera.com/) and create a New Server. Choose the configuration you need

My configuration for bot:
```
Type: B
CPU: 1
RAM: 1024 MB
Hard Disk 1: 10 GB
Management Services: No
Full Daily Backup: No
Billing Cycle: Monthly
WAN Traffic: 5000GB
```

2. You should receive ip address. Using the password and login you provided open you terminal and write
```
ssh username@your_server_ip
```
3. Update and upgrade the server
```
sudo apt-get update
sudo apt-get upgrade
```
4. Install Python and Pip
```
sudo apt-get install python3
sudo apt-get install python3-pip
```
5. Transfer bot to server. If you transfer the directory dont forget about `-r` flag. 
```
scp /path/to/local/bot username@your_server_ip:/path/to/remote/bot
```
Also you can just clone the repository from Github. Do not forget to create SSH key for the server

```
ssh-keygen -t ed25519 -C "your_email@example.com"
```

6. Install the requirements
```
pip install -r requirements.txt
```

7. Run python command 
```
python3 main.py
```
Sometimes you might need to install aiogram using `pip install -U --pre aiogram`

Also you can run this command in detach mode. To dom this you need to install `screen`
```
sudo apt-get install screen
```

Then you run the python program as usual. To quit press `Ctrl-A + D`

### Working with screens

To print all your screen use
```
screen -ls
```
This command will print all sessions with their id.

To reattach the session use 
```
screen -r [session id]
```

To kill session use
```
screen -X -S [session id] quit
```