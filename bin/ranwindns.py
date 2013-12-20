#!/usr/bin/env python

import subprocess
import ConfigParser

def check_output(*popenargs, **kwargs):
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output

def conf_get_IFP_boolean(config, section, option, default):
    if config.has_option(section, option):
        return config.getboolean(section, option)
    else:
        return default

def conf_get_IFP(config, section, option, default):
    if config.has_option(section, option):
        return config.get(section, option)
    else:
        return default

def conf_get_IFP_int(config, section, option, default):
    if config.has_option(section, option):
        return config.getint(section, option)
    else:
        return default

def send_mail(who, to, subject, body):
    MTA_SERVER = conf_get_IFP(config, "GENERAL", "MTA_SERVER", "")

    if not MTA_SERVER:
        print "Mail not sent because no MTA_SERVER has been defined."
        return

    import smtplib

    # Import the email modules we'll need
    from email.mime.text import MIMEText
    msg = MIMEText(body)

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = subject
    msg['From'] = who
    msg['To'] = to

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(MTA_SERVER)
    s.sendmail(who, [to], msg.as_string())
    s.quit()

STDOUT = -2

def manage_cvs_and_notification(server_name, filename):
    try:
        output = check_output(["cvs", "status", "%s" % filename])
    except subprocess.CalledProcessError, e:
        print "cvs status for %s has returned 1" % filename
        return

    if "Status: Unknown" in output:
        print "Status unknown for %s" % filename
        output = subprocess.check_call(["cvs", "add", "%s" % filename])

        print "New file %s" % filename
        modif = file(filename, "r").readlines()
        body = ''.join(modif)
        EMAIL_FROM = conf_get_IFP(config, "GENERAL", "EMAIL_FROM", "")
        EMAIL_TO = conf_get_IFP(config, "GENERAL", "EMAIL_TO", "")

        if not '@' in EMAIL_FROM or not '@' in EMAIL_TO:
            return

        for email_to in EMAIL_TO.split(";"):
            send_mail(EMAIL_FROM, email_to.strip(), "New server: %s" % server_name, body)
    else:
        try:
            check_output(["cvs", "diff", "-u", "%s" % filename])
        except subprocess.CalledProcessError, e:
            print "Modifications detected for %s" % filename
            modif = e.output.split('\r\n')[:]
            body = '\n'.join(modif)
            EMAIL_FROM = conf_get_IFP(config, "GENERAL", "EMAIL_FROM", "")
            EMAIL_TO = conf_get_IFP(config, "GENERAL", "EMAIL_TO", "")

            if not '@' in EMAIL_FROM or not '@' in EMAIL_TO:
                return

            for email_to in EMAIL_TO.split(";"):
                send_mail(EMAIL_FROM, email_to.strip(), "Changes detected for: %s" % server_name, body)
        else:
            pass

    print "Commiting %s" % filename
    subprocess.call(["cvs", "commit", "-m", "Update", "%s" % filename])

def manage_svn_and_notification(server_name, filename):
    try:
        output = check_output(["svn", "status", "%s" % filename])
    except WindowsError, e:
        print "Please ensure svn.exe is in your PATH"
        return

    if "? " in output:
        print "Status unknown for %s" % filename
        try:
            output = subprocess.check_call(["svn", "add", "%s" % filename])
        except subprocess.CalledProcessError, e:
            print "%s" % e
    elif "M " in output:
        output = check_output(["svn", "diff", "%s" % filename])
        print "Modifications detected for %s" % filename
        modif = output.split('\r\n')[4:]
        body = '\n'.join(modif)
        EMAIL_FROM = conf_get_IFP(config, "GENERAL", "EMAIL_FROM", "")
        EMAIL_TO = conf_get_IFP(config, "GENERAL", "EMAIL_TO", "")

        if not '@' in EMAIL_FROM or not '@' in EMAIL_TO:
            return

        try:
            send_mail(EMAIL_FROM, EMAIL_TO, "Changes detected for: %s" % server_name, body)
        except Exception, e:
            print "Sending mail has failed, please check value of MTA_SERVER in the configuration file."
    else:
        pass

    print "Commiting %s" % filename
    subprocess.call(["svn", "commit", "-m", "Update", "%s" % filename])

