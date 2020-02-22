"""Authenticating HTTP Server

This module builds on BaseHTTPServer and implements basic authentication

"""

import base64
from http.client import responses
import six.moves.BaseHTTPServer


DEFAULT_AUTH_ERROR_MESSAGE = b"""
<head>
<title>%(code)d - %(message)b</title>
</head>
<body>
<h1>Authorization Required</h1>
this server could not verify that you
are authorized to access the document
requested.  Either you supplied the wrong
credentials (e.g., bad password), or your
browser doesn't understand how to supply
the credentials required.
</body>"""


def _quote_html(html):
    return html.replace(b"&", b"&amp;").replace(b"<", b"&lt;").replace(b">", b"&gt;")


class AuthRequestHandler(six.moves.BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Simple handler that can check for auth headers

    In your subclass you have to define the method get_userinfo(user, password)
    which should return 1 or None depending on whether the password was
    ok or not. None means that the user is not authorized.
    """

    # False means no authentiation
    DO_AUTH = 1

    def parse_request(self):
        if not six.moves.BaseHTTPServer.BaseHTTPRequestHandler.parse_request(self):
            return False

        if self.DO_AUTH:
            authorization = self.headers.get('Authorization', '')
            if not authorization:
                self.send_autherror(401, b"Authorization Required")
                return False
            scheme, credentials = authorization.split()
            if scheme != 'Basic':
                self.send_error(501)
                return False
            credentials = base64.decodebytes(credentials.encode()).decode()
            user, password = credentials.split(':')
            authcheck = self.get_userinfo(user, password, self.command)
            if isinstance(authcheck, bool):
                return authcheck
            if isinstance(authcheck, int):
                self.send_autherror(authcheck, bytes(responses[authcheck], encoding='utf8'))
            return False
        return True

    def send_autherror(self, code, message=None):
        """Send and log an auth error reply.

        Arguments are the error code, and a detailed message.
        The detailed message defaults to the short entry matching the
        response code.

        This sends an error response (so it must be called before any
        output has been generated), logs the error, and finally sends
        a piece of HTML explaining the error to the user.

        """
        try:
            short, long = self.responses[code]
        except KeyError:
            short, long = b'???', b'???'
        if message is None:
            message = short
        explain = long
        self.log_error("code %d, message %s", code, message)

        # using _quote_html to prevent Cross Site Scripting attacks (see bug
        # #1100201)
        content = (self.error_auth_message_format % {b'code': code, b'message':
                   _quote_html(message), b'explain': explain})
        self.send_response(code, message)
        self.send_header('Content-Type', self.error_content_type)
        self.send_header('WWW-Authenticate', 'Basic realm="PyWebDAV"')
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(content)

    error_auth_message_format = DEFAULT_AUTH_ERROR_MESSAGE

    def get_userinfo(self, user, password, command):
        """Checks if the given user and the given
        password are allowed to access.
        """
        # Always reject
        return None
