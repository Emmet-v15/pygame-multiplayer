import colorama

disabled = False

class Logger:
    def __init__(self, name):
        self.name = name

    def disable():
        global disabled
        disabled = True

    def log(self, msg):
        if disabled:
            return
        print(f"{colorama.Fore.GREEN}[INFO] {self.name}: {msg}{colorama.Fore.RESET}")

    def warn(self, msg):
        if disabled:
            return
        print(f"{colorama.Fore.YELLOW}[WARN] {self.name}: {msg}{colorama.Fore.RESET}")

    def error(self, msg):
        if disabled:
            return
        print(f"{colorama.Fore.RED}[ERROR] {self.name}: {msg}{colorama.Fore.RESET}")

    def debug(self, msg):
        if disabled:
            return
        print(f"{colorama.Fore.BLUE}[DEBUG] {self.name}: {msg}{colorama.Fore.RESET}")

    def critical(self, msg):
        if disabled:
            return
        print(f"{colorama.Fore.MAGENTA}[CRITICAL] {self.name}: {msg}{colorama.Fore.RESET}")