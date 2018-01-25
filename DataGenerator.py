import csv
import datetime
import random

# Timestamp, Authentication Success, Device ID, Device Type, User ID



class Generator:

    # The number of days of data we should generate
    number_of_days = datetime.timedelta(days=7)

    # The day that should be the last day of data
    last_day = datetime.datetime.now()

    # The headers for our data
    HEADERS = ["Timestamp", "Authentication_Success", "Device_ID", "Device_Type", "User_ID"]

    # The rows of data that comprises our data set
    DATA = []

    # A list of the users for our fake service
    users = []

    # The number of users we will have
    number_of_users = 1000

    class Device:

        # The id of the device 6 digits long
        id = 0

        # The type of device this is {Mobile, Phone Call, Text, Key Fob}
        type_of_device = ""

        def __init__(self, type_of_device):
            self.id = random.randint(100000, 999999)
            self.type_of_device = type_of_device

    class User:

        # The id of this user 6 digits long
        id = 0

        # The list of devices that belong to this user
        devices = []

        def __init__(self):
            self.id = random.randint(100000, 999999)
            self.devices = []

            # Generate a list of devices for this user
            type_of_devices = ["Mobile App", "Phone Call", "Text", "Key Fob"]
            number_of_devices = random.randint(1, len(type_of_devices))

            for i in range(number_of_devices):
                index = random.randint(0, number_of_devices-(i+1))
                type_of_device = type_of_devices.pop(index)
                device = Generator.Device(type_of_device)
                self.devices.append(device)


    # DEPRICATED
    class Column:

        # The header for this column
        name = ""

        # The values this column can be, if empty this could be anything
        values = []


    def __init__(self):
        """
        Generate the users and their devices
        """
        for i in range(self.number_of_users):
            user = self.User()
            self.users.append(user)

    def set_number_of_days(self, n):
        """
        Sets the number of days we should generate data for
        :param n: the new number of days
        """
        self.number_of_days = datetime.timedelta(days=n)

    def set_last_day(self, d):
        """
        Sets the last day we should have data in the dataset
        :param d: the new day of type datetime.datetime
        """
        self.last_day = d

    def add_row(self, row):
        """
        Adds a row to the dataset
        :param row: The new row, gets appended to the end
        """
        self.DATA.append(row)

    # DEPRICATED
    def add_header(self, header_name, possible_values):
        """
        Adds a header to the dataset
        :param header_name:  The name of the header
        :param possible_values:  The possible values of the column
        """
        c = self.Column()
        c.name = header_name
        c.values = possible_values
        self.HEADERS.append(c)

    def generate_data(self):
        time = self.last_day - self.number_of_days
        while time < self.last_day:
            row = []
            seconds = random.randint(1, 60)
            time = time + datetime.timedelta(seconds=seconds)
            row.append(time)

            row.append(["SUCCESS", "SUCCESS", "SUCCESS", "SUCCESS", "SUCCESS", "SUCCESS", "FAIL"][random.randint(0,6)])

            user = self.users[random.randint(0,self.number_of_users-1)]
            device = user.devices[random.randint(0, len(user.devices)-1)]

            row.append(device.id)
            row.append(device.type_of_device)
            row.append(user.id)
            self.add_row(row)



def main():
    generator = Generator()
    generator.generate_data()


    with open("mock_data.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(generator.HEADERS)
        for row in generator.DATA:
            writer.writerow(row)



main()