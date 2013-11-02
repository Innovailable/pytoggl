import base64
import json

from requests import Request, Session
from requests.auth import HTTPBasicAuth

# actual api calls

API_BASE = "https://www.toggl.com/api/v8/"

def api_call(method, path, params, user, password):
    if isinstance(path, str):
        url = API_BASE + path
    else:
        url = API_BASE + '/'.join(str(el) for el in path)

    print(url)

    auth = HTTPBasicAuth(user, password)

    session = Session()
    request = Request(method, url, data=params, auth=auth)

    prepared = request.prepare()

    response = session.send(prepared)

    if response.status_code < 300:
        return json.loads(response.text)
    else:
        print(response.status_code)
        print(response.text)
        return None

# some helpers

class MethodHelper:

    def _get(self, path=None, params={}):
        return self._call('GET', path, params)

    def _post(self, path=None, params={}):
        return self._call('POST', path, params)

    def _put(self, path=None, params={}):
        return self._call('PUT', path, params)

    def _delete(self, path=None, params={}):
        return self._call('DELETE', path, params)

class TogglItem(MethodHelper):

    def __init__(self, toggl, root):
        self.toggl = toggl
        self.root = root

    def _call(self, method, path, params):
        if path == None:
            abs_path = self.root
        elif isinstance(path, str):
            abs_path = self.root + [path]
        else:
            abs_path = self.root + path

        return self.toggl._call(method, abs_path, params)

# entrance to api

class Toggl(MethodHelper):

    def __init__(self, api_token):
        self.api_token = api_token

    def _call(self, method, path, params):
        return api_call(method, path, params, self.api_token, "api_token")

    def me(self):
        return self._get("me")

    def workspaces(self):
        raw = self._get('workspaces')

        return [Workspace(workspace, self) for workspace in raw]

# classes used by the api

class Workspace(TogglItem):

    def __init__(self, raw, toggl):
        TogglItem.__init__(self, toggl, ['workspaces', raw['id']])
        self.raw = raw

    def name(self):
        return self.raw['name']

    def projects(self):
        raw = self._get('projects')
        return [Project(project, self.toggl) for project in raw]

class Project(TogglItem):

    def __init__(self, raw, toggl):
        TogglItem.__init__(self, toggl, ['projects', raw['id']])
        self.raw = raw

    def name(self):
        return self.raw['name']

    def workspace(self):
        # TODO: this does not work with the current API!
        raw = self.toggl._get(['worksapaces', self.raw['wid']])
        return Workspace(raw, self.toggl)