def manage_vcs_and_notification(server_name, filename):
    VCS = conf_get_IFP(config, "GENERAL", "VCS", "NONE")

    if VCS == "CVS":
        manage_cvs_and_notification(server_name, filename)
    elif VCS == "SVN":
        manage_svn_and_notification(server_name, filename)
    elif VCS.upper() == "NONE":
        return
    else:
        print "VCS %s is not supported" % VCS

def load_server_list(filename):
    server_list = []

    f = file(filename, "r")
    lines = f.read().split('\n')
    for line in lines:
        if line.startswith('#'):
            continue
        value_list = line.split(',')
        server_name = ""
        login = ""
        password = ""
        if len(value_list) >= 1:
            server_name = value_list[0].strip()
        if len(value_list) >= 2:
            login = value_list[1].strip()
        if len(value_list) >= 3:
            password = value_list[2].strip()

	if server_name:
            server_list.append((server_name, login, password))

    return server_list

def mkdir_IFN(localpath):
    import os

    try:
        os.makedirs(localpath)
    except:
        pass

def windns():
    import os

    filename = conf_get_IFP(config, "GENERAL", "SERVER_LIST", "")
    filename = os.path.expanduser(filename)

    if not os.path.exists(filename):
        print "server list file not found: %s" % filename
        return

    server_list = load_server_list(filename)

    print "%d servers were retrieved" % len(server_list)

    from ranwindns.common import generate_host_config

    record_only_good_config =  conf_get_IFP_boolean(config, "GENERAL", "RECORD_ONLY_GOOD_CONFIG", False)

    output_dir =  conf_get_IFP(config, "GENERAL", "OUTPUT_DIR", ".")

    mkdir_IFN(output_dir)

    for value in server_list:
        server_name, login, password = value
        target = "%s/%s.txt" % (output_dir, server_name)

        try:
            result = generate_host_config(server_name, target, login, password, record_only_good_config)

            if result:
                manage_vcs_and_notification(server_name, target)
        except Exception, e:
            print "[Exception] %s" % server_name
            print "%s" % e

DEFAULT_CONFIGURATION = \
"""# This is the default configuration file
# Please edit it and update values with your environment
[GENERAL]
EMAIL_FROM = ranwindns@yourdomain.com
EMAIL_TO = winadmin@yourdomain.com
MTA_SERVER = youremailserver.com

# Versionning and Configuration System: CVS or SVN (or NONE if no VCS)
VCS = NONE

# Location of the file with the list of servers to analyse
# LINE FORMAT:
# server_name, [login], [password]
SERVER_LIST = ./server_list.txt

# Directory where files will be generated
# Default is current directory
OUTPUT_DIR = .
"""

def create_default_configuration_file(filename):
    f = file(filename, "w")
    f.write(DEFAULT_CONFIGURATION)
    f.close()

def run(config_file):
    import os

    if not os.path.exists(config_file):
        print "Error: configuration file not found %s" % config_file
        return

    global config

    config = ConfigParser.ConfigParser()
    config.read(config_file)

    import datetime
    start = datetime.datetime.now()

    windns()

    end = datetime.datetime.now()
    duration = end - start

    print "Duration : %s" % duration

def genconfig(config_file):
    create_default_configuration_file(config_file)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Windows DNS Server changes tracker.',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog='GENCONFIG: generate default configuration file, to be customized with your environment.\nRUN: get configuration for each server and generates corresponding files.')
    parser.add_argument('action', type=str, help="Action to execute (GENCONFIG or RUN)")
    parser.add_argument('-c', '--config', type=str, help="Configuration file to use or create")
    parser.add_argument('--v', action='version', help="Print program version and exit.", version='%(prog)s 0.1.0 (20131220)')
    args = parser.parse_args()

    action = args.action
    config_file = args.config

    if not config_file:
        print "Error: configuration filename should be specified when action is RUN or GENCONFIG."
        print "Please use -c or --config parameter to define it."
        return

    action = action.upper()

    if action == "RUN":
        run(config_file)
    elif action == "GENCONFIG":
        genconfig(config_file)
    else:
        print "Action %s is unknown" % action

if __name__ == '__main__':
    # HACK HACK HACK
    # Put Python script dir at the end, as ranwindns script and ranwindns module clash :-(
    import sys
    sys.path = sys.path[1:] + [sys.path[0]]
    main()
