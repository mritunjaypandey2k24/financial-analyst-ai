# Security Updates

## Vulnerability Fixes - January 2026

### LangChain Security Patches

**Date**: January 9, 2026

#### Vulnerabilities Addressed

1. **CVE: XML External Entity (XXE) Attacks**
   - **Component**: langchain-community
   - **Affected Version**: < 0.3.27
   - **Fixed Version**: 0.3.27
   - **Severity**: High
   - **Description**: LangChain Community was vulnerable to XML External Entity (XXE) attacks which could allow attackers to access sensitive files or perform denial of service attacks.
   - **Action Taken**: Updated langchain-community from 0.0.10 to 0.3.27

2. **CVE: SSRF Vulnerability in RequestsToolkit**
   - **Component**: langchain-community
   - **Affected Version**: < 0.0.28
   - **Fixed Version**: 0.0.28 (updated to 0.3.27)
   - **Severity**: High
   - **Description**: Server-Side Request Forgery vulnerability existed in RequestsToolkit component allowing unauthorized network requests.
   - **Action Taken**: Updated langchain-community from 0.0.10 to 0.3.27

3. **CVE: Pickle Deserialization of Untrusted Data**
   - **Component**: langchain-community
   - **Affected Version**: < 0.2.4
   - **Fixed Version**: 0.2.4 (updated to 0.3.27)
   - **Severity**: Critical
   - **Description**: Unsafe deserialization of pickle data could lead to remote code execution.
   - **Action Taken**: Updated langchain-community from 0.0.10 to 0.3.27

#### Dependencies Updated

| Package | Previous Version | Updated Version | Reason |
|---------|-----------------|-----------------|--------|
| langchain | 0.1.0 | 0.3.27 | Compatibility with patched versions |
| langchain-community | 0.0.10 | 0.3.27 | Security patches for XXE, SSRF, and pickle deserialization |
| langchain-core | - | 0.3.27 | Required by updated langchain |
| langchain-openai | 0.0.2 | 0.2.12 | Compatibility with langchain 0.3.27 |
| langchain-text-splitters | - | 0.3.27 | Required by updated langchain |

#### Code Changes

**File: `rag_engine/text_splitter.py`**
- Updated import: `from langchain.text_splitter` → `from langchain_text_splitters`
- Reason: Module restructuring in langchain 0.3.x

**File: `agent/financial_agent.py`**
- Updated import: `from langchain.prompts` → `from langchain_core.prompts`
- Reason: Module restructuring in langchain 0.3.x

#### Testing

All modules have been updated and tested for compatibility:
- ✅ Import statements verified
- ✅ Functionality preserved
- ✅ No breaking changes to existing API
- ✅ Security vulnerabilities patched

#### Verification

To verify the security fixes:

```bash
# Check installed versions
pip list | grep langchain

# Expected output:
# langchain                     0.3.27
# langchain-community           0.3.27
# langchain-core                0.3.27
# langchain-openai              0.2.12
# langchain-text-splitters      0.3.27
```

#### Recommendations

1. **Always keep dependencies up to date**: Regularly check for security updates
2. **Use dependency scanning tools**: Consider integrating tools like Safety, Snyk, or Dependabot
3. **Pin versions in production**: Use exact versions in requirements.txt to ensure reproducibility
4. **Monitor security advisories**: Subscribe to security mailing lists for dependencies

#### Additional Security Considerations

While these vulnerabilities have been patched, follow these best practices:

1. **Input Validation**: Always validate and sanitize user inputs
2. **Least Privilege**: Run services with minimal required permissions
3. **Network Isolation**: Restrict outbound network access where possible
4. **Monitoring**: Implement logging and monitoring for suspicious activities
5. **Regular Updates**: Keep all dependencies and the Python runtime updated

#### References

- LangChain Security Advisories: https://github.com/langchain-ai/langchain/security/advisories
- Python Security Best Practices: https://python.readthedocs.io/en/latest/library/security_warnings.html
- OWASP Top 10: https://owasp.org/www-project-top-ten/

---

**Last Updated**: January 9, 2026
**Next Review**: Monthly security dependency review recommended
