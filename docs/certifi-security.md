# certifi trust-bundle security update

`requirements.txt` pins certifi 2026.10.19, replacing 2024.8.30, to address
[GHSA-6q48-6c7w-9gw2](https://github.com/advisories/GHSA-6q48-6c7w-9gw2).
The reviewed advisory lists versions >=2019.03.09 and <2026.10.19 as affected.
An attacker with a compromised emSign intermediate key and an on-path network
position could intercept or modify TLS traffic from clients trusting that CA.
An affected dependency does not establish that this application was exploited.

This is the minimum patched release listed by the advisory, published on
[PyPI](https://pypi.org/project/certifi/2026.10.19/), with no new dependencies.
It removes the affected emSign ECC Root CA - G3 trust anchor while retaining a
usable CA bundle. Other, unaffected emSign roots may remain trusted. No custom
CA-store editing or disabling of certificate/hostname verification is used.
The existing Pillow/Gradio compatibility patch is retained unchanged in scope.

## Install and validate

Use the existing Python 3.11/3.12 environment setup in README. Build the Gradio
compatibility wheel before installing requirements, then run:

```sh
python -m pip install -r requirements.txt
python -m pip check
python -m pytest tests/test_certifi_security.py tests/test_pillow_compat.py -q
```

The new offline tests check the exact version/pin, absence of the affected root
fingerprint in the actual PEM bundle, successful OpenSSL bundle loading, Requests' bundle path, and an HTTPX client with
certificate and hostname verification enabled. They do not simulate an attack
or establish connectivity to every application service.

Updating source does **not** update an installed application. Rebuild/reinstall
all affected environments or container images and restart long-running processes
so existing SSL contexts load the new bundle. Verify the installed version and
`certifi.where()` in each actual runtime. Custom bundles (for example via
`REQUESTS_CA_BUNDLE` or `SSL_CERT_FILE`) need separate operator review; this
change does not replace those stores or modify system security settings. Host
SSL hooks may also append system roots even when an explicit certifi path is
used. A clean certifi bundle alone therefore does not prove that the effective
trust configuration of every host is safe.
Deployment is not performed by this patch. Other dependencies are outside this
advisory's remediation scope and are not claimed vulnerability-free.
