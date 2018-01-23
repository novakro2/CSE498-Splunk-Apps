import csv
import datetime



class Generator:

    # The number of days of data we should generate
    number_of_days = datetime.timedelta(days=7)

    # The day that should be the last day of data
    last_day = datetime.datetime.now()

    # The headers for our data, a list of columns
    HEADERS = []

    # The rows of data that comprises our data set
    DATA = []

    class Column:

        # The header for this column
        name = ""

        # The values this column can be, if empty this could be anything
        values = []

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
        x = 1


def main():
    d = datetime.timedelta(days=7)
    dt = datetime.datetime.now()
    print(d.days)
    print(dt-d)



main()