from datetime import datetime, timedelta
import time
from urllib.parse import urljoin
import sys
import os
import re
import click
import urllib
import requests
import argparse
import signal
from pathlib import Path
from shutil import copyfile
import pkg_resources
import sseclient
from ._vendor import native_web_app

status = False
verbose = False

class bcolors:
    BACKG = '\033[48:2::45:67:90m'
    WHITE = '\033[38;5;253m '
    BOLDON = '\033[1m'
    BOLDOFF = '\033[2m'
    ENDC = '\033[0m'
    ERASE_END = '\033[K'


# Params:
#   error: [True/False/None] Report as error/info/non-status-info
def print_status(str, error=False):
    if status and (error != None):
        print("\r" + bcolors.BACKG + bcolors.WHITE + "%s" %str + \
              bcolors.ENDC +bcolors.ERASE_END, end='', flush=True)
    elif (error == True) or verbose:
        print(("Makerchip Error: " if error else "Makerchip Info: ") + str, file=sys.stderr)

def print_banner(str):
    if status:
        print(bcolors.BACKG + bcolors.WHITE + "%s" %str + \
              bcolors.ENDC +bcolors.ERASE_END, flush=True)

# Define a context manager to suppress stdout and stderr.
class suppress_stdout_stderr(object):
    '''
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    '''

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close all file descriptors
        for fd in self.null_fds + self.save_fds:
            os.close(fd)

class CloudFlareTimeoutException(Exception):
    pass

# Represents a Makerchip session.
class MakerchipSession:
    server = ""
    design = ""
    design_content = bytearray()
    http_session = requests.Session()
    proj_path = ""
    last_sync = datetime.now()
    last_mod = datetime.now()
    last_disconnect_time = time.perf_counter()
    autosave_on = False
    status = False
    verbose = False
    watch = False
    vcd = None
    wait_seconds = -1
    max_retries = -1

    def __init__(self, design, vcd, server, from_url, status, verbose, max_retries, wait_seconds):
        self.design = design
        self.status = status
        self.verbose = verbose
        self.max_retries = max_retries
        self.wait_seconds = wait_seconds
        self.vcd = vcd
        if server is None:
            self.server = "https://app.makerchip.com/"
        else:
            self.server = server

        # Create design file
        if from_url is not None:
            r = requests.get(from_url)
            self.design_content = r.content
            with open(design, 'wb+') as f:
                f.write(r.content)
        else:
            if Path(self.design).exists():
                f = open(self.design, "rb+")
                self.design_content = f.read()
                f.close()
            else:
                f = open(self.design, "wb+")
                self.design_content = pkg_resources.resource_string(__name__, "asset/default.tlv")
                f.write(self.design_content)
                f.close()

    def last_save_string(self):
        return "Last save: %s" % self.last_sync.strftime("%H:%M:%S")
        
    def auth_pub(self):
        try:
            self.http_session.get(urljoin(self.server, 'auth/pub/'))
        except:
            print_status("Error during authentication!", True)
            sys.exit(1)

    def create_public_project(self):
        f = open(self.design, "r")
        # Create backup file
        copyfile(self.design, "%s.bak" % self.design)

        if self.vcd:
            vcd = open(self.vcd, "r")
            data = {
                'name': '%s' % os.path.basename(self.design),
                'source': '%s' % (f.read()),
                'vcd': '%s' % (vcd.read()),
            }
            vcd.close
            f.close
        else:
            data = {
                'name': '%s' % os.path.basename(self.design),
                'source': '%s' % (f.read())
            }
            f.close()
        try:
            resp = self.http_session.post(urljoin(self.server, 'project/public/'), data=data)
            self.proj_path = resp.json()['path']
        except:
            print_status("Error while creating new project on server!", True)
            sys.exit(1)

    def delete_project(self):
        self.http_session.get(urljoin(self.server, 'project/public/%s/delete' % self.proj_path))

    def get_design(self):
        try:
            resp = self.http_session.get(urljoin(self.server, 'project/public/%s/contents' % self.proj_path))
            return resp.json()['value']
        except:
            print_status("Error while requesting design contents!", True)
            sys.exit(1)

    def check_conflict(self):
        if open(self.design, 'rb').read() == self.design_content:
            return False
        else:
            return True

    def save(self):
        f = open(self.design, "wb")
        f.write(self.design_content)
        f.close()

    def autosave(self):
        self.save_in_progress = True
        self.last_sync = datetime.now()
        design = self.get_design().encode('utf-8')
        if self.check_conflict():
            print_status("\nThe local file has been modified and resulted in a conflict. Exiting!", True)
            self.delete_project()
            print_status("Make sure your browser session is closed, your changes will get lost!")
            os._exit(1)
        if self.design_content != design:
            self.design_content = design
            self.last_mod = self.last_sync
        self.save()
        self.save_in_progress = False


    def listen(self):
        headers = {}
        headers['Accept'] = 'text/event-stream'
        retries = 0
        print_status("Waiting for editor to attach!")
        while retries < self.max_retries:
            wait_seconds = self.wait_seconds
            try:
                with self.http_session.get(urljoin(self.server, 'project/public/%s/desktopEvents' % self.proj_path), headers=headers, stream=True) as resp:
                    if resp.status_code != 200:
                        if resp.status_code == 524:
                            wait_seconds = 0
                            raise CloudFlareTimeoutException("Cloudflare timeout")
                        else:
                            raise Exception("Bad response from server. Code: " + str(resp.status_code))
                    client = sseclient.SSEClient(resp)
                    retries = 0
                    for event in client.events():
                        if event.data == "attach":
                            print_status("Editor attached!")
                        elif event.data == "save":
                            now = datetime.now()
                            print_status(self.last_save_string())
                            self.autosave()
                        elif event.data == "detach":
                            self.delete_project()
                            print_status("Closing local client!\n")
                            sys.exit(0)
                        elif event.data == "heartbeat":
                            print_status("Heartbeat", None)
                        else:
                            print_status("Unexpected event: " + event.data, True)
            except Exception as e:
                # Don't stress if elapsed time since last disconnect is over a minute (no delay and ignore the retry).
                now = time.perf_counter()
                stress = now - self.last_disconnect_time < 60
                if stress:
                    retries = retries + 1
                else:
                    wait_seconds = 0
                    retries = retries * 0.8  # We feel better now.
                #print_status(str(now - self.last_disconnect_time) + ", " + str(retries))
                # Do not consider CloudFlareTimeout and 0-byte read (also due to CloudFlare) to be errors.
                zero_bytes = str(e) == "('Connection broken: IncompleteRead(0 bytes read)', IncompleteRead(0 bytes read))"
                error = not (zero_bytes or isinstance(e, CloudFlareTimeoutException))
                # Reconnect if necessary.
                message = "Connection lost due to \"" + str(e) + "\"!"
                if zero_bytes and wait_seconds == 0:
                    message = "Ignoring 0-byte read error. (%s)" % self.last_save_string()
                    print_status(message)
                else:
                    # Disconnect and reconnect.
                    if wait_seconds > 0:
                        print_status(message + " Hang on...", error)
                    self.http_session.close()
                    time.sleep(wait_seconds)
                    print_status(message + " Trying to reconnect... (%s)" % self.last_save_string(), error)
                self.last_disconnect_time = time.perf_counter()
                # There's no confirmation of reconnect until a message is received, so for status, we must
                # simply assume reconnect is successful.
                print_status(self.last_save_string())
        else:
            print_status("All retries have failed. (%s)" % self.last_save_string(), True)

    def url(self):
        return (urljoin(self.server, 'sandbox/public/') + self.proj_path)


