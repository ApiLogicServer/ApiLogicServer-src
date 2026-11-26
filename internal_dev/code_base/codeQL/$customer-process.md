Customers might run CodeQL and Nexus IQ...

We run CodeQL on the code, plus pip-audit and npm audit on dependencies. We don't currently have Nexus IQ access. Can the FOSS InfoSec rep grant it, or tell us which Nexus IQ application and policy our scans run against? Our last scan (17.3.14) reported Flask-Cors 3.0.9 and openai, but a clean install of the published release shows Flask-Cors 6.0.5 and no openai. We'd like to reproduce their scan on our side to see where the difference comes from.

