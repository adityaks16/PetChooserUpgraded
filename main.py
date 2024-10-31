# Aditya Kunapareddy
# Purpose: Enhanced Pet Chooser program with editing capabilities
# Added features:
# - Edit pet names and ages
# - Quit functionality at every menu
# - Improved error handling
import mysql.connector
from pets import Pets


def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="cbcradio.org",
            user="cbcradio_bds4",
            password="Cherry36Cat*",
            database="cbcradio_bds754_4"
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


def fetch_pets(connection):
    try:
        cursor = connection.cursor()
        query = """
        SELECT pets.id, pets.name, pets.age, owners.name, types.animal_type
        FROM pets
        JOIN owners ON pets.owner_id = owners.id
        JOIN types ON pets.animal_type_id = types.id
        """
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error fetching pets: {e}")
        return []


def update_pet(connection, pet_id, field, value):
    try:
        cursor = connection.cursor()
        query = f"UPDATE pets SET {field} = %s WHERE id = %s"
        cursor.execute(query, (value, pet_id))
        connection.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error updating pet: {e}")
        connection.rollback()
        return False


def display_pets(pets):
    print("\nPlease choose a pet from the list below:")
    for i, pet in enumerate(pets, 1):
        print(f"[{i}] {pet.get_name()}")
    print("[Q] Quit")


def get_user_choice(max_choice):
    while True:
        choice = input("Choice: ").strip().lower()
        if choice == 'q':
            return None
        try:
            choice = int(choice)
            if 1 <= choice <= max_choice:
                return choice
            else:
                print(f"Please enter a number between 1 and {max_choice}, or 'Q' to quit.")
        except ValueError:
            print("Invalid input. Please enter a number or 'Q' to quit.")


def get_menu_choice():
    while True:
        choice = input("\nWould you like to [C]ontinue, [Q]uit, or [E]dit this pet? ").strip().lower()
        if choice in ['c', 'q', 'e']:
            return choice
        print("Invalid input. Please enter 'C', 'Q', or 'E'.")


def edit_pet_info(connection, pet, pet_id):
    print(f"\nYou have chosen to edit {pet.get_name()}.")

    # Edit name
    new_name = input("New name: [ENTER == no change] ").strip()
    if new_name.lower() == 'q':
        return False
    if new_name:
        if update_pet(connection, pet_id, 'name', new_name):
            print(f"Pet's name has been updated to {new_name}.")
            pet._name = new_name

    # Edit age
    while True:
        new_age = input("New age: [ENTER == no change] ").strip()
        if new_age.lower() == 'q':
            return False
        if not new_age:
            break
        try:
            new_age = int(new_age)
            if new_age < 0:
                print("Age cannot be negative. Please try again.")
                continue
            if update_pet(connection, pet_id, 'age', new_age):
                print(f"Pet's age has been updated to {new_age}.")
                pet._age = new_age
            break
        except ValueError:
            print("Invalid age. Please enter a number or press ENTER to skip.")

    return True


def main():
    connection = None
    try:
        connection = connect_to_database()
        if not connection:
            return

        while True:
            # Fetch fresh pet data
            pet_data = fetch_pets(connection)
            if not pet_data:
                print("No pets found in the database.")
                return

            # Create pet objects
            pets = [Pets(name, age, owner, animal_type) for pet_id, name, age, owner, animal_type in pet_data]
            pet_ids = [pet[0] for pet in pet_data]  # Store pet IDs for database updates

            # Display pets and get choice
            display_pets(pets)
            choice = get_user_choice(len(pets))
            if choice is None:
                print("Thank you for using the Pet Chooser. Goodbye!")
                break

            # Display selected pet
            selected_pet = pets[choice - 1]
            selected_pet_id = pet_ids[choice - 1]
            print(f"\nYou have chosen {selected_pet}")

            # Get next action
            menu_choice = get_menu_choice()
            if menu_choice == 'q':
                print("Thank you for using the Pet Chooser. Goodbye!")
                break
            elif menu_choice == 'e':
                print("\nWhich pet would you like to edit?")
                display_pets(pets)
                edit_choice = get_user_choice(len(pets))
                if edit_choice is None:
                    print("Thank you for using the Pet Chooser. Goodbye!")
                    break

                pet_to_edit = pets[edit_choice - 1]
                pet_to_edit_id = pet_ids[edit_choice - 1]
                if not edit_pet_info(connection, pet_to_edit, pet_to_edit_id):
                    print("Edit cancelled. Thank you for using the Pet Chooser. Goodbye!")
                    break

    except mysql.connector.Error as e:
        print(f"A database error occurred: {str(e)}. The program will now exit.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}. The program will now exit.")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()