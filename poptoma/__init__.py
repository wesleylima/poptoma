from urllib import parse
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class OptomaSession():
    """Session that re-logs in if the session expires"""

    def __init__(self, base_url, username, password):
        self.session = requests.session()
        self.base_url = 'http://' + base_url # http://192.168.1.245/
        self.username = username
        self.password = password
        if not self._login():
            # Could not log in, so we don't have a valid session
            # We can only assume wrong username or password (good assumption)
            # The web UI doesn't actually provide useful information,
            # just a redirect to the login page again.
            # TODO: Make this a better exception
            raise Exception()

    def _login(self):
        response = self.session.get(parse.urljoin(self.base_url, '/login.htm'))
        # TODO: Catch the HTTPConnectionPool exception more gracefully.
        # TODO: This happens when the wrong host is provided to the API or projector is disconnected from the network
        html = BeautifulSoup(response.text, 'html.parser')
        challenge_element = html.find('input', {'name': 'Challenge'})
        if not challenge_element:
            # We're probably hit a http server that is not our projector
            # (or something is broken with the projectors web ui)
            # TODO: Handle this exception more specifically?
            return False

        challenge = challenge_element['value']
        login_str = self.username+self.password+challenge
        response = hashlib.md5(login_str.encode())

        data = {
            'user': 0,
            'Username': '1',
            'Password': '',
            'Challenge': '',
            'Response': response.hexdigest(),
        }
        response = self.session.post(parse.urljoin(self.base_url, '/tgi/login.tgi'), data)
        if self._needs_login(response):
            # Log in failed
            return False

        # Log in successful
        return True

    def _needs_login(self, response):
        # Handle errors
        if response.status_code != 200:
            raise requests.RequestException(request=request, response=response)

        html = BeautifulSoup(response.text, 'html.parser')
        # If we get the login frame then we need to log in
        login_frame = html.find("frame", {"src": "/login.htm"})
        return True if login_frame else False

    def _full_path(self, path):
        return parse.urljoin(self.base_url, path)

    def get(self, path):
        #tries the get
        response = self.session.get(self._full_path(path))

        # If we get the login frame then we need to log in
        if self._needs_login(response):
            #Try the request again
            self._login()
            response = self.session.get(self._full_path(path))

        return response


    def post(self, path, payload):
        #tries the post
        response = self.session.post(self._full_path(path), payload)

        if self._needs_login(response):
            #Try the request again
            self._login()
            response = self.session.post(self._full_path(path), payload)

        return response

class Projector():
    """An Optoma Projector"""
    def __init__(self, host, username, password):
        self._power_status = None # false is off, true is on, None is unknown
        self._latest_power_status_change = datetime.now()
        self.session = OptomaSession(host, username, password) # TODO: catch session password exception

    def power_status(self):
        """Get the latest state from the projector."""
        # Wait a bit to make sure the UI has the latest power state if we just triggered a status change
        # TODO: Make timedelta dynamic based on which command was executed (power on seems to take longer to 'stick' than power off)
        if (self._power_status is not None and \
            datetime.now() - self._latest_power_status_change < timedelta(seconds=30)): # Yeah... it can take up to 30 sec for the power on status to register
            return self._power_status

        # Status is stale from last time we took action. Let's get a fresh one from the UI
        response = self.session.get('/control.htm')
        html = BeautifulSoup(response.text, 'html.parser')
        power_status = int(html.find("input", {"id": "pwr"})['value'])
        if power_status == 1:
            self._power_status = True
        else:
            self._power_status = False

        return self._power_status


    def turn_on(self):
        """Turn the projector on."""

        on_command = {
            'btn_powon': 'Power On'
        }
        self.session\
            .post('/tgi/control.tgi', on_command)

        self._set_power_status(True)

    def _set_power_status(self, status):
        """This only changes the objects stauts. It doesn't affect the device itself and makes to http calls"""
         # false is off, true is on
        if self._power_status != status:
            self._power_status = status
            self._latest_power_status_change = datetime.now()


    def turn_off(self):
        """Turn the projector off."""

        off_command = {
            'btn_powoff': 'Power Off'
        }
        self.session.post('/tgi/control.tgi', off_command)

        self._set_power_status(False)
