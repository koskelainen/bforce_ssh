# bforce ssh

[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)
[![python](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)

### SSH login brute force

Project for learning cyber security risks and protection measures.

### Requirements

- Python (3.10.*)
- Dependency manager `poetry`
- Dependencies `colorama`, `paramiko` and `python-dotenv`

### Tested on

- Ubuntu 22.04
- MacOS

### Install poetry

> If you have installed poetry, skip the block below!

Install poetry in Ubuntu

<details>

```bash
$ sudo apt install python3-poetry
```

Upgrade poetry in Ubuntu

```shell
sudo apt install --only-upgrade python3-poetry
```

</details>

Install poetry in MacOS

<details>

With pip

```bash
python -m pip install poetry
```
With pipx

```shell
pipx install poetry
```

Upgrade poetry in MacOS

With self poetry

```shell
poetry self update
```

With pip

```shell
python3 -m pip install -upgrade poetry
```

With pipx

```shell
pipx upgrade poetry
```
</details>

[Other way poetry installation](https://github.com/python-poetry/install.python-poetry.org)

### Download

```bash
git clone https://github.com/koskelainen/bforce_ssh.git
```

### Install modules

All dependencies are installed after the command `poetry install`

```bash
$ cd bforce_ssh/
$ poetry install
```

### Usage

`-h` or `--help ` to call help or *without arguments*

```bash
python bforce_ssh.py -h
```

help example:

```bash
$ python bforce_ssh.py
[$] python  bforce_ssh.py -i Host [OPTION]

options:
  -h, --help            show this help message and exit
  -np PRODUCERS, --nprod PRODUCERS
                        number of producers, read files (default 1)
  -nc CONSUMERS, --ncon CONSUMERS
                        number of consumers, ssh client (default 4)
  -i HOST, --ip HOST    ip address
  -p PORT, --port PORT  port ssh (default 22)
  -u USERNAME, --user USERNAME
                        ssh user name
  -U USERS_FILE, --users_file USERS_FILE
                        usernames file path
  -P PASSWORDS_FILE, --passwords_file PASSWORDS_FILE
                        passwords file path
  -t TIMEOUT, --timeout TIMEOUT
                        request timeout (default 5)
  -bt BANNER_TIMEOUT, --banner_timeout BANNER_TIMEOUT
                        request banner timeout (default 50)
  -at AUTH_TIMEOUT, --auth_timeout AUTH_TIMEOUT
                        request auth timeout (default 10)
[+] bforce_ssh.py executed in 0.00 seconds.

```

#### Brute force password of single user
	
```bash
python bforce_ssh.py -i localhost -p 22 -u admin -P data/passwords/file.txt
```

#### Brute force user and password
	
```bash
python bforce_ssh.py -i 127.0.0.1 -U data/users/file.txt -P data/passwords/file.txt
```

Run example:

```shell
$ python bforce_ssh.py -i localhost -p 22 -U data/users/file.txt -P data/passwords/file.txt
[+] test : admin............................................. Failed
[+] test : root.............................................. Failed
[+] test : toor.............................................. Failed
[+] test : raspberry......................................... Failed
[+] test : test.............................................. Failed
[+] test : uploader.......................................... Failed
[+] test : password.......................................... Failed
[+] test : administrator..................................... Failed
[+] test : marketing......................................... Failed
[+] test : 12345678.......................................... Failed
[+] test : 1234.............................................. Failed
[+] test : 12345............................................. Failed
[+] test : qwertyF........................................... Failed
[+] test : webadmin.......................................... Failed
[+] test : webmaster......................................... Failed
[+] test : maintaince........................................ Failed
[+] test : techsupport....................................... Failed
[+] test : letmein........................................... Failed
...


```


```shell
$ python bforce_ssh.py -i 127.0.0.1 -u adm1n -P data/passwords/file.txt
[$] adm1n : adm1n............................................. Successful
[+] bforce_ssh.py executed in 0.20 seconds.

```
