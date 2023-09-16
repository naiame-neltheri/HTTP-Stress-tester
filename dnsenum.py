import argparse

if "__main__" in __name__:
    parser = argparse.ArgumentParser(description='DNS enumeration by HTTP')
    parser.add_argument('domain', metavar='domain', type=str, nargs=1, help='Domain to enumerate')
    parser.add_argument('--wordlist', dest='wordlist', action='store', help='wordlist file to use for enumration')

    args = parser.parse_args()
    print(args)