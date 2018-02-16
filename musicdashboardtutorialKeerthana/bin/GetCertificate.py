import splunk.admin as admin
import splunk.clilib.cli_common as scc
import splunktalib.common.util as utils
from splunktalib.conf_manager import conf_manager as conf
from splunktalib.common import log
import logging


"""
Copyright (C) 2005 - 2015 Splunk Inc. All Rights Reserved.
Description:  This skeleton python script handles the parameters in the configuration page.

      handleList method: lists configurable parameters in the configuration page
      corresponds to handleractions = list in restmap.conf

      handleEdit method: controls the parameters and saves the values 
      corresponds to handleractions = edit in restmap.conf
"""


class ConfigApp(admin.MConfigHandler):
    """
    Set up supported arguments
    """
    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in [ 'interval']:
                self.supportedArgs.addOptArg(arg)
        
    """
    Read the initial values of the parameters from the custom file
      myappsetup.conf, and write them to the setup screen.

    If the app has never been set up,
      uses .../<appname>/default/myappsetup.conf.

    If app has been set up, looks at
      .../local/myappsetup.conf first, then looks at
    .../default/myappsetup.conf only if there is no value for a field in
      .../local/myappsetup.conf

    For boolean fields, may need to switch the true/false setting.

    For text fields, if the conf file says None, set to the empty string.
    """

    def handleList(self, confInfo):
        confDict = self.readConf("symantec_ep")
        if None != confDict:
            for stanza, settings in confDict.items():
                for key, val in settings.items():
                    confInfo['symantec_ep'].append(key, val)

    """
    After user clicks Save on setup screen, take updated parameters,
    normalize them, and save them somewhere
    """
    def handleEdit(self, confInfo):
        name = self.callerArgs.id
        args = self.callerArgs
    
    
        if self.callerArgs.data['interval'][0] in [None, '']:
          self.callerArgs.data['interval'][0] = ''  

        
    '''
    Since we are using a conf file to store parameters, 
write them to the [setupentity] stanza
    in app_name/local/myappsetup.conf  
    '''
        
    self.writeConf('symantec_ep', 'symantec_ep', self.callerArgs.data)
      
    
      
# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)