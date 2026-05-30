# OAuth 2.0 and OpenID Connect (OIDC)

A comprehensive guide to OAuth 2.0 authorization framework and OpenID Connect authentication protocol for secure API access and user authentication.

---

## Table of Contents

1. [What are OAuth 2.0 and OIDC?](#what-are-oauth-20-and-oidc)
2. [OAuth 2.0 Fundamentals](#oauth-20-fundamentals)
3. [OAuth 2.0 Flows](#oauth-20-flows)
4. [OpenID Connect (OIDC)](#openid-connect-oidc)
5. [Tokens](#tokens)
6. [Security Considerations](#security-considerations)
7. [Real-World Examples](#real-world-examples)
8. [Interview Tips](#interview-tips)

---

# What are OAuth 2.0 and OIDC?

## What is OAuth 2.0?

**OAuth 2.0** is an authorization framework that allows applications to obtain limited access to user accounts on an HTTP service. It enables third-party applications to access user resources without exposing user credentials.

**Simple definition:** A way for applications to get permission to access your data on another service (like allowing a photo app to access your Google photos) without giving them your password.

OAuth 2.0 is about **authorization** (permission to access resources), not authentication (proving who you are).

## What is OpenID Connect (OIDC)?

**OpenID Connect (OIDC)** is an authentication layer built on top of OAuth 2.0 that adds identity information. It provides authentication (who you are) in addition to authorization (what you can access).

**Simple definition:** OAuth 2.0 tells a service "this app has permission," while OIDC also tells it "this is user John Doe."

OIDC extends OAuth 2.0 to provide **authentication** (identity) in addition to authorization.

## Key Difference

| Aspect | OAuth 2.0 | OpenID Connect |
|--------|-----------|----------------|
| **Purpose** | Authorization | Authentication + Authorization |
| **Provides** | Access tokens | ID tokens + Access tokens |
| **Use Case** | API access | User login + API access |
| **Identity** | No user identity | User identity information |

---

# OAuth 2.0 Fundamentals

## Core Concepts

### 1. Resource Owner

**What is Resource Owner?**

The resource owner is the user who owns the data and can grant access to it.

**Example:**
- User who owns photos on Google Photos
- User who owns data on their account
- The person who can authorize access

### 2. Client

**What is Client?**

The client is the application requesting access to the user's resources.

**Example:**
- Photo printing app wanting to access Google Photos
- Third-party application
- The app requesting permission

### 3. Authorization Server

**What is Authorization Server?**

The authorization server issues access tokens to clients after authenticating the resource owner and obtaining authorization.

**Example:**
- Google's OAuth server
- GitHub's OAuth server
- The server that grants tokens

### 4. Resource Server

**What is Resource Server?**

The resource server hosts the protected resources and accepts and responds to protected resource requests using access tokens.

**Example:**
- Google Photos API (hosts photos)
- GitHub API (hosts repositories)
- The API that has the data

## OAuth 2.0 Flow Overview

**Basic Flow:**
1. Client requests authorization from resource owner
2. Resource owner grants authorization
3. Client receives authorization grant
4. Client requests access token from authorization server
5. Authorization server issues access token
6. Client uses access token to access resource server

---

# OAuth 2.0 Flows

## Authorization Code Flow

### What is Authorization Code Flow?

Authorization Code flow is the most secure and commonly used OAuth 2.0 flow. It involves exchanging an authorization code for an access token.

### How it Works

**Step-by-Step:**

1. **Client Redirects User:** Client redirects user to authorization server with client ID and redirect URI
2. **User Authenticates:** User logs in to authorization server
3. **User Authorizes:** User grants permission to client
4. **Authorization Code:** Authorization server redirects back with authorization code
5. **Exchange Code:** Client exchanges authorization code for access token (server-to-server)
6. **Access Token:** Client receives access token
7. **Access Resources:** Client uses access token to access resource server

### Characteristics

**Advantages:**
- Most secure flow
- Access token never exposed to browser
- Supports refresh tokens
- Recommended for web applications

**Use Cases:**
- Web applications (server-side)
- Mobile applications
- Most common flow

### Example

```
1. User clicks "Login with Google"
2. Redirected to: https://accounts.google.com/oauth/authorize?client_id=123&redirect_uri=...
3. User logs in and authorizes
4. Redirected back: https://app.com/callback?code=AUTH_CODE
5. App exchanges code for token (server-to-server)
6. App receives access token
7. App uses token to access Google APIs
```

## Implicit Flow

### What is Implicit Flow?

Implicit flow returns the access token directly to the client in the redirect URI. It's simpler but less secure than Authorization Code flow.

### How it Works

**Step-by-Step:**

1. **Client Redirects User:** Client redirects user to authorization server
2. **User Authenticates:** User logs in
3. **User Authorizes:** User grants permission
4. **Access Token:** Authorization server redirects back with access token in URL fragment
5. **Access Resources:** Client uses access token to access resource server

### Characteristics

**Advantages:**
- Simpler (no code exchange)
- Works for single-page applications
- No server needed for token exchange

**Disadvantages:**
- Access token exposed in browser
- No refresh tokens
- Less secure
- **Deprecated** (not recommended)

**Use Cases:**
- Single-page applications (legacy)
- JavaScript applications (legacy)
- **Note:** Being replaced by Authorization Code + PKCE

## Client Credentials Flow

### What is Client Credentials Flow?

Client Credentials flow is used for machine-to-machine communication where there is no user involved. The client authenticates itself and gets an access token.

### How it Works

**Step-by-Step:**

1. **Client Authenticates:** Client sends client ID and client secret to authorization server
2. **Access Token:** Authorization server validates credentials and issues access token
3. **Access Resources:** Client uses access token to access resource server

### Characteristics

**Advantages:**
- Simple for server-to-server
- No user interaction needed
- Good for APIs

**Use Cases:**
- Server-to-server communication
- Microservices
- API-to-API calls
- Background jobs

### Example

```
1. Service A needs to call Service B's API
2. Service A sends client_id and client_secret to authorization server
3. Authorization server validates and returns access token
4. Service A uses token to call Service B's API
```

## Resource Owner Password Credentials Flow

### What is Resource Owner Password Credentials Flow?

Resource Owner Password Credentials flow allows the client to exchange username and password for an access token directly.

### How it Works

**Step-by-Step:**

1. **User Provides Credentials:** User gives username and password to client
2. **Client Requests Token:** Client sends credentials to authorization server
3. **Access Token:** Authorization server validates and issues access token
4. **Access Resources:** Client uses access token

### Characteristics

**Advantages:**
- Simple flow
- Direct credential exchange

**Disadvantages:**
- **Not recommended** (security concerns)
- Client sees user password
- Only for trusted clients
- **Deprecated** in many implementations

**Use Cases:**
- Legacy applications
- Highly trusted clients
- **Note:** Avoid if possible

---

# OpenID Connect (OIDC)

## What is OpenID Connect?

**OpenID Connect (OIDC)** extends OAuth 2.0 to provide authentication. It adds an ID token that contains user identity information.

**Simple definition:** OAuth 2.0 + User identity = OpenID Connect. It tells you not just that someone has permission, but also who they are.

## OIDC Components

### 1. ID Token

**What is ID Token?**

ID token is a JWT (JSON Web Token) that contains user identity information (who the user is).

**Contains:**
- User identifier (sub - subject)
- Issuer (who issued the token)
- Audience (who it's for)
- Expiration time
- User claims (name, email, etc.)

**Example:**
```json
{
  "sub": "user123",
  "iss": "https://accounts.google.com",
  "aud": "client_id",
  "exp": 1234567890,
  "email": "user@example.com",
  "name": "John Doe"
}
```

### 2. UserInfo Endpoint

**What is UserInfo Endpoint?**

UserInfo endpoint is an OIDC endpoint that returns user information when called with a valid access token.

**How it works:**
- Client calls UserInfo endpoint with access token
- Returns user information (name, email, etc.)
- Provides additional user claims

### 3. Claims

**What are Claims?**

Claims are pieces of information about the user (name, email, profile picture, etc.).

**Standard Claims:**
- sub (subject - user ID)
- name
- email
- picture
- etc.

**Custom Claims:**
- Application-specific user information
- Additional user attributes

## OIDC Flow

**How OIDC Works:**

1. **Authorization Request:** Same as OAuth 2.0, but with `openid` scope
2. **User Authenticates:** User logs in
3. **User Authorizes:** User grants permission
4. **Tokens Issued:** Authorization server issues both ID token and access token
5. **User Identity:** Client can extract user identity from ID token
6. **Additional Info:** Client can call UserInfo endpoint for more claims

**Key Difference from OAuth 2.0:**
- OAuth 2.0: Only access token (authorization)
- OIDC: ID token + access token (authentication + authorization)

---

# Tokens

## Access Token

### What is Access Token?

Access token is a credential that can be used to access protected resources. It represents the authorization granted to the client.

**Characteristics:**
- Short-lived (minutes to hours)
- Used to access APIs
- Contains scopes (what can be accessed)
- Opaque or JWT format

**Usage:**
```
Authorization: Bearer ACCESS_TOKEN
```

### Access Token Types

**1. Opaque Tokens:**
- Random string
- Server validates by looking it up
- More secure (can't be decoded)
- Requires database lookup

**2. JWT Tokens:**
- Self-contained (can be validated without lookup)
- Contains claims (user, scopes, expiration)
- Stateless validation
- Can be decoded (but signature verified)

## Refresh Token

### What is Refresh Token?

Refresh token is a credential used to obtain new access tokens. It's long-lived and stored securely.

**Characteristics:**
- Long-lived (days to months)
- Used to get new access tokens
- Stored securely (not in browser)
- Revocable

**Usage:**
- When access token expires
- Client uses refresh token to get new access token
- Avoids re-authentication

## ID Token (OIDC)

### What is ID Token?

ID token is a JWT containing user identity information, used in OpenID Connect.

**Characteristics:**
- JWT format
- Contains user identity
- Short-lived
- Signed by authorization server

**Usage:**
- Extract user identity
- Verify user authentication
- Get user claims

---

# Security Considerations

## Best Practices

### 1. Use HTTPS

**Why:** All OAuth/OIDC communication must use HTTPS to prevent token interception.

### 2. Secure Token Storage

**Why:** Access tokens and refresh tokens must be stored securely.

**For Web Apps:**
- Store in secure HTTP-only cookies
- Or server-side session
- Never in localStorage or JavaScript-accessible storage

**For Mobile Apps:**
- Use secure storage (Keychain, Keystore)
- Never in plain text

### 3. State Parameter

**What is State Parameter?**

State parameter is a random value used to prevent CSRF attacks.

**How it works:**
- Client generates random state
- Includes in authorization request
- Authorization server returns same state
- Client verifies state matches

**Example:**
```
Authorization: ?state=random123
Callback: ?code=ABC&state=random123
Verify: state matches
```

### 4. PKCE (Proof Key for Code Exchange)

**What is PKCE?**

PKCE is an extension to OAuth 2.0 that adds security for public clients (mobile apps, SPAs).

**How it works:**
- Client generates code verifier and challenge
- Sends challenge in authorization request
- Exchanges code with verifier
- Prevents code interception attacks

**Use Cases:**
- Mobile applications
- Single-page applications
- Public clients

### 5. Scope Limitation

**Why:** Request only the minimum scopes needed.

**Example:**
- Don't request "read all emails" if you only need "read profile"
- Principle of least privilege

### 6. Token Validation

**Why:** Always validate tokens before trusting them.

**For JWT:**
- Verify signature
- Check expiration
- Validate issuer
- Check audience

---

# Real-World Examples

## Google OAuth

**Flow:** Authorization Code
**Scopes:** profile, email, etc.
**Use Case:** "Sign in with Google"

## GitHub OAuth

**Flow:** Authorization Code
**Scopes:** repo, user, etc.
**Use Case:** Third-party apps accessing GitHub

## Facebook Login

**Flow:** Authorization Code (OIDC)
**Use Case:** "Login with Facebook"

---

# Interview Tips

## Common Questions

**Q: What is OAuth 2.0?**
- Authorization framework for third-party access
- Allows apps to access user resources without passwords
- About authorization (permission), not authentication (identity)
- Multiple flows for different use cases

**Q: What is the difference between OAuth 2.0 and OpenID Connect?**
- **OAuth 2.0:** Authorization only (what can be accessed)
- **OpenID Connect:** Authentication + Authorization (who you are + what can be accessed)
- OIDC extends OAuth 2.0 with ID tokens
- OAuth = access tokens, OIDC = ID tokens + access tokens

**Q: Explain the Authorization Code flow.**
- Most secure OAuth flow
- User redirected to authorization server
- User authorizes, gets authorization code
- Client exchanges code for access token (server-to-server)
- Access token used to access resources
- Recommended for web applications

**Q: What is the difference between access token and refresh token?**
- **Access token:** Short-lived, used to access APIs, expires quickly
- **Refresh token:** Long-lived, used to get new access tokens, stored securely
- When access token expires, use refresh token to get new one
- Avoids re-authentication

**Q: What is PKCE and why is it important?**
- Proof Key for Code Exchange
- Security extension for public clients (mobile, SPA)
- Prevents code interception attacks
- Uses code verifier and challenge
- Recommended for mobile and SPA applications

**Q: What are the security best practices for OAuth?**
- Use HTTPS for all communication
- Store tokens securely (not in browser storage)
- Use state parameter for CSRF protection
- Use PKCE for public clients
- Request minimum scopes needed
- Validate tokens properly
- Use short-lived access tokens

**Q: When would you use Client Credentials flow?**
- Machine-to-machine communication
- Server-to-server APIs
- No user involved
- Microservices communication
- Background jobs

## Key Points to Remember

- **OAuth 2.0** = Authorization framework (permission to access)
- **OpenID Connect** = Authentication + Authorization (identity + permission)
- **Authorization Code** = Most secure flow, recommended
- **Access Token** = Short-lived, used for API access
- **Refresh Token** = Long-lived, used to get new access tokens
- **ID Token** = User identity (OIDC)
- **PKCE** = Security for public clients
- **State Parameter** = CSRF protection
- **Use OAuth/OIDC** for secure third-party access, user authentication

---

## Related Topics

- [SSO](./SSO.md) - Single Sign-On using OAuth/OIDC
- [SSL-TLS-mTLS](./SSL-TLS-mTLS.md) - Secure communication for OAuth
- [API Design](./API-Design.md) - Securing APIs with OAuth
- [Security](./Security.md) - General security practices
