# Security Policy

## Supported Versions

Currently supported versions of the Ambient Sound Synthesizer integration:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by:

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Email the maintainer directly at the contact information in the GitHub profile
3. Include detailed information about the vulnerability:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

You can expect:
- Acknowledgment of your report within 48 hours
- Regular updates on the progress of addressing the vulnerability
- Credit for responsible disclosure (if desired) once the issue is resolved

## Security Practices

### API Key Management

This integration requires users to provide their own Freesound API key. Here's how we handle API keys securely:

#### ✅ What We Do:

1. **No Hardcoded Keys**: We never include API keys, tokens, or credentials in the source code
2. **Secure Storage**: API keys are stored using Home Assistant's encrypted configuration entry system
3. **User-Provided**: Users obtain their own API keys from Freesound (https://freesound.org/apiv2/apply/)
4. **Validation**: Keys are validated during setup to ensure they're correct before storing
5. **No Logging**: API keys are never logged in plaintext

#### ✅ What Users Should Do:

1. **Keep Your Key Private**: Never share your Freesound API key publicly
2. **Use Free Tier Wisely**: The free tier provides 5,000 requests/month - monitor your usage
3. **Regenerate If Compromised**: If you believe your key has been exposed, regenerate it at Freesound
4. **Review API Quota**: Regularly check your API usage at https://freesound.org/

### Secure Coding Practices

This integration follows these security best practices:

1. **Input Validation**: All user inputs are validated before processing
2. **URL Validation**: Audio URLs are validated to ensure they come from trusted Freesound CDN
3. **No Arbitrary Code Execution**: No `eval()` or similar dangerous functions are used
4. **HTTPS Only**: All API communications use HTTPS
5. **Error Handling**: Errors are logged without exposing sensitive information

### Audio Content Security

1. **Freesound CDN Only**: Audio files are only loaded from the official Freesound CDN (`https://cdn.freesound.org/`)
2. **No User Uploads**: This integration does not accept user-uploaded audio files
3. **Read-Only Access**: The integration only reads from Freesound's API, never writes or modifies data

## Dependencies

This integration has minimal dependencies:
- `aiohttp>=3.8.0` - Used for HTTP requests

We regularly monitor these dependencies for security vulnerabilities.

## Security Audit

A comprehensive security audit was performed on January 10, 2026. Results are documented in `SECURITY_AUDIT.md`. Key findings:

- ✅ No hardcoded secrets found
- ✅ Secure API key management
- ✅ Clean git history
- ✅ No sensitive files in repository

## Best Practices for Contributors

If you're contributing to this project:

1. **Never Commit Secrets**: Never commit API keys, tokens, passwords, or credentials
2. **Use `.gitignore`**: Ensure sensitive files are in `.gitignore`
3. **Review Before Pushing**: Always review your changes before pushing
4. **Test Keys Separately**: Use test API keys that are different from production keys
5. **Follow Code Review**: All changes go through code review before merging

## Vulnerability Disclosure Timeline

When a vulnerability is reported:

1. **Day 0**: Vulnerability reported and acknowledged
2. **Day 1-7**: Vulnerability assessed and fix developed
3. **Day 7-14**: Fix tested and deployed
4. **Day 14+**: Public disclosure (coordinated with reporter)

## Contact

For security concerns, please contact the project maintainer:
- GitHub: @ABWilliamsn
- GitHub Issues (for non-security bugs): https://github.com/ABWilliamsn/Ambient-Sound-Synthesizer/issues

## License

This security policy is part of the Ambient Sound Synthesizer project and is licensed under the same terms as the project itself.
