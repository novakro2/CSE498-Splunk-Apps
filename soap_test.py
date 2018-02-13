from zeep import Client
from zeep import Transport
from requests import Session

session = Session()
session.cert = ('C:/Users/Robert/Documents/CSE498/certificate.pem', 'C:/Users/Robert/Documents/CSE498/plainkey.pem')
transport = Transport(session=session)

client = Client("C:/Users/Robert/Documents/CSE498/wsdl/vipuserservices-mgmt-1.8.wsdl", transport=transport)
# client.service.createUser(requestId="1234", userId="PYTHONTEST")

res = client.service.setTemporaryPassword(requestId="1234", userId="PYTHONTEST")
pw = res.temporaryPassword

client2 = Client("C:/Users/Robert/Documents/CSE498/wsdl/vipuserservices-auth-1.8.wsdl", transport=transport)
res = client2.service.authenticateUser(requestId="12345", userId="PYTHONTEST", otpAuthData="654789")
print(res)
