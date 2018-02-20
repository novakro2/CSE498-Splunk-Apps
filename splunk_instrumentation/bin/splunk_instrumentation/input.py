'''
This is the main entry point to scripted inputs to run

checks if this instance should run the app and then runs the app

'''

from constants import INST_EXECUTION_ID, INST_SCHEMA_FILE, INST_DEBUG_LEVEL
import sys
import logging
from report import report
from time import sleep
from schedule_manager import ScheduleManager
from splunk_instrumentation.dataPoints.data_point import dataPointFactory
from splunk_instrumentation.metrics.metrics_schema import load_schema
from splunk_instrumentation.dataPoints.spl_data_point import SPLDataPoint # noqa
from splunk_instrumentation.dataPoints.report_data_point import ReportDataPoint # noqa
from splunk_instrumentation.metrics.instance_profile import get_instance_profile

logging.root.setLevel(INST_DEBUG_LEVEL)
formatter = logging.Formatter('%(levelname)s %(message)s')
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(formatter)
logging.root.addHandler(handler)

report.report('executionID', INST_EXECUTION_ID)


def run(dateRange, schema_file):
    profile = get_instance_profile()
    ms = load_schema(schema_file, profile.visibility)
    sm = ScheduleManager(ms, dataPointFactory)
    logging.info("INST Started")

    if profile.visibility:
        sm.collect(dateRange)
        sleep(5)
        sm.send(dateRange)
    logging.info("INST Done")

def can_run():
    '''
    This list is eveluated in order
    '''
    profile = get_instance_profile()
    profile.sync_deployment_id()
    profile.sync_salt()

    if not profile.visibility:
        report.report("not-opted-in", True)
        return False

    if not profile.opt_in_is_up_to_date():
        report.report("opt-in-out-of-date-license-only", True)


    report.report("profile.visibility", profile.visibility)
    report.report("profile.cluster_mode", profile.profile.get('cluster_mode'))
    report.report("profile.roles", profile.roles)

    if (profile.roles.get('search_head') and not profile.roles.get('shc_member')) or profile.roles.get('sh_captain'):
        report.report("profile.retry_transaction", True)
        profile.retry_transaction()


    if profile.server_info.get('product_type') == "splunk":
        report.report("instance.type", 'Cloud')
        return False

    return True

def run_input(dateRange):
    if can_run():
        try:
            run(dateRange, INST_SCHEMA_FILE)
            report.send()
        except Exception as ex:
            report.report('input.error', str(ex))
