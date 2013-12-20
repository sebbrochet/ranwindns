
def GetHostConfig(host, user, password, namespace = ""):
    result = {}

    import wmi

    if user and password:
        c = wmi.WMI(host, user = user, password = password, namespace = namespace)
    else:
        c = wmi.WMI(host)

    result["DNS"] = GetDNS_Zones(c)

    return result

class SortedDict(object):
    def __init__(self, d):
        self.d = d

class FakedList(object):
    def __init__(self, l):
        self.l= l

def pretty_print_dict(d, output_list, left, sort = False):
    if sort:
        for key in iter(sorted(d.keys())):
            output_list.append("%s%s" % (left * ' ', key))
            pretty_print(d[key], output_list, left+3)
    else:
        for key in d.keys():
            output_list.append("%s%s" % (left * ' ', key))
            pretty_print(d[key], output_list, left+3)

def pretty_print_list(l, output_list, left):
    for item in l:
        if item.__class__ is list:
            pretty_print(item, output_list, left+3)
        else:
            pretty_print(item, output_list, left)

def pretty_print(v, output_list, left=0):
    if v.__class__ is SortedDict:
        pretty_print_dict(v.d, output_list, left, sort = True)
    elif v.__class__ is dict:
        pretty_print_dict(v, output_list, left)
    elif v.__class__ is FakedList:
        pretty_print_list(v.l, output_list, left-3)
    elif v.__class__ is list:
        pretty_print_list(v, output_list, left)
    else:
        output_list.append("%s%s" % (left * ' ', v))

def myprint(unicodeobj):
    print unicodeobj

def GetSystemName(c):
    result = []

    systems = c.Win32_ComputerSystem()

    for system in systems:
        result.append(system.Name)

    return result

def GetDNS_Zones(c):
    def get_record_for_zone(name):
        wql = "Select * from MicrosoftDNS_ResourceRecord where DomainName='%s'" % name
        record_list = c.query(wql)
        return [record.TextRepresentation for record in record_list]

    result = {}

    #dns_server = c.get('MicrosoftDNS_Server.name="."')
    #print dns_server.name

    zones = c.instances("MicrosoftDNS_Zone")

    for zone in zones:
        name = zone.Name
        result[name] = get_record_for_zone(name)

    return result

def generate_host_config(host, target, user="", password="", RecordOnlyGoodConfig=False):
    host_config = GetHostConfig(host, user, password, "root\MicrosoftDNS")

    output_list = []

    if host_config:
        display_list = [
            { "DNS" : SortedDict(host_config["DNS"]) },
        ]

        pretty_print(display_list, output_list)
    else:
        output_list.append("Error: check if:")
        output_list.append("host %s answers ping" % host)
        output_list.append("COM+ service is started on host: %s" % host)
        output_list.append("Used account has enough (admin) rights")

    if target != "<stdout>":
        if host_config or not RecordOnlyGoodConfig:
            f = file(target, "w")
            f.write('\n'.join(output_list).encode('utf-8'))
            f.close()
    else:
        myprint('\n'.join(output_list))

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

    generate_host_config(host, target, user, password)

if __name__ == '__main__':
    main()