#!/usr/bin/env python3

import censys.certificates
import censys.ipv4
import censys
import sys
import cli
import os

# Finds subdomains of a domain using Censys API
def find_subdomains(domain, api_id, api_secret):
    try:
        censys_certificates = censys.certificates.CensysCertificates(api_id=api_id, api_secret=api_secret)
        certificate_query = 'parsed.names: %s and tags.raw: trusted' % domain
        certificates_search_results = censys_certificates.search(certificate_query, fields=['parsed.names'])
        
        # Flatten the result, and remove duplicates
        subdomains = []
        for search_result in certificates_search_results:
            subdomains.extend(search_result['parsed.names'])
		
        return set(subdomains)
    except censys.base.CensysUnauthorizedException:
        sys.stderr.write('[-] Your Censys credentials look invalid.\n')
        exit(1)
    except censys.base.CensysRateLimitExceededException:
        sys.stderr.write('[-] Looks like you exceeded your Censys account limits rate. Exiting\n')
        exit(1)

# Filters out uninteresting subdomains
def filter_subdomains(domain, subdomains):
	return [ subdomain for subdomain in subdomains if '*' not in subdomain and subdomain.endswith(domain) ]

# Prints the list of found subdomains to stdout
def print_subdomains(domain, subdomains):
    if len(subdomains) is 0:
        print('[-] Did not find any subdomain')
        return

    print('[*] Found %d unique subdomain%s of %s' % (len(subdomains), 's' if len(subdomains) > 1 else '', domain))
	
    for subdomain in subdomains:
        print('  - ' + subdomain)

# Saves the list of found subdomains to an output file
def save_subdomains_to_file(subdomains, output_file):
    if output_file is None or len(subdomains) is 0:
        return

    try:
        with open(output_file, 'w') as f:
            for subdomain in subdomains:
                f.write(subdomain + '\n')

        print('[*] Wrote %d subdomains to %s' % (len(subdomains), os.path.abspath(output_file)))
    except IOError as e:
        sys.stderr.write('[-] Unable to write to output file %s : %s\n' % (output_file, e))

def main(domain, output_file, censys_api_id, censys_api_secret):
    print('[*] Searching Censys for subdomains of %s' % domain)
    subdomains = find_subdomains(domain, censys_api_id, censys_api_secret)
    subdomains = filter_subdomains(domain, subdomains)
    print_subdomains(domain, subdomains)
    save_subdomains_to_file(subdomains, output_file)

if __name__ == "__main__":
    args = cli.parser.parse_args()

    censys_api_id = None
    censys_api_secret = None

    if 'CENSYS_API_ID' in os.environ and 'CENSYS_API_SECRET' in os.environ:
        censys_api_id = os.environ['CENSYS_API_ID']
        censys_api_secret = os.environ['CENSYS_API_SECRET']

    if args.censys_api_id and args.censys_api_secret:
        censys_api_id = args.censys_api_id
        censys_api_secret = args.censys_api_secret

    if None in [ censys_api_id, censys_api_secret ]:
        sys.stderr.write('[!] Please set your Censys API ID and secret from your environment (CENSYS_API_ID and CENSYS_API_SECRET) or from the command line.\n')
        exit(1)
		
    main(args.domain, args.output_file, censys_api_id, censys_api_secret)