
# encoding = utf-8

import os
import sys
import time
import datetime
import json

import requests

from workdaylib import Workday, VALID_INPUTS

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''

MIN_INTERVAL = 120

USER_AGENT = "Workday Add-on for Splunk v0.4.1"

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    input_name = definition.parameters.get("input_name", None)
    interval = int(definition.parameters.get("interval"))

    if interval < MIN_INTERVAL:
        raise ValueError("Interval must be at least {}".format(MIN_INTERVAL))

    if input_name not in VALID_INPUTS:
        # input_name is hardcoded in the selector dropdown, this should only happen if someone is messing with internals
        raise ValueError("Invalid input \"{}\", supported values are \"{}\"".format(input_name, "|".join(VALID_INPUTS)))


def collect_events(helper, ew):
    """Implement your data collection logic here

    # The following examples get the arguments of this input.
    # Note, for single instance mod input, args will be returned as a dict.
    # For multi instance mod input, args will be returned as a single value.
    opt_input_name = helper.get_arg('input_name')
    # In single instance mode, to get arguments of a particular input, use
    opt_input_name = helper.get_arg('input_name', stanza_name)

    # get input type
    helper.get_input_type()

    # The following examples get input stanzas.
    # get all detailed input stanzas
    helper.get_input_stanza()
    # get specific input stanza with stanza name
    helper.get_input_stanza(stanza_name)
    # get all stanza names
    helper.get_input_stanza_names()

    # The following examples get options from setup page configuration.
    # get the loglevel from the setup page
    loglevel = helper.get_log_level()
    # get proxy setting configuration
    proxy_settings = helper.get_proxy()
    # get account credentials as dictionary
    account = helper.get_user_credential_by_username("username")
    account = helper.get_user_credential_by_id("account id")
    # get global variable configuration
    global_tenant_id = helper.get_global_setting("tenant_id")
    global_tenant_host = helper.get_global_setting("tenant_host")
    global_client_id = helper.get_global_setting("client_id")
    global_client_secret = helper.get_global_setting("client_secret")
    global_refresh_token = helper.get_global_setting("refresh_token")

    # The following examples show usage of logging related helper functions.
    # write to the log for this modular input using configured global log level or INFO as default
    helper.log("log message")
    # write to the log using specified log level
    helper.log_debug("log message")
    helper.log_info("log message")
    helper.log_warning("log message")
    helper.log_error("log message")
    helper.log_critical("log message")
    # set the log level for this modular input
    # (log_level can be "debug", "info", "warning", "error" or "critical", case insensitive)
    helper.set_log_level(log_level)

    # The following examples send rest requests to some endpoint.
    response = helper.send_http_request(url, method, parameters=None, payload=None,
                                        headers=None, cookies=None, verify=True, cert=None,
                                        timeout=None, use_proxy=True)
    # get the response headers
    r_headers = response.headers
    # get the response body as text
    r_text = response.text
    # get response body as json. If the body text is not a json string, raise a ValueError
    r_json = response.json()
    # get response cookies
    r_cookies = response.cookies
    # get redirect history
    historical_responses = response.history
    # get response status code
    r_status = response.status_code
    # check the response status, if the status is not sucessful, raise requests.HTTPError
    response.raise_for_status()

    # The following examples show usage of check pointing related helper functions.
    # save checkpoint
    helper.save_check_point(key, state)
    # delete checkpoint
    helper.delete_check_point(key)
    # get checkpoint
    state = helper.get_check_point(key)

    # To create a splunk event
    helper.new_event(data, time=None, host=None, index=None, source=None, sourcetype=None, done=True, unbroken=True)
    """

    '''
    # The following example writes a random number as an event. (Multi Instance Mode)
    # Use this code template by default.
    import random
    data = str(random.randint(0,100))
    event = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=helper.get_sourcetype(), data=data)
    ew.write_event(event)
    '''

    '''
    # The following example writes a random number as an event for each input config. (Single Instance Mode)
    # For advanced users, if you want to create single instance mod input, please use this code template.
    # Also, you need to uncomment use_single_instance_mode() above.
    import random
    input_type = helper.get_input_type()
    for stanza_name in helper.get_input_stanza_names():
        data = str(random.randint(0,100))
        event = helper.new_event(source=input_type, index=helper.get_output_index(stanza_name), sourcetype=helper.get_sourcetype(stanza_name), data=data)
        ew.write_event(event)
    '''

    if helper.get_log_level() == "DEBUG":
        import traceback
        debug = True
    else:
        debug = False

    try:
        # Construct Workday client from the provided global config
        rest_api_endpoint   = helper.get_global_setting("rest_api_endpoint")
        token_endpoint      = helper.get_global_setting("token_endpoint")
        client_id           = helper.get_global_setting("client_id")
        client_secret       = helper.get_global_setting("client_secret")
        refresh_token       = helper.get_global_setting("refresh_token")

        empty_fields = []
        if not rest_api_endpoint:
            empty_fields.append("Workday REST API Endpoint")
        if not token_endpoint:
            empty_fields.append("Token Endpoint")
        if not client_id:
            empty_fields.append("Client ID")
        if not client_secret:
            empty_fields.append("Client Secret")
        if not refresh_token:
            empty_fields.append("Refresh Token")
        if len(empty_fields) > 0:
            raise ValueError("Empty fields in global configuration: {}".format(", ".join(empty_fields)))

        wday = Workday(rest_api_endpoint, token_endpoint, client_id, client_secret, refresh_token, http_user_agent=USER_AGENT, helper=helper)
    except ValueError as e:
        helper.log_error(str(e))
        if debug: helper.log_debug("".join(traceback.format_exc()))
        sys.exit(1)

    stanza_names = helper.get_input_stanza_names()
    if not isinstance(stanza_names, list):
        stanza_names = [stanza_names]

    for stanza_name in stanza_names:
        input_type = helper.get_input_type()
        input_name = helper.get_arg("input_name")
        include_target = helper.get_arg("include_target")

        index = helper.get_output_index(stanza_name)
        sourcetype = "workday:{}".format(input_name)

        if input_name == "user_activity":

            # Pull checkpoint value and setup query range for this run
            # Only pull up to 5 minutes in the past to allow time for events to be available in the report
            checkpoint_format = "%Y-%m-%dT%H:%M:%SZ"
            end = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
            start = helper.get_check_point(input_name)
            if start is None:
                start = end
                helper.log_info("No timestamp checkpoint found for input \"{}\", starting from now ({})".format(
                    input_name,
                    start.strftime(checkpoint_format)
                ))
                # Save current time now to preserve original start time in case of errors
                helper.save_check_point(input_name, end.strftime(checkpoint_format))

            else:
                # Confirm that the checkpoint is in the correct format
                try:
                    start = datetime.datetime.strptime(start, checkpoint_format)
                except ValueError as e:
                    helper.log_error("Invalid checkpoint value for input \"{}\", aborting ({})".format(input_name, str(e)))
                    continue


            helper.log_info("Starting input \"{}\" for window ({}, {})".format(
                input_name,
                start.strftime(checkpoint_format),
                end.strftime(checkpoint_format)
            ))

            try:
                input_start = time.time()
                results = list(wday.audit_logs(start, end, include_target=include_target))

            except requests.exceptions.ConnectionError as e:
                helper.log_error("Unable to connect to host")
                if debug: helper.log_debug("".join(traceback.format_exc()))

            except requests.exceptions.Timeout as e:
                helper.log_error("Request timed out, retries exhausted")
                if debug: helper.log_debug("".join(traceback.format_exc()))

            except requests.exceptions.HTTPError as e:
                helper.log_error("Request failed with error code ({}), retries exhausted".format(e.response.status_code))
                if debug: helper.log_debug("".join(traceback.format_exc()))

            except Exception as e:
                helper.log_error("Unknown exception occurred ({})".format(str(e)))
                if debug: helper.log_debug("".join(traceback.format_exc()))

            else:

                # Deliberately wait to write events until all are collected with no errors
                # otherwise errors or restarts could cause missing / duplicate events
                for result in results:
                    event = helper.new_event(
                        source = input_type,
                        index = index,
                        sourcetype = sourcetype,
                        data = json.dumps(result)
                    )
                    ew.write_event(event)

                input_runtime = time.time() - input_start
                event_count = len(results)
                helper.log_info("Finished input \"{}\" for window ({}, {}) in {} seconds, {} events written".format(
                    input_name,
                    start.strftime(checkpoint_format),
                    end.strftime(checkpoint_format),
                    round(input_runtime, 2),
                    event_count
                ))

                helper.save_check_point(input_name, end.strftime(checkpoint_format))

        else:
            helper.log_warning("Invalid input \"{}\", supported values are \"{}\"".format(input_name, "|".join(VALID_INPUTS)))
