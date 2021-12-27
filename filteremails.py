import requests
import sys
import argparse
from bs4 import BeautifulSoup

"""
Input: Text file containing email addresses, one address per line
Output: A file containing all email address from the input file
whose domain was found in the file under the URL
"""

# I made some changes to the original codes:)
__original_author__ = 'lukasrieger'

# constant default settings
URL = 'https://gist.github.com/michenriksen/8710649'
PATH_DOMAINS_LOCAL = 'disposable_domains.txt'
DEFAULT_INPUT = 'emails.txt'
DEFAULT_OUTPUT = 'filtered_emails.txt'


def refresh_domains_file():
    """
    This method gets the disposable domains list from the git repo
    as html and scrapes it. Finally all domains are written to a file.
    """
    html = requests.get(URL).content
    soup = BeautifulSoup(html, features='html.parser')
    tds = soup.findAll('td', class_='js-file-line')
    domains = [td.text + '\n' for td in tds]

    with open(PATH_DOMAINS_LOCAL, 'w') as f:
        f.writelines(domains)

    print(f'Refreshed disposable domains file under path {PATH_DOMAINS_LOCAL}')


def get_disposable_domains(refresh=False):
    """
    This method loads the entries from the disposable domains file
    into a list and returns the list. If the parameter refresh=True,
    the file is refreshed with the domains given in the git repo.
    """
    if refresh:
        # load data from git repo
        refresh_domains_file()

    domains = None
    with open(PATH_DOMAINS_LOCAL) as f:
        domains = f.readlines()
    # remove linebreaks
    return [domain.rstrip() for domain in domains]


def check_mails(in_path, out_path, refresh=False):
    """
    Loads the list of disposable domains and
    checks each address from the input file for those domains.
    Only if the list of disposable domains contains the email's
    domain, the email address will be added to the outfile.
    """
    # Membership check in set is faster than list.
    disposable_domains = set(get_disposable_domains(refresh=refresh))
    count = 0
    print(disposable_domains)
    with open(in_path) as in_file, open(out_path, 'w') as out_file:
        for email in in_file:
            try:
                suffix = email[email.find('@') + 1:]
            except:
                # If the email address does not contain '@', we consider it invalid.
                print(f'Invalid email address: {email}')
                continue

            # remove blanks around the suffix
            if suffix.strip() in disposable_domains:
                out_file.write(email)
                count += 1

    return count


if __name__ == '__main__':
    print('Filtering emails...')

    parser = argparse.ArgumentParser(
        description='Filter email addresses by disposable domains.')
    parser.add_argument('-i', type=str, nargs='?',
                        help='Path of input file with the email addresses.')
    parser.add_argument('-o', type=str, nargs='?',
                        help='Path where the output will be put.')
    parser.add_argument('-r', action='store_true',
                        help='Refresh local copy of the disposable domains file.')

    args = parser.parse_args()

    path_input = args.i if args.i else DEFAULT_INPUT
    path_output = args.o if args.o else DEFAULT_OUTPUT
    refresh = args.r

    try:
        mails_count = check_mails(path_input, path_output, refresh)
        print(f'Copied {mails_count} email addresses to the output file.')
        print('Done.')
    except:
        print(
            f'Sorry, an unexpected error ({sys.exc_info()[1]}) occurred!\nCall filtermails.py -h for help.')
