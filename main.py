import db_data
import wazzup
import pandas as pd


def main():
    #file_n= 'employee.csv'
    #df = pd.read_csv(file_n)
    #phones = df["number"].tolist()
    #wazzup.sending_messages_for_employee(phones)

    num_list = db_data.get_number_info()
    wazzup.sending_messages(num_list)




if __name__ == "__main__":
    main()