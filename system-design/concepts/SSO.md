# Single Sign-On (SSO)

A comprehensive guide to Single Sign-On (SSO) systems, federated identity, SAML, and implementation patterns for enabling users to access multiple applications with one set of credentials.

---

## Table of Contents

1. [What is Single Sign-On?](#what-is-single-sign-on)
2. [Why Single Sign-On?](#why-single-sign-on)
3. [SSO Architecture](#sso-architecture)
4. [SAML (Security Assertion Markup Language)](#saml-security-assertion-markup-language)
5. [OAuth/OIDC for SSO](#oauthoidc-for-sso)
6. [SSO Patterns](#sso-patterns)
7. [Federated Identity](#federated-identity)
8. [Implementation Considerations](#implementation-considerations)
9. [Real-World Examples](#real-world-examples)
10. [Interview Tips](#interview-tips)

---

# What is Single Sign-On?

## What is Single Sign-On?

**Single Sign-On (SSO)** is an authentication process that allows users to access multiple applications or services with a single set of credentials (username and password). Once authenticated, users can access all authorized applications without logging in again.

**Simple definition:** Login once, access everything - like having one master key that opens all the doors in a building instead of carrying separate keys for each door.

SSO improves user experience by eliminating the need to remember and enter credentials for each application separately.

## Key Concepts

### Authentication vs. Authorization

**Authentication:** The process of verifying who a user is (proving identity).

**Authorization:** The process of determining what a user is allowed to do (permissions).

**In SSO:**
- SSO handles **authentication** (who you are)
- Each application handles **authorization** (what you can do)

### Identity Provider (IdP)

**What is Identity Provider?**

Identity Provider (IdP) is the service that authenticates users and provides identity information to other applications.

**Examples:**
- Google (for "Sign in with Google")
- Microsoft Azure AD
- Okta
- Auth0

**Role:**
- Authenticates users
- Issues identity tokens
- Manages user credentials

### Service Provider (SP)

**What is Service Provider?**

Service Provider (SP) is an application or service that relies on the Identity Provider for authentication.

**Examples:**
- Web applications using SSO
- SaaS applications
- Internal enterprise applications

**Role:**
- Receives identity information from IdP
- Grants access based on identity
- Doesn't manage credentials

---

# Why Single Sign-On?

## Problems Without SSO

**User Experience:**
- Users must remember multiple passwords
- Users must log in to each application separately
- Password fatigue and forgotten passwords
- Poor user experience

**Security:**
- Users reuse passwords across services
- Weak passwords due to too many to remember
- Password reset overhead
- Multiple attack surfaces

**Administration:**
- Multiple user directories to manage
- User provisioning/de-provisioning complexity
- Password policy enforcement across systems
- Higher IT support costs

## Benefits With SSO

**User Experience:**
- Single login for all applications
- Faster access to applications
- Better user experience
- Reduced password fatigue

**Security:**
- Centralized authentication
- Stronger password policies
- Easier to revoke access
- Reduced password-related attacks

**Administration:**
- Centralized user management
- Easier user provisioning
- Consistent security policies
- Lower IT support costs

---

# SSO Architecture

## Basic SSO Flow

### Step-by-Step Process

1. **User Accesses Application:** User tries to access Service Provider application
2. **Redirect to IdP:** Application redirects user to Identity Provider
3. **User Authenticates:** User logs in to Identity Provider
4. **Identity Assertion:** Identity Provider creates identity assertion (token)
5. **Redirect Back:** Identity Provider redirects user back to application with assertion
6. **Application Validates:** Application validates assertion with Identity Provider
7. **Access Granted:** Application grants access to user

### Architecture Diagram

```
User → Service Provider → Identity Provider
  │         │                    │
  │   1. Access app              │
  │   2. Redirect to IdP ────────▶
  │                             │
  │   3. Login                  │
  │◀────────────────────────────│
  │                             │
  │   4. Identity assertion     │
  │◀────────────────────────────│
  │         │                    │
  │   5. Validate assertion     │
  │         │                    │
  │   6. Access granted          │
```

## SSO Components

### 1. Identity Provider (IdP)

**Responsibilities:**
- User authentication
- Identity assertion creation
- Session management
- User directory management

**Examples:**
- Google
- Microsoft Azure AD
- Okta
- Auth0

### 2. Service Provider (SP)

**Responsibilities:**
- Receiving identity assertions
- Validating assertions
- Granting access
- Managing application sessions

**Examples:**
- Web applications
- SaaS applications
- Enterprise applications

### 3. User Directory

**What is User Directory?**

User directory stores user credentials and identity information.

**Examples:**
- Active Directory
- LDAP
- Database
- Cloud directories

---

# SAML (Security Assertion Markup Language)

## What is SAML?

**SAML (Security Assertion Markup Language)** is an XML-based standard for exchanging authentication and authorization data between Identity Provider and Service Provider.

**Simple definition:** A language/protocol that allows Identity Provider to tell Service Provider "this user is authenticated and here's who they are."

SAML is commonly used for enterprise SSO, especially in B2B scenarios.

## SAML Components

### 1. SAML Assertion

**What is SAML Assertion?**

SAML assertion is an XML document that contains authentication and authorization information about a user.

**Contains:**
- User identity (name, email)
- Authentication method
- Attributes (roles, groups)
- Validity period

**Example Structure:**
```xml
<saml:Assertion>
  <saml:Subject>
    <saml:NameID>user@example.com</saml:NameID>
  </saml:Subject>
  <saml:AttributeStatement>
    <saml:Attribute Name="email">
      <saml:AttributeValue>user@example.com</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

### 2. SAML Request

**What is SAML Request?**

SAML request is sent by Service Provider to Identity Provider to initiate SSO.

**Contains:**
- Request ID
- Destination (IdP URL)
- Issuer (SP identifier)

### 3. SAML Response

**What is SAML Response?**

SAML response is sent by Identity Provider to Service Provider containing the SAML assertion.

**Contains:**
- SAML assertion
- Signature
- Status

## SAML Flows

### 1. SP-Initiated SSO

**How it works:**
1. User accesses Service Provider
2. Service Provider creates SAML request
3. Redirects user to Identity Provider with request
4. User authenticates at Identity Provider
5. Identity Provider creates SAML response with assertion
6. Redirects user back to Service Provider with response
7. Service Provider validates and grants access

### 2. IdP-Initiated SSO

**How it works:**
1. User logs in to Identity Provider
2. User selects application from IdP portal
3. Identity Provider creates SAML response
4. Redirects user to Service Provider with response
5. Service Provider validates and grants access

## SAML vs OAuth/OIDC

| Aspect | SAML | OAuth/OIDC |
|--------|------|------------|
| **Format** | XML | JSON (JWT) |
| **Use Case** | Enterprise SSO | Modern web/mobile |
| **Complexity** | More complex | Simpler |
| **Protocol** | SOAP/HTTP | REST/JSON |
| **Tokens** | SAML assertions | JWT tokens |
| **Common Use** | B2B, enterprise | Consumer apps |

---

# OAuth/OIDC for SSO

## Using OAuth 2.0 for SSO

**How it works:**
- OAuth 2.0 can be used for SSO
- Identity Provider acts as authorization server
- Applications act as clients
- Access tokens used for authentication

**Limitations:**
- OAuth 2.0 is for authorization, not authentication
- Doesn't provide user identity by default

## Using OpenID Connect for SSO

**How it works:**
- OpenID Connect (OIDC) extends OAuth 2.0 for authentication
- Provides ID tokens with user identity
- Better suited for SSO than OAuth 2.0 alone

**Advantages:**
- Modern, REST-based
- JSON/JWT format (simpler than SAML)
- Good for web and mobile
- Widely adopted

**Flow:**
1. User accesses application
2. Redirected to Identity Provider (OIDC)
3. User authenticates
4. Receives ID token + access token
5. Application validates ID token
6. Grants access

## OIDC vs SAML for SSO

| Aspect | SAML | OIDC |
|--------|------|------|
| **Format** | XML | JSON |
| **Complexity** | Higher | Lower |
| **Use Case** | Enterprise | Modern apps |
| **Mobile** | Limited | Excellent |
| **Adoption** | Enterprise | Growing |

---

# SSO Patterns

## 1. Centralized SSO

**What is Centralized SSO?**

All applications use the same Identity Provider for authentication.

**Architecture:**
- Single Identity Provider
- Multiple Service Providers
- All apps trust same IdP

**Example:**
- Company uses Okta for all applications
- All apps redirect to Okta for login
- Single login works for all apps

**Advantages:**
- Simple architecture
- Centralized management
- Consistent experience

**Disadvantages:**
- Single point of failure
- Vendor lock-in

## 2. Federated SSO

**What is Federated SSO?**

Multiple Identity Providers trust each other, allowing users from one organization to access applications in another.

**Architecture:**
- Multiple Identity Providers
- Trust relationships between IdPs
- Users can access cross-organization apps

**Example:**
- Company A and Company B have trust relationship
- User from Company A can access Company B's app
- No separate account needed

**Advantages:**
- Cross-organization access
- B2B scenarios
- Reduced account management

**Disadvantages:**
- More complex
- Trust management
- Security considerations

## 3. Social SSO

**What is Social SSO?**

Using social identity providers (Google, Facebook, etc.) for authentication.

**Architecture:**
- Social IdPs (Google, Facebook, etc.)
- Applications trust social IdPs
- Users login with social accounts

**Example:**
- "Sign in with Google"
- "Login with Facebook"
- Users use existing social accounts

**Advantages:**
- User convenience
- No account creation needed
- Leverages existing accounts

**Disadvantages:**
- Dependency on social providers
- Privacy concerns
- Less control

---

# Federated Identity

## What is Federated Identity?

**Federated Identity** is an arrangement that allows users to use the same identity across multiple organizations or domains without creating separate accounts.

**Simple definition:** Your identity from one organization is trusted by another organization, so you can access their services without creating a new account.

## Federation Models

### 1. Identity Federation

**What is Identity Federation?**

Multiple organizations share identity information through trusted relationships.

**Example:**
- University students can access library resources at partner universities
- No separate account needed
- Identity from home university is trusted

### 2. Attribute Federation

**What is Attribute Federation?**

Organizations share user attributes (roles, permissions) while maintaining separate identities.

**Example:**
- User has account at Company A
- Company A shares user's role with Company B
- Company B grants access based on role
- But user still has separate identity at each

---

# Implementation Considerations

## Security Considerations

### 1. Token Security

**Why:** SSO tokens must be protected from interception and tampering.

**Best Practices:**
- Use HTTPS for all SSO communication
- Sign and encrypt tokens
- Use short token expiration
- Validate token signatures

### 2. Session Management

**Why:** SSO sessions must be properly managed and terminated.

**Best Practices:**
- Implement session timeout
- Support logout from all applications
- Monitor active sessions
- Revoke sessions on security events

### 3. Token Validation

**Why:** Applications must validate SSO tokens before trusting them.

**Best Practices:**
- Verify token signature
- Check token expiration
- Validate issuer
- Verify audience

## User Experience

### 1. Seamless Experience

**Goal:** Users should have smooth SSO experience.

**Considerations:**
- Fast redirects
- Clear error messages
- Remember user choice
- Handle edge cases

### 2. Logout

**Challenge:** Logging out from one application should log out from all (or provide choice).

**Solutions:**
- Global logout (logout from all apps)
- Per-application logout
- Session termination at IdP

---

# Real-World Examples

## Enterprise SSO

### Microsoft Azure AD

**Usage:** Enterprise SSO for Microsoft and third-party applications
**Protocol:** SAML, OIDC
**Features:** Single sign-on, multi-factor authentication, conditional access

### Okta

**Usage:** Identity and access management platform
**Protocol:** SAML, OIDC, OAuth
**Features:** SSO, user provisioning, adaptive authentication

## Consumer SSO

### Google Sign-In

**Usage:** "Sign in with Google" for web and mobile apps
**Protocol:** OpenID Connect
**Features:** Social SSO, user profile access

### Facebook Login

**Usage:** "Login with Facebook" for applications
**Protocol:** OAuth 2.0, OpenID Connect
**Features:** Social SSO, user data access

---

# Interview Tips

## Common Questions

**Q: What is Single Sign-On (SSO)?**
- Authentication process allowing access to multiple apps with one login
- User logs in once, accesses all authorized applications
- Improves user experience and security
- Centralized authentication management

**Q: What is the difference between Identity Provider and Service Provider?**
- **Identity Provider (IdP):** Authenticates users, issues identity tokens (e.g., Google, Okta)
- **Service Provider (SP):** Application that trusts IdP, grants access based on identity
- IdP = "Who you are", SP = "What you access"
- IdP authenticates, SP authorizes

**Q: What is SAML and how does it work?**
- Security Assertion Markup Language, XML-based standard for SSO
- Identity Provider creates SAML assertion (user identity)
- Service Provider validates assertion and grants access
- Commonly used for enterprise SSO, B2B scenarios

**Q: What is the difference between SAML and OIDC for SSO?**
- **SAML:** XML-based, enterprise-focused, more complex, B2B scenarios
- **OIDC:** JSON-based, modern web/mobile, simpler, REST-based
- SAML = Enterprise SSO, OIDC = Modern app SSO
- Choose based on use case and requirements

**Q: How does SSO work technically?**
- User accesses application (Service Provider)
- SP redirects to Identity Provider
- User authenticates at IdP
- IdP creates identity assertion/token
- IdP redirects back to SP with assertion
- SP validates assertion and grants access
- User can now access other apps without re-authentication

**Q: What are the security considerations for SSO?**
- Use HTTPS for all SSO communication
- Sign and encrypt tokens/assertions
- Validate tokens properly (signature, expiration, issuer)
- Implement session management and timeout
- Support secure logout
- Monitor for suspicious activity

**Q: What is federated identity?**
- Arrangement allowing same identity across multiple organizations
- Users from one org can access apps in another org
- Trust relationships between Identity Providers
- Reduces need for separate accounts

## Key Points to Remember

- **SSO** = Single login for multiple applications
- **Identity Provider** = Authenticates users, issues tokens
- **Service Provider** = Application that trusts IdP
- **SAML** = XML-based SSO protocol, enterprise-focused
- **OIDC** = JSON-based SSO protocol, modern apps
- **Federated Identity** = Identity shared across organizations
- **Security** = HTTPS, token validation, session management
- **Use SSO** for better UX, centralized auth, reduced password fatigue

---

## Related Topics

- [OAuth-OIDC](./OAuth-OIDC.md) - OAuth 2.0 and OpenID Connect for SSO
- [SSL-TLS-mTLS](./SSL-TLS-mTLS.md) - Secure communication for SSO
- [API Design](./API-Design.md) - Securing APIs with SSO
- [Security](./Security.md) - General security practices
