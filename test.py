from wsgiref.simple_server import make_server
import oauth2
import oauth2.grant
import oauth2.error
import oauth2.store.memory
import oauth2.tokengenerator
import oauth2.web

class ExampleSiteAdapter(oauth2.web.SiteAdapter):
    def authenticate(self, request, environ, scopes):
        if request.post_param('confirm') == 'confirm':
            return {}
        raise oauth2.error.UserNotAuthenticated

    def render_auth_page(self, request, response, environ, scopes):
        response.body = '''
        <html>
            <body>
                <form method="POST" name="confirmation_form">
                    <input type="submit" name="confirm" value="confirm" />
                    <input type="submit" name="deny" value="deny" />
                </form>
            </body>
        </html>'''
        return response

    def user_has_denied_access(self, request):
        if request.post_param('deny') == 'deny':
            return True
        return False

client_store = oauth2.store.memory.ClientStore()
client_store.add_client(client_id='abc', client_secret='xyz', redirect_uris=['http://localhost/callback'])

token_store = oauth2.store.memory.TokenStore()

auth_controller = oauth2.Provider(
    access_token_store = token_store,
    auth_code_store = token_store,
    client_store = client_store,
    site_adapter = ExampleSiteAdapter(),
    token_generator = oauth2.tokengenerator.Uuid4()    
)

auth_controller.add_grant(oauth2.grant.AuthorizationCodeGrant())
auth_controller.add_grant(oauth2.grant.ImplicitGrant())

auth_controller.add_grant(oauth2.grant.RefreshToken(expires_in=2592000))
app = oauth2.web.Wsgi(server=auth_controller)

if __name__ == '__main__':
    httpd = make_server('', 8080, app)
    httpd.serve_forever()
