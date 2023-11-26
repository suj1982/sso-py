from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# Replace these values with your identity provider configuration
OAUTH_PROVIDERS = {
    'google': {'client_id': 'your_google_client_id', 'client_secret': 'your_google_client_secret'},
    'github': {'client_id': 'your_github_client_id', 'client_secret': 'your_github_client_secret'}
}

oauth = OAuth(app)

for provider, config in OAUTH_PROVIDERS.items():
    oauth.register(
        name=provider,
        client_id=config['client_id'],
        client_secret=config['client_secret'],
        authorize_url=f'{provider}/authorize',
        authorize_params=None,
        authorize_kwargs=None,
        access_token_url=f'{provider}/token',
        access_token_params=None,
        access_token_kwargs=None,
        refresh_token_url=None,
        redirect_uri=f'http://localhost:5000/{provider}/callback',
        client_kwargs={'scope': 'openid profile email'}
    )


@app.route('/')
def home():
    if 'user' in session:
        return f'Hello {session["user"]["name"]}! <a href="/logout">Logout</a>'
    return 'Hello, anonymous user! <a href="/login">Login</a>'


@app.route('/login')
def login():
    return 'Login with <a href="/login/google">Google</a> or <a href="/login/github">GitHub</a>'


@app.route('/login/<provider>')
def login_provider(provider):
    return oauth.create_client(provider).authorize_redirect(url_for('authorize', _external=True))


@app.route('/login/<provider>/callback')
def authorize(provider):
    token = oauth.create_client(provider).authorize_access_token()
    user_info = oauth.create_client(provider).parse_id_token(token)
    session['user'] = {'name': user_info['name'], 'email': user_info['email']}
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
