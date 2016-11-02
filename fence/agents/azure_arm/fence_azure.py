#!/usr/bin/python

import sys, re, pexpect
import logging
import logging.handlers
import atexit
sys.path.append("/usr/share/fence")
from fencing import *
from fencing import fail, fail_usage, EC_TIMED_OUT, run_delay

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient

#BEGIN_VERSION_GENERATION
RELEASE_VERSION="4.0.24.6-7e576"
BUILD_DATE="(built Mon Oct 24 16:32:49 DST 2016)"
REDHAT_COPYRIGHT="Copyright (C) Red Hat, Inc. 2004-2010 All rights reserved."
#END_VERSION_GENERATION

def get_power_status(conn, options):
        logging.info("getting power status for VM " + options["--vmname"])
        tenantid = options["--tenandId"]
        rgName = options["--resourceGroup"]
        servicePrincipal = options["--username"]
        vmName = options["--vmname"]
        spPassword = options["--password"]
        subscriptionId = options["--subscriptionId"]
        credentials = ServicePrincipalCredentials(
                client_id = servicePrincipal,
                secret = spPassword,
                tenant = tenantid
        )
        compute_client = ComputeManagementClient(
                credentials,
                subscriptionId
        )

        powerState = "unknown"
        vmStatus = compute_client.virtual_machines.get(rgName, vmName, "instanceView")
        for status in vmStatus.instance_view.statuses:
                if status.code.startswith("PowerState"):
                        powerState = status.code
                        break

        logging.info("Found power state of VM: " + powerState)
        if powerState == "PowerState/running":
                return "on"

        return "off"

def set_power_status(conn, options):
        logging.info("setting power status for VM " + options["--vmname"] + " to " + options["--action"])
        tenantid = options["--tenandId"]
        rgName = options["--resourceGroup"]
        servicePrincipal = options["--username"]
        vmName = options["--vmname"]
        spPassword = options["--password"]
        subscriptionId = options["--subscriptionId"]
        credentials = ServicePrincipalCredentials(
                client_id = servicePrincipal,
                secret = spPassword,
                tenant = tenantid
        )
        compute_client = ComputeManagementClient(
                credentials,
                subscriptionId
        )

        if (options["--action"]=="off"):
                logging.info("Deallocating " + vmName + "in resource group " + rgName)
                compute_client.virtual_machines.deallocate(rgName, vmName)
        elif (options["--action"]=="reboot"):
                logging.info("Restarting " + vmName + "in resource group " + rgName)
                compute_client.virtual_machines.restart(rgName, vmName)

# Main agent method
def main():

        device_opt = ["vmName", "resourceGroup", "login", "passwd", "tenandId", "subscriptionId"]

        atexit.register(atexit_handler)
        all_opt["vmName"] = {
                "getopt" : "vmname:",
                "longopt" : "vmname",
                "help" : "-v, --vmname=[name]       Type of VMware to connect",
                "shortdesc" : "Name of VM.",
                "required" : "1",
                "order" : 1
        }

        all_opt["resourceGroup"] = {
                "getopt" : "rg:",
                "longopt" : "resourceGroup",
                "help" : "-rg, --resourceGroup=[name]       Type of VMware to connect",
                "shortdesc" : "Name of resource Group.",
                "required" : "1",
                "order" : 2
        }
        all_opt["tenandId"] = {
                "getopt" : "tid:",
                "longopt" : "tenandId",
                "help" : "-tenandId, --tenandId=[name]       Type of VMware to connect",
                "shortdesc" : "Id of Active Directory Tenant.",
                "required" : "1",
                "order" : 3
        }
        all_opt["subscriptionId"] = {
		"getopt" : "sid:",
                "longopt" : "subscriptionId",
                "help" : "-sid, --subscriptionId=[name]       Type of VMware to connect",
                "shortdesc" : "Id of Azure Subscription.",
                "required" : "1",
                "order" : 4
        }

        options = check_input(device_opt, process_input(device_opt))

        docs = {}
        docs["shortdesc"] = "Fence agent for Azure Resource Manager"
        docs["longdesc"] = ""
        docs["vendorurl"] = "http://www.microsoft.com"
        show_docs(options, docs)

        run_delay(options)

        # Operate the fencing device
        result = fence_action(None, options, set_power_status, get_power_status, None)

        sys.exit(result)

if __name__ == "__main__":
        main()