def run():
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Run Makerchip as a web application.')
    parser.add_argument('design', type=str, nargs=1, help='Design to be edited.')
    parser.add_argument('--vcd', type=str, help='Waveform for debug mode.')
    parser.add_argument('--from_url', type=str, help='Initialize design from URL.')
    parser.add_argument('--server', type=str, help='Makerchip server. (default: https://app.makerchip.com)')
    parser.add_argument('--status', action='store_true', help='Show the status bar.')
    parser.add_argument('--verbose', action='store_true', help='Report status updates to stderr (unless --status).')
    parser.add_argument('--max_retries', type=int, default=20, help='Maximum immediate retries for recovering connection.')
    parser.add_argument('--wait_seconds', type=int, default=1, help='Seconds between retry attempts.')
    args = parser.parse_args()
    global status
    global verbose
    status = args.status
    verbose = args.verbose

    # ToS check and prompt
    home = Path.home()
    file = "%s/.makerchip_accepted" % home
    if not Path(file).exists():
        # Open the app.
        with suppress_stdout_stderr():
            try:
                native_web_app.open("https://makerchip.com/terms/")
            except Exception:
                print(f"No web browser found. Please open a browser and point it to https://makerchip.com/terms/.")
        if click.confirm('Please review our Terms of Service (opened in a separate window). \
Have you read and do you accept these Terms of Service?', default=False):
            Path(file).touch()
        else:
            print("ToS must be accepted!")
            sys.exit(1)
    Path(file).touch()
    print("You have agreed to our Terms of Service here: https://makerchip.com/terms.")
    print_banner("-------------------------")
    print_banner("            ^            ")
    print_banner("        Makerchip        ")
    print_banner("            v            ")
    print_banner("-------------------------")

    # Determine if the provided design is a URL or a local file and act accordingly.
    if re.match("[a-z]+://*", args.design[0]):
        url = "https://makerchip.com/sandbox?code_url=%s" % urllib.parse.quote_plus(args.design[0])
        # Open the app.
        try:
            native_web_app.open(url)
        except Exception:
            print(f"No web browser found. Please open a browser and point it to {s.url()}.")
        print(url)
    else:
        # Initialize Makerchip session
        s = MakerchipSession(args.design[0], args.vcd, args.server, args.from_url, args.status, args.verbose, args.max_retries, args.wait_seconds)

        # Autheticate
        s.auth_pub()

        # Create a temporary project on the server
        s.create_public_project()

        # Create a signal handler and register it.
        # Used for deleting the project before exiting.
        def exit_gracefully(signum, frame):
            print_status("Deleting project from server before exiting.")
            s.save()
            s.delete_project()
            # Delete backup file
            if os.path.exists("%s.bak" % args.design[0]):
                os.remove("%s.bak" % args.design[0])
            print_status("Exited! Make sure your browser session is closed. Further changes will be lost!\n")
            sys.exit(0)

        signal.signal(signal.SIGINT, exit_gracefully)

        #Open the app.
        with suppress_stdout_stderr():
            try:
                native_web_app.open(s.url())
            except Exception:
                print(f"No web browser found. Please open a browser and point it to {s.url()}.")



        # Run autosave while the browser is running.
        s.listen()

        # Terminate script
        exit_gracefully(None, None)
if __name__ == '__main__':
    run()