import json
import os
import re
import sys

import requests
from flask import Flask, redirect, url_for, request

app = Flask(__name__)

DISPOSABLE_DOMAINS = []


def runFlaskApp():
    try:
        if sys.argv[1].lower().startswith("d"):
            debug = True
        else:
            debug = False
    except IndexError:
        debug = False
    app.run("0.0.0.0", port=3337, debug=debug)


def makeFileIfNotExists():
    if not("disposable.data" in os.listdir(os.getcwd())):
        r = requests.get(
            "https://raw.githubusercontent.com/disposable/disposable-email-domains/master/domains_mx.txt").content
        with open(os.path.join(os.getcwd(), "disposable.data"), "wb") as domainlist:
            domainlist.write(r)


def getDomains():
    global DISPOSABLE_DOMAINS
    try:
        with open(os.path.join(os.getcwd(), "disposable.data"), "r", encoding="utf-8") as domainlistf:
            DISPOSABLE_DOMAINS = domainlistf.readlines()
    except FileNotFoundError:
        makeFileIfNotExists()


def validateFirstStep(email: str = None):
    if email is None:
        return "Error"

    # REGEX TAKEN FROM:
    #   https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if (re.fullmatch(regex, email)):
        return True
    else:
        return False


def validateEmailDomain(email: str = None):
    global DISPOSABLE_DOMAINS

    makeFileIfNotExists()

    if email is None:
        return "Error"

    if validateFirstStep(email=email):
        for domain in DISPOSABLE_DOMAINS:
            if email.lower().strip().endswith(str(domain).lower().strip()):
                return False
        return True
    else:
        return False


@app.route("/api")
def checkemail():
    global DISPOSABLE_DOMAINS

    if len(DISPOSABLE_DOMAINS) == 0:
        makeFileIfNotExists()
        getDomains()

    emailaddr = request.args.get("email")

    if emailaddr is None:
        return str(json.dumps({'status': 'error. no email parameter'}))

    if validateEmailDomain(email=emailaddr) == True:
        return str(json.dumps({'status': True}))
    else:
        return str(json.dumps({'status': False}))


if __name__ == "__main__":
    getDomains()
    runFlaskApp()
