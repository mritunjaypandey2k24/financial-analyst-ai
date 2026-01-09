# Security Updates

## Vulnerability Fixes - January 2026

### LangChain Security Patches - Update 2

**Date**: January 9, 2026 (Second Update)

#### Additional Vulnerabilities Addressed

4. **CVE: Template Injection via Attribute Access in Prompt Templates**
   - **Component**: langchain-core
   - **Affected Version**: <= 0.3.79
   - **Fixed Version**: 0.3.81
   - **Severity**: High
   - **Description**: Template injection vulnerability allowing attackers to execute arbitrary code via attribute access in prompt templates.
   - **Action Taken**: Updated langchain-core from 0.3.27 to 0.3.81

5. **CVE: Serialization Injection Vulnerability (Secret Extraction)**
   - **Component**: langchain-core
   - **Affected Version**: < 0.3.81
   - **Fixed Version**: 0.3.81
   - **Severity**: High
   - **Description**: Serialization injection vulnerability in dumps/loads APIs could allow attackers to extract secrets or execute arbitrary code.
   - **Action Taken**: Updated langchain-core from 0.3.27 to 0.3.81

### LangChain Security Patches - Initial Update

**Date**: January 9, 2026

#### Vulnerabilities Addressed

1. **CVE: XML External Entity (XXE) Attacks**
   - **Component**: langchain-community
   - **Affected Version**: < 0.3.27
   - **Fixed Version**: 0.3.27 (now 0.3.81)
   - **Severity**: High
   - **Description**: LangChain Community was vulnerable to XML External Entity (XXE) attacks which could allow attackers to access sensitive files or perform denial of service attacks.
   - **Action Taken**: Updated langchain-community from 0.0.10 to 0.3.81

2. **CVE: SSRF Vulnerability in RequestsToolkit**
   - **Component**: langchain-community
   - **Affected Version**: < 0.0.28
   - **Fixed Version**: 0.0.28 (now 0.3.81)
   - **Severity**: High
   - **Description**: Server-Side Request Forgery vulnerability existed in RequestsToolkit component allowing unauthorized network requests.
   - **Action Taken**: Updated langchain-community from 0.0.10 to 0.3.81

3. **CVE: Pickle Deserialization of Untrusted Data**
   - **Component**: langchain-community
   - **Affected Version**: < 0.2.4
   - **Fixed Version**: 0.2.4 (now 0.3.81)
   - **Severity**: Critical
   - **Description**: Unsafe deserialization of pickle data could lead to remote code execution.
   - **Action Taken**: Updated langchain-community from 0.0.10 to 0.3.81

#### Dependencies Updated (Latest)

| Package | Previous Version | Updated Version | Reason |
|---------|-----------------|-----------------|--------|
| langchain | 0.1.0 → 0.3.27 | **0.3.81** | Latest security patches |
| langchain-community | 0.0.10 → 0.3.27 | **0.3.81** | Security patches (XXE, SSRF, pickle) |
| langchain-core | - → 0.3.27 | **0.3.81** | Security patches (template injection, serialization) |
| langchain-openai | 0.0.2 | 0.2.12 | Compatibility |
| langchain-text-splitters | - → 0.3.27 | **0.3.81** | Latest stable version |

#### Code Changes

**File: `rag_engine/text_splitter.py`**
- Updated import: `from langchain.text_splitter` → `from langchain_text_splitters`
- Reason: Module restructuring in langchain 0.3.x

**File: `agent/financial_agent.py`**
- Updated import: `from langchain.prompts` → `from langchain_core.prompts`
- Reason: Module restructuring in langchain 0.3.x

#### Security Vulnerabilities Summary

**Total Vulnerabilities Patched**: 5

1. ✅ XML External Entity (XXE) Attacks - **HIGH**
2. ✅ SSRF in RequestsToolkit - **HIGH**
3. ✅ Pickle Deserialization - **CRITICAL**
4. ✅ Template Injection via Attribute Access - **HIGH**
5. ✅ Serialization Injection (Secret Extraction) - **HIGH**

#### Testing

All modules have been updated and tested for compatibility:
- ✅ Import statements verified
- ✅ Functionality preserved
- ✅ No breaking changes to existing API
- ✅ All security vulnerabilities patched

#### Verification

To verify the security fixes:

```bash
# Check installed versions
pip list | grep langchain

# Expected output:
# langchain                     0.3.81
# langchain-community           0.3.81
# langchain-core                0.3.81
# langchain-openai              0.2.12
# langchain-text-splitters      0.3.81
```

#### Recommendations

1. **Always keep dependencies up to date**: Regularly check for security updates
2. **Use dependency scanning tools**: Consider integrating tools like Safety, Snyk, or Dependabot
3. **Pin versions in production**: Use exact versions in requirements.txt to ensure reproducibility
4. **Monitor security advisories**: Subscribe to security mailing lists for dependencies
5. **Regular security audits**: Perform monthly reviews of all dependencies

#### Additional Security Considerations

While these vulnerabilities have been patched, follow these best practices:

1. **Input Validation**: Always validate and sanitize user inputs, especially in prompt templates
2. **Least Privilege**: Run services with minimal required permissions
3. **Network Isolation**: Restrict outbound network access where possible
4. **Secure Serialization**: Avoid deserializing untrusted data when possible
5. **Template Security**: Use safe template rendering practices
6. **Monitoring**: Implement logging and monitoring for suspicious activities
7. **Regular Updates**: Keep all dependencies and the Python runtime updated

#### Impact on Financial Analyst AI

The patched vulnerabilities are particularly important for this application because:

1. **Prompt Templates**: The AI agent uses prompt templates which were vulnerable to injection attacks
2. **User Input**: The system accepts user queries which could be crafted to exploit template vulnerabilities
3. **Serialization**: ChromaDB and LangChain use serialization which could expose secrets
4. **Network Requests**: Data ingestion module makes external requests (SEC EDGAR)

All these attack vectors are now secured with the latest patches.

#### References

- LangChain Security Advisories: https://github.com/langchain-ai/langchain/security/advisories
- Python Security Best Practices: https://python.readthedocs.io/en/latest/library/security_warnings.html
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Template Injection Guide: https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/18-Testing_for_Server-side_Template_Injection

---

**Last Updated**: January 9, 2026
**Security Status**: ✅ All Known Vulnerabilities Patched
**Next Review**: Monthly security dependency review recommended
