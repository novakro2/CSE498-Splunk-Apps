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


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class DataGen:

    # Increase the rate based on the time of day or pattern we want to generate.
    # Keys are hours of the day
    # Values is base number of seconds between actions
    rate = {
        0: 600,
        1: 600,
        2: 600,
        3: 600,
        4: 600,
        5: 300,
        6: 300,
        7: 120,
        8: 100,
        9: 60,
        10: 30,
        11: 20,
        12: 10,
        13: 10,
        14: 10,
        15: 25,
        16: 40,
        17: 60,
        18: 100,
        19: 140,
        20: 300,
        21: 600,
        22: 600,
        23: 600
    }

    DAY = -1

    altered_hour = -1
    altered_rate = -1

    # List of user names that have been created
    users = []

    def __init__(self):
        f = open("users.txt", 'r')
        for line in f:
            user = line.strip("\n")
            self.users.append(user)
        f.close()
        print(self.users)

    def generate_users(self, x):
        """
        Generates x number of users
        :param x:
        :return:
        """
        for i in range(x):
            user = id_generator()
            self.create_user(user)

    def create_user(self, user):
        """
        Create user. Add username to list and to file
        :param user:
        """
        self.users.append(user)

        # Append user to user file
        f = open("users.txt", 'a')
        f.write(user+"\n")
        f.close()

        # Send req to vip to create user
        req_id = get_time()
        res = client_mgmt.service.createUser(requestId=req_id, userId=user)

    def auth_user(self, user, success):
        """
        Gen temp code and authenticate
        :param user:
        """
        req_id = get_time()
        res1 = client_mgmt.service.setTemporaryPassword(requestId=req_id, userId=user)
        if success:
            pw = res1.temporaryPassword
        else:
            pw = "FAKEPASSWORD"
        print(pw)
        #res2 = client_auth.service.authenticateUser(requestId=req_id, userId=user, otpAuthData=pw)

    def generate(self):

        c = 0
        while True:
            # Calculate time to sleep between commands
            hour = datetime.datetime.now().hour
            day = datetime.datetime.today().weekday()

            # Calculate daily modifiers
            if day != self.DAY:
                self.DAY = day

                # If it's a weekend
                if day in [5, 6]:
                    weekend_modifier = 2
                else:
                    weekend_modifier = 1
                daily_modifier = random.uniform(0.8, 1.2)
                daily_success_modifier = random.uniform(0.5, 2.0)

            # Calculate wait time until next command
            rate = self.rate[hour]
            random_modifier = random.uniform(0.0, 0.5)
            wait = [rate - (rate*random_modifier), rate + (rate*random_modifier)][random.randint(0, 1)]
            wait *= (daily_modifier*weekend_modifier)

            print(wait)

            # Randomly create user sometimes.
            create_user = (random.randint(1, int(wait)*100) == 1)

            # Create new user name
            if create_user:
                user = id_generator()
                self.create_user(user)

            # Get existing user name
            else:
                user = self.users[random.randint(0, len(self.users)-1)]

            # randomly determine if auth should be success
            success_auth = (random.randint(1, 100) > (7*daily_success_modifier))
            self.auth_user(user, success_auth)
            #time.sleep(wait)
            c += 1
            if c > 10:
                break


dg = DataGen()


dg.generate()


