
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, help="Name or IP of the host to get configuration from")
    parser.add_argument('--output', type=str, nargs='?', default='<stdout>', help="Output file to write the configuration, default is <stdout>")
    parser.add_argument('--user', type=str, nargs='?', default='', help="Name the account to use to connect to host")
    parser.add_argument('--pwd', type=str, nargs='?', default='', help="Password of the account to use to connect to host")
    args = parser.parse_args()

    host = args.host
    target = args.output

    user = args.user
    password = args.pwd

    from ranwindns.common import generate_host_config
    generate_host_config(host, target, user, password)

if __name__ == '__main__':
    # HACK HACK HACK
    # Put Python script dir at the end, as ranwindns script and ranwindns module clash :-(
    import sys
    sys.path = sys.path[1:] + [sys.path[0]]
    main()