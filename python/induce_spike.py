from zeep import Client
from zeep import Transport
from requests import Session
import time
import datetime
import random
import string

session = Session()
session.cert = ('C:/Users/Robert/Documents/CSE498/certificate.pem', 'C:/Users/Robert/Documents/CSE498/plainkey.pem')
transport = Transport(session=session)

client_mgmt = Client("C:/Users/Robert/Documents/CSE498/wsdl/vipuserservices-mgmt-1.8.wsdl", transport=transport)
client_auth = Client("C:/Users/Robert/Documents/CSE498/wsdl/vipuserservices-auth-1.8.wsdl", transport=transport)
client_query = Client("C:/Users/Robert/Documents/CSE498/wsdl/vipuserservices-query-1.8.wsdl", transport=transport)
client_api_auth = Client("C:/Users/Robert/Documents/CSE498/api/vip_auth.wsdl", transport=transport)

def get_time():
    """ Gets the time. Used for request ids"""
    return int(time.time())

def user_exists(user):
    """
    Determines if a user exists
    :param user: the username
    :return: true or false if the user exists
    """
    req_id = get_time()
    res = client_query.service.getUserInfo(requestId=req_id, userId=user)
    return not request_failed(res)

def request_failed(msg):
    """
    Determines if a request succeeded
    :param msg: the return msg
    :return: true or false if request was a success or failure
    """
    return msg.statusMessage != 'Success'

if not user_exists("spiker"):
    req_id = get_time()
    res = client_mgmt.service.createUser(requestId=req_id, userId="spiker")

for i in range(500):
    req_id = get_time()
    res1 = client_mgmt.service.setTemporaryPassword(requestId=req_id, userId="spiker")
    req_id = get_time()
    client_auth.service.authenticateUser(requestId=req_id, userId="spiker", otpAuthData=res1.temporaryPassword)
