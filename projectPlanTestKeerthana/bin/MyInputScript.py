
import splunk.entity as entity

. . .

# access the credentials in /servicesNS/nobody/app_name/admin/passwords
def getCredentials(sessionKey):
   myapp = 'projectPlanTestKeerthana'
   try:
      # list all credentials
      entities = entity.getEntities(['admin', 'passwords'], namespace=myapp,
                                    owner='nobody', sessionKey=sessionKey)
   except Exception, e:
      raise Exception("Could not get %s credentials from splunk. Error: %s"
                      % (myapp, str(e)))

   # return first set of credentials
   for i, c in entities.items():
        return c['username'], c['clear_password']

   raise Exception("No credentials have been found")  

def main():
        # read session key sent from splunkd
        sessionKey = sys.stdin.readline().strip()

        if len(sessionKey) == 0:
           sys.stderr.write("Did not receive a session key from splunkd. " +
                            "Please enable passAuth in inputs.conf for this " +
                            "script\n")
           exit(2)

        # now get twitter credentials - might exit if no creds are available
        username, password = getCredentials(sessionKey)

        # use the credentials to access the data source
        . . .


# import splunk.admin as admin
# import splunk.entity as en
# # import your required python modules

# '''
# Copyright (C) 2005 - 2010 Splunk Inc. All Rights Reserved.
# Description:  This skeleton python script handles the parameters in the configuration page.

#       handleList method: lists configurable parameters in the configuration page
#       corresponds to handleractions = list in restmap.conf

#       handleEdit method: controls the parameters and saves the values 
#       corresponds to handleractions = edit in restmap.conf

# '''

# class ConfigApp(admin.MConfigHandler):
#   '''
#   Set up supported arguments
#   '''
#   def setup(self):
#     if self.requestedAction == admin.ACTION_EDIT:
#       for arg in ['Certificate_ID', 'Certificate_Path']:
#         self.supportedArgs.addOptArg(arg)
        
#   '''
#   Read the initial values of the parameters from the custom file
#       app.conf, and write them to the setup page. 

#   If the app has never been set up,
#       uses .../app_name/default/app.conf. 

#   If app has been set up, looks at 
#       .../local/app.conf first, then looks at 
#   .../default/app.conf only if there is no value for a field in
#       .../local/app.conf

#   For boolean fields, may need to switch the true/false setting.

#   For text fields, if the conf file says None, set to the empty string.
#   '''

#   def handleList(self, confInfo):
#     confDict = self.readConf("app")
#     if None != confDict:
#       for stanza, settings in confDict.items():
#         for key, val in settings.items():
#           if key in ['Certificate_Path']:
#             if int(val) == 1:
#               val = '0'
#             else:
#               val = '1'
#           if key in ['Certificate_ID'] and val in [None, '']:
#             val = ''
#           confInfo[stanza].append(key, val)
          
#   '''
#   After user clicks Save on setup page, take updated parameters,
#   normalize them, and save them somewhere
#   '''
#   def handleEdit(self, confInfo):
#     name = self.callerArgs.id
#     args = self.callerArgs
    

#     if int(self.callerArgs.data['Certificate_Path'][0]) == 1:
#       self.callerArgs.data['Certificate_Path'][0] = '0'
#     else:
#       self.callerArgs.data['Certificate_Path'][0] = '1'
    
#     if self.callerArgs.data['Certificate_ID'][0] in [None, '']:
#       self.callerArgs.data['Certificate_ID'][0] = ''  

        
#     '''
#     Since we are using a conf file to store parameters, 
# write them to the [setupentity] stanza
#     in app_name/local/app.conf  
#     '''
        
#     self.writeConf('app', 'setupentity', self.callerArgs.data)
      
# # initialize the handler
# admin.init(ConfigApp, admin.CONTEXT_NONE)