import db_data
import wazzup

def main():
    num_list = db_data.get_number_info()
    wazzup.sending_messages(num_list)




if __name__ == "__main__":
    main()