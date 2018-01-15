# Censys subdomain finder

This is a tool to enumerate subdomains using the Certificate Transparency logs stored by [Censys](https://censys.io). It should return any subdomain who has ever been issued a SSL certificate by a public CA.

See it in action:

```
$ python censys_subdomain_finder.py github.com

[*] Searching Censys for subdomains of github.com
[*] Found 42 unique subdomains of github.com in ~1.7 seconds

  - hq.github.com
  - talks.github.com
  - cla.github.com
  - github.com
  - cloud.github.com
  - enterprise.github.com
  - help.github.com
  - collector-cdn.github.com
  - central.github.com
  - smtp.github.com
  - cas.octodemo.github.com
  - schrauger.github.com
  - jobs.github.com
  - classroom.github.com
  - dodgeball.github.com
  - visualstudio.github.com
  - branch.github.com
  - www.github.com
  - edu.github.com
  - education.github.com
  - import.github.com
  - styleguide.github.com
  - community.github.com
  - server.github.com
  - mac-installer.github.com
  - registry.github.com
  - f.cloud.github.com
  - offer.github.com
  - helpnext.github.com
  - foo.github.com
  - porter.github.com
  - id.github.com
  - atom-installer.github.com
  - review-lab.github.com
  - vpn-ca.iad.github.com
  - maintainers.github.com
  - raw.github.com
  - status.github.com
  - camo.github.com
  - support.enterprise.github.com
  - stg.github.com
  - rs.github.com

```

## Setup

1) Register an account (free) on https://censys.io/register
2) Browse to https://censys.io/account, and set two environment variables with your API ID and API secret

```
$ export CENSYS_API_ID=...
$ export CENSYS_API_SECRET=...
```

3) Clone the repository

```
$ git clone https://github.com/christophetd/censys-subdomain-finder.git
```

4) Install the dependencies

```
$ cd censys-subdomain-finder
$ pip install -r requirements.txt
```

5) Run the script on `example.com` to make sure everything works as expected.

```
$ python censys_subdomain_finder.py example.com

[*] Searching Censys for subdomains of example.com
[*] Found 5 unique subdomains of example.com

  - products.example.com
  - www.example.com
  - dev.example.com
  - example.com
  - support.example.com
```
## Usage

```
usage: censys_subdomain_finder.py [-h] [-o OUTPUT_FILE]
                                  [--censys-api-id CENSYS_API_ID]
                                  [--censys-api-secret CENSYS_API_SECRET]
                                  domain

positional arguments:
  domain                The domain to scan

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        A file to output the list of subdomains to (default:
                        None)
  --censys-api-id CENSYS_API_ID
                        Censys API ID. Can also be defined using the
                        CENSYS_API_ID environment variable (default: None)
  --censys-api-secret CENSYS_API_SECRET
                        Censys API secret. Can also be defined using the
                        CENSYS_API_SECRET environment variable (default: None)
```


## Compatibility

Should run on Python 2.7 and 3.5.

## Notes

The Censys API has a limit rate of 120 queries per 5 minutes window. Each invocation of this tool makes exactly one API call to Censys.

Feel free to [open an issue](https://github.com/christophetd/censys-subdomain-finder/issues/new) or to [tweet @christophetd](https://twitter.com/christophetd/) for suggestions or remarks.
