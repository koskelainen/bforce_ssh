#!/usr/bin/evn python
from argparse import ArgumentParser
from asyncio import run, all_tasks, create_task, get_running_loop, gather, sleep, Queue, CancelledError
from dataclasses import dataclass
from os import environ
from pathlib import Path
from signal import SIGINT, SIGTERM, SIGHUP, Signals
from socket import error as socket_error
from sys import argv
from time import perf_counter
from typing import Iterator

from dotenv import load_dotenv
from paramiko import SSHClient, AutoAddPolicy
from paramiko import SSHException as paramiko_SSHException, AuthenticationException as paramiko_AuthenticationException

from utils import *

load_dotenv()
USERS_FILE = environ.get("USERS_FILE", None)
PASSWORDS_FILE = environ.get("PASSWORDS_FILE", None)


@dataclass
class Daemon(Singleton):
    stopping = False


@dataclass
class BaseSsh:
    __version__ = "0.1.0"
    host: str
    port: int
    username: str
    users_file: str
    passwords_file: str
    producers: int
    consumers: int
    timeout: int
    banner_timeout: int
    auth_timeout: int

    def get_users(self) -> Iterator:
        if self.username is None:
            yield from read_file(self.users_file)
        yield self.username

    def get_passwords(self) -> Iterator:
        yield from read_file(self.passwords_file)

    def check_fpath_exists(self) -> bool:
        users = self.path_exists(self.users_file)
        passwords = self.path_exists(self.passwords_file)
        if not users or not passwords:
            if not passwords:
                print(f"{err_out}{ffb}No such file or directory", self.passwords_file)
            if not users:
                print(f"{err_out}{ffb}No such file or directory", self.users_file)
            return False
        return True

    @staticmethod
    def path_exists(fpath: str) -> bool:
        return Path(fpath).absolute().exists()


def get_argument_parser() -> BaseSsh:
    use = f"\r{info_out}{ffb}python {fgb} {Path(__file__).name} {ffb}-i Host [OPTION]{sf}"
    parser = ArgumentParser(description='', usage=use)
    parser.add_argument("-np", "--nprod", default=1, type=int, dest="producers",
                        help="number of producers, read files (default 1)")
    parser.add_argument("-nc", "--ncon", default=4, type=int, dest="consumers",
                        help="number of consumers, ssh client (default 4)")
    parser.add_argument('-i', '--ip', default=None, type=str, dest='host',
                        help='ip address', required=True)
    parser.add_argument('-p', '--port', default=22, type=int, dest='port',
                        help='port ssh (default 22)')
    parser.add_argument('-u', '--user', default=None, type=str, dest='username',
                        help='ssh user name')
    parser.add_argument('-U', '--users_file', default=USERS_FILE, type=str, dest='users_file',
                        help='usernames file path')
    parser.add_argument('-P', '--passwords_file', default=PASSWORDS_FILE, type=str, dest='passwords_file',
                        help='passwords file path')
    parser.add_argument('-t', '--timeout', default=5, type=int, dest='timeout',
                        help='request timeout (default 5)')
    parser.add_argument('-bt', '--banner_timeout', default=50, type=int, dest='banner_timeout',
                        help='request banner timeout (default 50)')
    parser.add_argument('-at', '--auth_timeout', default=10, type=int, dest='auth_timeout',
                        help='request auth timeout (default 10)')

    return BaseSsh(**parser.parse_args(args=None if argv[1:] else ["--help"]).__dict__)


def read_file(filename: str, mode: str = "r") -> Iterator:
    try:
        with open(filename, mode=mode) as fd:
            for line in fd:
                yield line.strip()
    except FileNotFoundError:
        print(f"{err_out}File not found. {filename=} {sf}")
        _shutdown()
    except IOError:
        print(f"{err_out}Could not open file.  {filename=} {sf}")


async def check_ssh(
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: int,
        banner_timeout: int,
        auth_timeout: int,
) -> None:
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    try:
        ssh.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=timeout,
            banner_timeout=banner_timeout,
            auth_timeout=auth_timeout,
        )
        print(f"{info_out}{ffb}{username} : {password:.<50} {fgb}Successful{sf}")
        _shutdown()
    except paramiko_AuthenticationException:
        print(f"{ver_out}{ffb}{username} : {password:.<50} {frb}Failed{sf}")
    except socket_error:
        print(f"{err_out}{ffb}{username} : {password:.<50} {frb}Connection Failed{sf}")
    except paramiko_SSHException:
        print(f"{err_out}{ffb}{username} : {password:.<50} {frb}Error{sf}")
    finally:
        ssh.close()


async def consume(
        queue: Queue,
        host: str,
        port: int,
        timeout: int,
        banner_timeout: int,
        auth_timeout: int,
) -> None:
    daemon = Daemon()
    try:
        while not daemon.stopping:
            username, password = await queue.get()
            await sleep(0.0001)
            await check_ssh(host, port, username, password, timeout, banner_timeout, auth_timeout)
            queue.task_done()
    except CancelledError:
        _shutdown()
    except RuntimeError:
        ...


async def produce(base_ssh: BaseSsh, q: Queue) -> None:
    if not base_ssh.check_fpath_exists():
        _shutdown()
        return
    for username in base_ssh.get_users():
        for password in base_ssh.get_passwords():
            await q.put((username, password))


def _shutdown() -> None:
    tasks = all_tasks()
    Daemon().stopping = True
    for task in tasks:
        task.cancel()
    try:
        get_running_loop().close()
    except RuntimeError:
        ...


def shutdown(sig: Signals) -> None:
    print(f"{ver_out}{ffb}Received exit signal {sig.name}")
    _shutdown()


def setup_signal_handler() -> None:
    loop = get_running_loop()

    for sig in (SIGHUP, SIGTERM, SIGINT):
        loop.add_signal_handler(sig, shutdown, *[sig, ])


async def main(bssh: BaseSsh) -> None:
    setup_signal_handler()

    queue_log_pass = Queue()
    producers = [create_task(produce(bssh, queue_log_pass)) for _ in range(bssh.producers)]
    _ = [create_task(
        consume(
            queue=queue_log_pass,
            host=bssh.host,
            port=bssh.port,
            timeout=bssh.timeout,
            banner_timeout=bssh.banner_timeout,
            auth_timeout=bssh.auth_timeout,
        )) for _ in range(bssh.consumers)
    ]

    await gather(*producers)
    await queue_log_pass.join()
    _shutdown()


if __name__ == '__main__':
    start = perf_counter()
    try:
        run(main(get_argument_parser()))
    except CancelledError:
        ...
    except KeyboardInterrupt:
        print(f"{ver_out}{ffb}keyboard interrupt")
    finally:
        end = perf_counter()
        print(f"{ver_out}{ffb}{Path(__file__).name} executed in {end - start:0.2f} seconds.")
