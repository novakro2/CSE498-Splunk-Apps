from zeep import Client
from zeep import Transport
from requests import Session
import time

session = Session()
session.cert = ('C:/Users/Robert/Documents/CSE498/certificate.pem', 'C:/Users/Robert/Documents/CSE498/plainkey.pem')
transport = Transport(session=session)

client_mgmt = Client("C:/Users/Robert/Documents/CSE498/wsdl/vipuserservices-mgmt-1.8.wsdl", transport=transport)
client_auth = Client("C:/Users/Robert/Documents/CSE498/wsdl/vipuserservices-auth-1.8.wsdl", transport=transport)
client_query = Client("C:/Users/Robert/Documents/CSE498/wsdl/vipuserservices-query-1.8.wsdl", transport=transport)
client_api_auth = Client("C:/Users/Robert/Documents/CSE498/api/vip_auth.wsdl", transport=transport)

def user_exists(user):
    """
    Determines if a user exists
    :param user: the username
    :return: true or false if the user exists
    """
    req_id = get_time()
    res = client_query.service.getUserInfo(requestId=req_id, userId=user)
    return not request_failed(res)

def quit_program():
    """
    Closes the session before exiting the program
    """
    session.close()
    exit()

def request_failed(msg):
    """
    Determines if a request succeeded
    :param msg: the return msg
    :return: true or false if request was a success or failure
    """
    return msg.statusMessage != 'Success'

def get_time():
    """ Gets the time. Used for request ids"""
    return int(time.time())

def display_startup(x):
    """
    Displays startup message
    params: x A dummy parameter. Does nothing.
    """
    print("\nWhat would you like to do? (Enter number)")
    print("1. Authenticate User")
    print("2. Create User")
    print("3. Register Device (mobile VIP auth app)")
    print("4. Exit")
    answ = input("Enter choice: ")

    next = {
        '1': authenticate_user,
        '2': create_user,
        '3': register_device,
        '4': quit_program
    }[answ]()


def authenticate_user():
    """
    Authenticates a user
    """

    def use_credential(user):
        """
        Prompts user for the credential they are using
        """
        code = input("Please enter code: ")
        req_id = get_time()
        return client_auth.service.authenticateUser(requestId=req_id, userId=user, otpAuthData=code)


    def use_temp_code(user):
        """
        Generates a temp code for the user, doesn't promt for code
        """
        print("Generating temp code")
        req_id = get_time()
        res1 = client_mgmt.service.setTemporaryPassword(requestId=req_id, userId=user)
        return client_auth.service.authenticateUser(requestId=req_id, userId=user, otpAuthData=res1.temporaryPassword)

    user = input("Enter the user you would like to authenticate: ")
    # Need to check if user exists before we continue
    if not user_exists(user):
        print("User",user,"doesn't exist")
        display_startup(1)

    print("\nWhat would you like to do? (Enter number)")
    print("1. Use mobile VIP auth app")
    print("2. Generate a temporary code")
    print("3. Go back")
    answ = input("Enter choice: ")

    next = {
        '1': use_credential,
        '2': use_temp_code,
        '3': display_startup
    }[answ](user)

    if request_failed(next):
        print("Could not authenticate user")
    else:
        print("User authenticated")
    display_startup(1)

def create_user():
    """
    Creates a user
    """
    user = input("Enter the name of the user: ")

    # Check if the user already exists. If so just go back to main menu
    if user_exists(user):
        print("User",user,"already exists")
        display_startup(1)

    req_id = get_time()
    res = client_mgmt.service.createUser(requestId=req_id, userId=user)

    if request_failed(res):
        print("Couldnt create user",user)
    else:
        print("User",user,"created.")
    display_startup(1)

def register_device():

    user = input("Enter the name of the user: ")

    if not user_exists(user):
        print("User",user,"doesn't exist")
        display_startup(1)

    cred_id = (input("Enter the credential ID: ")).replace(" ", "")
    code = input("Enter the one time security code: ")

    req_id = get_time()
    res = client_mgmt.service.addCredential(requestId=req_id,
                                            userId=user,
                                            credentialDetail={'credentialType': "STANDARD_OTP",
                                                              'credentialId': cred_id},
                                            otpAuthData=code)

    if request_failed(res):
        print("Could not register device")
    else:
        print("Device registered")
    display_startup(1)

def main():
    display_startup(1)
    print("DONE")

main()