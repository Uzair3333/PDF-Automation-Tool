from utils.extract import extractor
def show_menu():
        print("\n--- PDF-Automatin-Tool ---\n")
        print("1. Merge PDFs\n2. Split PDF\n3. Extract Text from PDF\n4. Add Watermark\n5. Exit")
        try:
            user_choice = int(input("Enter your choice: "))
            return user_choice
        except ValueError:
            print("\n❌ Invalid value. Choose one of the above options.\n")
while True:

    choice = show_menu()

    if choice == 1:
        pass

    elif choice == 2:
        pass
    elif choice == 3:
        path = input("Enter path to the pdf: ")
        obj = extractor(path)
        obj.text_extractor()
        if obj.success == True:
            obj.text_saver()
            obj.output()
    elif choice == 4:
        pass
    elif choice == 5:
        print("\n👋 Good Bye!\n")
        break
    else:
        print("\n❌ Invalid input. Please select a valid option.\n")
        continue