# Security Checklist Reference

This reference provides the security assessment criteria used by the Code Analyzer skill.

## Input Validation

### Data Sanitization
- [ ] All user inputs are validated and sanitized before processing
- [ ] Input length limits are enforced to prevent buffer overflows
- [ ] Special characters are properly escaped or filtered
- [ ] Regular expressions for input validation are not vulnerable to ReDoS attacks

### SQL Injection Prevention
- [ ] Parameterized queries are used instead of string concatenation
- [ ] ORM frameworks are configured securely
- [ ] Database permissions are properly restricted
- [ ] Stored procedures are used where appropriate

### Cross-Site Scripting (XSS) Prevention
- [ ] All dynamic content is properly escaped before rendering
- [ ] Content Security Policy (CSP) headers are set appropriately
- [ ] HTML sanitization is applied to user-generated content
- [ ] Output encoding is applied based on context (HTML, JavaScript, CSS, etc.)

## Authentication and Authorization

### Password Management
- [ ] Passwords are hashed with strong algorithms (bcrypt, Argon2, etc.)
- [ ] Password complexity requirements are enforced
- [ ] Account lockout mechanisms are implemented
- [ ] Password reset tokens expire after a short time

### Session Management
- [ ] Session IDs are cryptographically random
- [ ] Session timeouts are implemented
- [ ] Session fixation attacks are prevented
- [ ] Sessions are invalidated after logout

### Access Control
- [ ] Principle of least privilege is applied
- [ ] Role-based access control (RBAC) is implemented properly
- [ ] Vertical and horizontal privilege escalation is prevented
- [ ] Sensitive operations require additional verification

## Cryptography

### Key Management
- [ ] Cryptographic keys are stored securely
- [ ] Key rotation policies are implemented
- [ ] Keys are never hardcoded in source code
- [ ] Public key infrastructure (PKI) is used for certificate management

### Encryption Standards
- [ ] Strong encryption algorithms are used (AES-256, RSA-2048+, etc.)
- [ ] Proper initialization vectors (IV) are used for block ciphers
- [ ] Encryption keys and data are handled separately
- [ ] Perfect forward secrecy is implemented where possible

## API Security

### Rate Limiting
- [ ] API rate limiting is implemented to prevent abuse
- [ ] Resource-intensive operations are limited
- [ ] DDoS protection mechanisms are in place
- [ ] Per-user and per-IP limits are configured

### Authentication
- [ ] API keys are rotated regularly
- [ ] OAuth 2.0 or OpenID Connect is used for authentication
- [ ] JWT tokens have proper expiration and refresh mechanisms
- [ ] API keys are transmitted over HTTPS only

### Data Exposure
- [ ] Sensitive data is not exposed in URLs
- [ ] API responses do not leak internal information
- [ ] Error messages do not reveal system details
- [ ] Data minimization principles are applied

## Infrastructure Security

### Network Security
- [ ] HTTPS is enforced for all communications
- [ ] TLS is configured with strong cipher suites
- [ ] Security headers are properly set (HSTS, X-Frame-Options, etc.)
- [ ] Network segmentation is implemented

### Server Security
- [ ] Server software is kept up-to-date
- [ ] Unnecessary services and ports are disabled
- [ ] File upload functionality is secured
- [ ] Server logs are monitored for security events

## Vulnerability Categories

### High-Risk Vulnerabilities
- SQL injection
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Insecure deserialization
- XML external entity (XXE) attacks

### Medium-Risk Vulnerabilities
- Broken authentication
- Sensitive data exposure
- Security misconfigurations
- Using components with known vulnerabilities
- Insufficient logging and monitoring

### Low-Risk Vulnerabilities
- Session timeouts too long
- Missing security headers
- Information disclosure in comments
- Debug information exposure

## Security Testing Procedures

### Static Analysis
1. Automated tools scan source code for known patterns
2. Manual code review of critical security functions
3. Verification of secure coding practices implementation

### Dynamic Analysis
1. Penetration testing of running applications
2. Vulnerability scanning of network interfaces
3. API security testing with tools like OWASP ZAP

### Dependency Checking
1. Regular scanning for known vulnerabilities in dependencies
2. Verification of dependency licenses
3. Removal of unused dependencies to minimize attack surface