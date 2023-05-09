#!/usr/bin/env python3

from censys.search import CensysCerts
from censys.common.exceptions import (
    CensysUnauthorizedException,
    CensysRateLimitExceededException,
    CensysException,
)
from dotenv import load_dotenv
import sys
import cli
import os
import time

load_dotenv()

USER_AGENT = f"{CensysCerts.DEFAULT_USER_AGENT} (censys-subdomain-finder; +https://github.com/christophetd/censys-subdomain-finder)"

MAX_PER_PAGE = 100
COMMUNITY_PAGES = 10


# Finds subdomains of a domain using Censys API
def find_subdomains(domain, api_id, api_secret, limit_results):
    try:
        censys_certificates = CensysCerts(
            api_id=api_id, api_secret=api_secret, user_agent=USER_AGENT
        )
        certificate_query = "names: %s" % domain
        pages = -1 # unlimited
        if limit_results:
            pages = COMMUNITY_PAGES
        certificates_search_results = censys_certificates.search(
            certificate_query,
            per_page=MAX_PER_PAGE,
            pages=pages
        )

        # Flatten the result, and remove duplicates
        subdomains = []
        for page in certificates_search_results:
            for search_result in page:
                subdomains.extend(search_result["names"])

        return set(subdomains)
    except CensysUnauthorizedException:
        sys.stderr.write("[-] Your Censys credentials look invalid.\n")
        exit(1)
    except CensysRateLimitExceededException:
        sys.stderr.write(
            "[-] Looks like you exceeded your Censys account limits rate. Exiting\n"
        )
        return set(subdomains)
    except CensysException as e:
        # catch the Censys Base exception, example "only 1000 first results are available"
        sys.stderr.write("[-] Something bad happened, " + repr(e))
        return set(subdomains)


# Filters out uninteresting subdomains
def filter_subdomains(domain, subdomains):
    return [
        subdomain
        for subdomain in subdomains
        if "*" not in subdomain and subdomain.endswith(domain) and subdomain != domain
    ]


# Prints the list of found subdomains to stdout
def print_subdomains(domain, subdomains, time_elapsed):
    if len(subdomains) == 0:
        print("[-] Did not find any subdomain")
        return

    print(
        "[*] Found %d unique subdomain%s of %s in ~%s seconds\n"
        % (
            len(subdomains),
            "s" if len(subdomains) > 1 else "",
            domain,
            str(time_elapsed),
        )
    )
    for subdomain in subdomains:
        print("  - " + subdomain)

    print("")


# Saves the list of found subdomains to an output file
def save_subdomains_to_file(subdomains, output_file):
    if output_file is None or len(subdomains) == 0:
        return

    try:
        with open(output_file, "w") as f:
            for subdomain in subdomains:
                f.write(subdomain + "\n")

        print(
            "[*] Wrote %d subdomains to %s"
            % (len(subdomains), os.path.abspath(output_file))
        )
    except IOError as e:
        sys.stderr.write(
            "[-] Unable to write to output file %s : %s\n" % (output_file, e)
        )


def main(domain, output_file, censys_api_id, censys_api_secret, limit_results):
    print("[*] Searching Censys for subdomains of %s" % domain)
    start_time = time.time()
    subdomains = find_subdomains(
        domain, censys_api_id, censys_api_secret, limit_results
    )
    subdomains = filter_subdomains(domain, subdomains)
    end_time = time.time()
    time_elapsed = round(end_time - start_time, 1)
    print_subdomains(domain, subdomains, time_elapsed)
    save_subdomains_to_file(subdomains, output_file)


if __name__ == "__main__":
    args = cli.parser.parse_args()

    censys_api_id = None
    censys_api_secret = None

    if "CENSYS_API_ID" in os.environ and "CENSYS_API_SECRET" in os.environ:
        censys_api_id = os.environ["CENSYS_API_ID"]
        censys_api_secret = os.environ["CENSYS_API_SECRET"]

    if args.censys_api_id and args.censys_api_secret:
        censys_api_id = args.censys_api_id
        censys_api_secret = args.censys_api_secret

    limit_results = not args.commercial
    if limit_results:
        print(
            f"[*] Applying free plan limits ({MAX_PER_PAGE * COMMUNITY_PAGES} results at most)"
        )
    else:
        print("[*] No limits applied, getting all results")

    if None in [censys_api_id, censys_api_secret]:
        sys.stderr.write(
            "[!] Please set your Censys API ID and secret from your environment (CENSYS_API_ID and CENSYS_API_SECRET) or from the command line.\n"
        )
        exit(1)

    main(args.domain, args.output_file, censys_api_id, censys_api_secret, limit_results)
