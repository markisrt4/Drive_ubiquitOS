# OAuth

The `oauth` protocol component provides reusable OAuth 2.0 and PKCE functionality.

It includes:

- OAuth client configuration
- Authorization URL construction
- PKCE verifier and challenge generation
- Authorization code exchange
- Access token refresh
- OAuth token types
- OAuth token store interface
- Local redirect callback handling

Provider-specific URLs, scopes, configuration, and behavior should remain in provider-specific protocol components.

## OAuth Client

The `OAuthClient` communicates with OAuth authorization and token endpoints.

It can:

- Build authorization URLs
- Exchange authorization codes for tokens
- Refresh access tokens

## PKCE

The `create_pkce_pair()` function generates:

- A PKCE code verifier
- A SHA-256 code challenge
- The `S256` challenge method

## OAuth Tokens

The `OAuthTokens` type contains:

- Access token
- Refresh token
- Expiration time
- Token type
- Scope

The `is_expired()` method can be used to determine whether an access token should be refreshed.

## Token Storage

`OAuthTokenStoreIf` defines the interface for token storage implementations.

Token storage implementations are responsible for:

- Loading tokens
- Saving tokens
- Clearing tokens

The OAuth protocol component does not prescribe a specific storage format or location.

## Redirect / Callback Server

`OAuthRedirectServer` receives a single OAuth redirect callback through a local HTTP server.

It extracts values such as:

- Authorization code
- State
- Error
- Error description

## Component Test

A CLI component test is provided in the `component_test` directory.

```text
oauth/
├── __init__.py
├── oauth_redirect_server.py
├── oauth_client.py
├── oauth_token_store_if.py
├── oauth_types.py
├── pkce.py
├── README.md
└── component_test/
    ├── __init__.py
    └── oauth_cli.py
```

Run the component test from the project root:

```bash
python3 -m protocols.oauth.component_test.oauth_cli
```

The test generates a PKCE verifier, challenge, state value, and example authorization URL.

Scopes can be supplied using repeated `--scope` arguments:

```bash
python3 -m protocols.oauth.component_test.oauth_cli \
    --scope user-read-playback-state \
    --scope user-modify-playback-state
```

Provider endpoint values can also be supplied:

```bash
python3 -m protocols.oauth.component_test.oauth_cli \
    --client-id example-client \
    --authorization-url https://example.com/authorize \
    --token-url https://example.com/token \
    --redirect-uri http://127.0.0.1:8888/callback
```

The component test does not contact an OAuth provider or exchange real tokens.

## Design

The OAuth component contains provider-independent OAuth behavior.

Provider-specific endpoints, scopes, token storage implementations, and authorization policies should be defined outside this component.
