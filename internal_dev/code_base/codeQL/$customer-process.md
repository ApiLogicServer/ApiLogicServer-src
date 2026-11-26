
## Customer perspective

Customers might run CodeQL and Nexus IQ...

## Product Note

We run CodeQL on the code, plus pip-audit and npm audit on dependencies. We don't currently have Nexus IQ access. Can the FOSS InfoSec rep grant it, or tell us which Nexus IQ application and policy our scans run against? Our last scan (17.3.14) reported Flask-Cors 3.0.9 and openai, but a clean install of the published release shows Flask-Cors 6.0.5 and no openai. We'd like to reproduce their scan on our side to see where the difference comes from.

## More Customer Note

Nexus IQ is proprietary from Sonatype:  check alternative OWASP Dependency-Check is a free, open-source Software Composition Analysis (SCA) tool that identifies known vulnerabilities in a project’s third-party dependencies.

It is an OWASP Flagship project (started in 2012) maintained under the Apache 2.0 license. Its main purpose is to help address the OWASP Top 10 risk of “Using Components with Known Vulnerabilities” (now often listed as Vulnerable and Outdated Components).

## Product Option

Dependency-Check fills the same role as Nexus IQ, but it won't reproduce FedEx's Sonatype results.

Overlap: We already run pip-audit for Python and npm audit for the 14 React skeletons. Dependency-Check is a third source on the same ground.

Different data: It matches packages to CVEs through CPE identifiers against the NVD, while Sonatype uses its own proprietary vulnerability data. The two will disagree in both directions. Dependency-Check is known for false positives from CPE matching, and it can miss advisories that only the Python and npm advisory databases carry.
Flask-Cors 3.0.9 and openai puzzle: Their scan flagged them although the 17.3.14 release installs Flask-Cors 6.0.5 and no openai. Dependency-Check can show whether a free scanner also sees them. It cannot tell us why Sonatype did.

Setup: It needs Java and a first-run NVD database download, which is slow without a free NVD API key.
I'd run it against two inputs:

* The installed 17.05.47 venv's pip freeze.
* The 14 package-lock.json files.

I'd then compare the result with pip-audit and npm audit, and write it up in internal_dev/code_base/ next to the CodeQL reports.

Do you want me to install it (brew install dependency-check, plus the NVD download) and run that? If you have an NVD API key, tell me where it lives.

## Customer Process

Only for 17.3 so if we never upgrade passes for now, if new vulnerabilities are discovered then we get a FOSS email alert to remediate which often means upgrade to a newer version.

Also means I can’t use later versions of GenAI logic like 17.4 which is not currently FOSS approved so it’s not a one time pass thing it’s a continuous cycle.

We get these alerts on software we’ve been using for months and years and when a  new vulnerability is discovered in JDK or Linux OS we are required to update the ci/cd pipeline FOSS check fails and can’t deploy to production.

## Our understanding

So, please confirm (or not):

* we pass on 17.3
* you cannot use 17.4 until it passes
* appears our current internal procedures are sufficient - upgrading them to OWASP is not indicated at current time
