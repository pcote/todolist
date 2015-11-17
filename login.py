from oauth2client import client


class LoginHandler(object):
    def __init__(self, secrets_file, scope, redirect_uri):
        self.secrets_file = secrets_file
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.flow = client.flow_from_clientsecrets(secrets_file, scope=scope, redirect_uri=redirect_uri)
        self.__display_name = None
        self.__email = None

    @property
    def auth_url(self):
        url = self.flow.step1_get_authorize_url()
        return url

    def setup_user_info(self, code):
        import httplib2
        from apiclient import discovery
        creds = self.flow.step2_exchange(code)
        http_auth = creds.authorize(httplib2.Http())
        service = discovery.build("plus", "v1", http_auth)
        res = service.people().get(userId="me").execute()
        self.__email = res.get("emails")[0].get("value")
        self.__display_name = res.get("displayName")

    @property
    def email(self):
        return self.__email

    @property
    def display_name(self):
        return self.__display_name