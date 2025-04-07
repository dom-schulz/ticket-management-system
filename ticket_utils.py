# ticket_utils.py
# This file contains utility functions for the Ticket Apprentice application
# Functionality includes:
# - Database operations (insert, delete, update)
# - UI element creation and management
# - Data validation
# - Search functionality
# - Result display in treeviews

# Function to populate result tree
def populate_result_tree(tree, query, columns):
    
    try:
        conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
        cursor = conn.cursor()

        cursor.execute(query)
        results = cursor.fetchall()

        # Clear existing data in the result tree
        for item in tree.get_children():
            tree.delete(item)

        # Populate the result tree with the query results
        for result in results:
            tree.insert("", "end", values=result)

    except mariadb.Error as e:
        print(f"Error: {e}")

    finally:
        try:
            # Close the connection and cursor in the 'finally' block
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except Exception as close_error:
            print(f"Error during closing: {close_error}")
            

# function to check date format to be used throughout
def is_valid_date_format(date_str):
    """
    Check if a given date string is in the format 'YYYY-MM-DD' and has valid components.

    Args:
        date_str (str): The date string to be validated.

    Returns:
        bool: True if the date string is in the correct format and has valid components,
              False otherwise.
    """ 
    
    try:
        # Check if the date string has the format YYYY-MM-DD
        year, month, day = map(int, date_str.split('-'))

        # Check if the year is prior to 2023
        if year >= 2023:
            return False

        # Check if the month is between 1 and 12
        if not 1 <= month <= 12:
            return False

        # Check if the day is between 1 and 31
        if not 1 <= day <= 31:
            return False

        return True
    except ValueError:
        return False


def insert_pick_table(event):
    
    # function definitions to only be used within the insert pick table function
    def insert_user(id_entry, name_entry, phone_entry, dob_entry, labels):
        """
        Insert a new user into the 'Users' table.

        Args:
            id_entry (Entry): Entry widget for the user ID.
            name_entry (Entry): Entry widget for the user's name.
            phone_entry (Entry): Entry widget for the user's phone number.
            dob_entry (Entry): Entry widget for the user's date of birth.
            labels: List of labels to be destroyed at end of function

        Note:
            The function assumes a MariaDB database connection and handles validation,
            insertion, and widget destruction upon a successful insert.

        Returns:
            True or False (depending on whether the insertion occured)
        """
        
        # Extract values from entry widgets
        id = id_entry.get()
        name = name_entry.get()
        phone = phone_entry.get()
        dob = dob_entry.get()

        # Database connection and validation
        try:
            conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
            cursor = conn.cursor()
            
            # Check if ID already exists to prevent duplicates
            check_query = "SELECT id FROM Users WHERE id = %s"
            cursor.execute(check_query, (id,))
            existing_id = cursor.fetchone()

            # Validation checks for form inputs
            if existing_id:
                MessageBox.showinfo("Insert Status:", f"ID {id} already exists. Please select a new ID.")
                
            elif id == '' or name == '' or phone == '' or dob == '':
                MessageBox.showinfo("Insert Status:", "All Fields are required")
            elif not is_valid_date_format(dob):
                MessageBox.showinfo("Insert Status:", "Invalid date format or invalid values. Please use YYYY-MM-DD.")
            
            else:                                                              
                # Insert the new user if all validations pass
                insert_query = "INSERT INTO Users (id, user_name, phone_number, date_of_birth) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_query, (id, name, phone, dob))
                conn.commit()  # need to commit for insert delete etc. 
                
                MessageBox.showinfo("Insert Status", "Inserted Successfully")
                
                # Clean up UI elements after insertion
                id_entry.destroy()
                name_entry.destroy()
                phone_entry.destroy()
                dob_entry.destroy()
                for label in labels:
                    label.destroy()

                cursor.close()
                conn.close()
                return True
        except Exception as e:
            print(f"Error: {e}")
            MessageBox.showerror("Error", f"Error: {e}")
            cursor.close()
            conn.close()
            return False

    def insert_user_and_destroy(id_entry, name_entry, phone_entry, dob_entry, labels, insert_button):
        """
        Insert a new user into the 'Users' table and destroy specified widgets upon success.

        Args:
            id_entry (Entry): Entry widget for the user ID.
            name_entry (Entry): Entry widget for the user's name.
            phone_entry (Entry): Entry widget for the user's phone number.
            dob_entry (Entry): Entry widget for the user's date of birth.
            labels (list): List of labels to be destroyed at the end of the function.
            insert_button (Button): The insert button widget to be destroyed.

        Returns:
            None
        """
        
        success = insert_user(id_entry, name_entry, phone_entry, dob_entry, labels)
        if success:
            insert_button.destroy()
            return
        else:
            return

    def insert_venue(venue_name_entry, city_entry, capacity_entry, labels):
        """
        Insert a new venue into the 'Venue' table.

        Args:
            venue_name_entry (Entry): Entry widget for the venue name.
            city_entry (Entry): Entry widget for the city.
            capacity_entry (Entry): Entry widget for the capacity.
            labels (list): List of labels to be destroyed at the end of the function.

        Note:
            The function assumes a MariaDB database connection and handles validation,
            insertion, and widget destruction upon a successful insert.

        Returns:
            None
        """
        
        venue_name = venue_name_entry.get()
        city = city_entry.get()
        capacity = capacity_entry.get()

        try:
            conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
            cursor = conn.cursor()

            check_query = "SELECT venue_name FROM Venue WHERE venue_name = %s"
            cursor.execute(check_query, (venue_name,))
            existing_venue_name = cursor.fetchone()

            if existing_venue_name:
                MessageBox.showinfo("Insert Status:", f"Venue name {venue_name} already exists. Please select a new name.")
            elif venue_name == '' or city == '' or capacity == '':
                MessageBox.showinfo("Insert Status:", "All Fields are required")
            else:
                # Execute the insert query
                insert_query = "INSERT INTO Venue (venue_name, city, capacity) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (venue_name, city, capacity))
                conn.commit()

                # Show success message
                MessageBox.showinfo("Insert Status", "Inserted Successfully")

                # Clear output
                venue_name_entry.destroy()
                city_entry.destroy()
                capacity_entry.destroy()
                for label in labels:
                    label.destroy()

                return True
        except Exception as e:
            print(f"Error: {e}")
            MessageBox.showerror("Error", f"Error: {e}")
            cursor.close()
            conn.close()
            return False

    def insert_venue_and_destroy(venue_name_entry, city_entry, capacity_entry, labels, insert_button):
        """
        Wrapper function for insert_venue, destroying the insert button afterward.

        Args:
            venue_name_entry (Entry): Entry widget for the venue name.
            city_entry (Entry): Entry widget for the city.
            capacity_entry (Entry): Entry widget for the capacity.
            labels (list): List of labels to be destroyed at the end of the function.
            insert_button (Button): The insert button widget to be destroyed.

        Returns:
            None
        """
        
        success = insert_venue(venue_name_entry, city_entry, capacity_entry, labels)
        if success:
            insert_button.destroy()
            return
        else:
            return

    def insert_event(event_name_entry, venue_name_entry, event_date_entry, start_time_entry, labels):
        """
        Insert a new event into the 'Events' table.

        Args:
            event_name_entry (Entry): Entry widget for the event name.
            venue_name_entry (Entry): Entry widget for the venue name.
            city_entry (Entry): Entry widget for the city.
            event_date_entry (Entry): Entry widget for the event date.
            start_time_entry (Entry): Entry widget for the start time.
            labels (list): List of labels to be destroyed at the end of the function.

        Note:
            The function assumes a MariaDB database connection and handles validation,
            insertion, and widget destruction upon a successful insert.

        Returns:
            True or False (depending on whether the insertion was completed)
        """
        
        event_name = event_name_entry.get()
        venue_name = venue_name_entry.get()
        event_date = event_date_entry.get()
        start_time = start_time_entry.get()

        try:
            conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
            cursor = conn.cursor()

            check_venue_query = "SELECT venue_name FROM Venue WHERE venue_name = %s"
            cursor.execute(check_venue_query, (venue_name,))
            existing_venue_name = cursor.fetchone()

            if not existing_venue_name:
                MessageBox.showinfo("Insert Status:", f"Venue name {venue_name} does not exist. Please select a valid venue. You may have to create a venue first in 'Venue'")
            elif event_name == '' or venue_name == '' or event_date == '' or start_time == '':
                MessageBox.showinfo("Insert Status:", "All Fields are required")
            else:
                insert_query = "INSERT INTO Events (event_name, venue_name, event_date, start_time) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_query, (event_name, venue_name, event_date, start_time))
                conn.commit()

                MessageBox.showinfo("Insert Status", "Inserted Successfully")

                # Clear output
                event_name_entry.destroy()
                venue_name_entry.destroy()
                event_date_entry.destroy()
                start_time_entry.destroy()
                for label in labels:
                    label.destroy()
                cursor.close()
                conn.close()
                return True
        except Exception as e:
            print(f"Error: {e}")
            MessageBox.showerror("Error", f"Error: {e}")
            cursor.close()
            conn.close()
            return False

    def insert_event_and_destroy(event_name_entry, venue_name_entry, event_date_entry, start_time_entry, labels, insert_button):
        """
        Wrapper function for insert_event, destroying the insert button afterward.

        Args:
            event_name_entry (Entry): Entry widget for the event name.
            venue_name_entry (Entry): Entry widget for the venue name.
            city_entry (Entry): Entry widget for the city.
            event_date_entry (Entry): Entry widget for the event date.
            start_time_entry (Entry): Entry widget for the start time.
            labels (list): List of labels to be destroyed at the end of the function.
            insert_button (Button): The insert button widget to be destroyed.

        Returns:
            None
        """
        
        success = insert_event(event_name_entry, venue_name_entry, event_date_entry, start_time_entry, labels)
        if success: 
            insert_button.destroy()
            return
        else:
            return

    def insert_individual_performer(stage_name_entry, individual_name_entry, age_entry, labels):
        """
        Insert a new individual performer into the 'IndividualPerformers' table.

        Args:
            stage_name_entry (Entry): Entry widget for the stage name.
            individual_name_entry (Entry): Entry widget for the individual name.
            age_entry (Entry): Entry widget for the age.
            labels (list): List of labels to be destroyed at the end of the function.

        Note:
            The function assumes a MariaDB database connection and handles validation,
            insertion, and widget destruction upon a successful insert.

        Returns:
            True or False (depending on whether the insertion was completed)
        """
        stage_name = stage_name_entry.get()
        individual_name = individual_name_entry.get()
        age = age_entry.get()

        try:
            conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
            cursor = conn.cursor()

            check_stage_query = "SELECT stage_name FROM IndividualPerformers WHERE stage_name = %s"
            cursor.execute(check_stage_query, (stage_name,))
            existing_stage_name = cursor.fetchone()

            # Validate age as an integer between 0 and 120
            try:
                age = int(age)
                if not 0 <= age <= 120:
                    raise ValueError("Age must be between 0 and 120")
            except ValueError:
                MessageBox.showinfo("Insert Status:", "Age must be a valid integer between 0 and 120")
                return False

            if existing_stage_name:
                MessageBox.showinfo("Insert Status:", f"Stage name {stage_name} already exists. Please select a new name.")
            elif stage_name == '' or individual_name == '' or age == '':
                MessageBox.showinfo("Insert Status:", "All Fields are required")
            else:
                insert_query = "INSERT INTO IndividualPerformers (stage_name, individual_name, age) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (stage_name, individual_name, age))
                conn.commit()

                MessageBox.showinfo("Insert Status", "Inserted Successfully")

                # Clear output
                stage_name_entry.destroy()
                individual_name_entry.destroy()
                age_entry.destroy()
                for label in labels:
                    label.destroy()

                return True

        except Exception as e:
            print(f"Error: {e}")
            MessageBox.showerror("Error", f"Error: {e}")

        finally:
            cursor.close()
            conn.close()

        return False

    def insert_individual_performer_and_destroy(stage_name_entry, individual_name_entry, age_entry, labels, insert_button):
        """
        Wrapper function for insert_individual_performer, destroying the insert button afterward.

        Args:
            stage_name_entry (Entry): Entry widget for the stage name.
            individual_name_entry (Entry): Entry widget for the individual name.
            age_entry (Entry): Entry widget for the age.
            labels (list): List of labels to be destroyed at the end of the function.
            insert_button (Button): The insert button widget to be destroyed.

        Returns:
            None
        """
        success = insert_individual_performer(stage_name_entry, individual_name_entry, age_entry, labels)
        if success:
            insert_button.destroy()
            return
        else:
            return

    def insert_group(group_name_entry, founded_entry, labels):
        """
        Insert a new group into the 'Groups' table.

        Args:
            group_name_entry (Entry): Entry widget for the group name.
            founded_entry (Entry): Entry widget for the founded date.
            labels (list): List of labels to be destroyed at the end of the function.

        Note:
            The function assumes a MariaDB database connection and handles validation,
            insertion, and widget destruction upon a successful insert.

        Returns:
            True or False (depending on whether the insertion was completed)
        """
        group_name = group_name_entry.get()
        founded = founded_entry.get()

        try:
            conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
            cursor = conn.cursor()

            check_group_query = "SELECT group_name FROM Groups WHERE group_name = %s"
            cursor.execute(check_group_query, (group_name,))
            existing_group_name = cursor.fetchone()

            # Validate founded as a valid date format
            if not is_valid_date_format(founded):
                MessageBox.showinfo("Insert Status:", "Invalid founded date format. Please use YYYY-MM-DD.")
                return False

            if existing_group_name:
                MessageBox.showinfo("Insert Status:", f"Group name {group_name} already exists. Please select a new name.")
            elif group_name == '' or founded == '':
                MessageBox.showinfo("Insert Status:", "All Fields are required")
            else:
                insert_query = "INSERT INTO Groups (group_name, founded) VALUES (%s, %s)"
                cursor.execute(insert_query, (group_name, founded))
                conn.commit()

                MessageBox.showinfo("Insert Status", "Inserted Successfully")

                # Clear output
                group_name_entry.destroy()
                founded_entry.destroy()
                for label in labels:
                    label.destroy()

                return True

        except Exception as e:
            print(f"Error: {e}")
            MessageBox.showerror("Error", f"Error: {e}")

        finally:
            cursor.close()
            conn.close()

        return False

    def insert_group_and_destroy(group_name_entry, founded_entry, labels, insert_button):
        """
        Wrapper function for insert_group, destroying the insert button afterward.

        Args:
            group_name_entry (Entry): Entry widget for the group name.
            founded_entry (Entry): Entry widget for the founded date.
            labels (list): List of labels to be destroyed at the end of the function.
            insert_button (Button): The insert button widget to be destroyed.

        Returns:
            None
        """
        
        success = insert_group(group_name_entry, founded_entry, labels)
        if success: 
            insert_button.destroy()
            return
        else:
            return

    def insert_membership(stage_name_entry, group_name_entry, labels):
        """
        Insert a new membership into the 'Memberships' table.

        Args:
            stage_name_entry (Entry): Entry widget for the stage name.
            group_name_entry (Entry): Entry widget for the group name.
            labels (list): List of labels to be destroyed at the end of the function.

        Note:
            The function assumes a MariaDB database connection and handles validation,
            insertion, and widget destruction upon a successful insert.

        Returns:
            True or False (depending on whether the insertion was completed)
        """
        stage_name = stage_name_entry.get()
        group_name = group_name_entry.get()

        try:
            conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
            cursor = conn.cursor()

            check_stage_query = "SELECT stage_name FROM IndividualPerformers WHERE stage_name = %s"
            cursor.execute(check_stage_query, (stage_name,))
            existing_stage_name = cursor.fetchone()

            check_group_query = "SELECT group_name FROM Groups WHERE group_name = %s"
            cursor.execute(check_group_query, (group_name,))
            existing_group_name = cursor.fetchone()
            
            check_membership_query = "SELECT * FROM Memberships WHERE stage_name = %s AND group_name = %s"
            cursor.execute(check_membership_query, (stage_name, group_name))
            existing_membership = cursor.fetchone()


            if existing_membership:
                MessageBox.showinfo("Insert Status:", f"Membership for {stage_name} and {group_name} already exists.")
            elif not existing_stage_name:
                MessageBox.showinfo("Insert Status:", f"Stage name {stage_name} does not exist. Please select a valid stage name. You may have to create a performer in 'IndividualPerformers'")
            elif not existing_group_name:
                MessageBox.showinfo("Insert Status:", f"Group name {group_name} does not exist. Please select a valid group name. You may have to create a group in 'Groups'")
            else:
                insert_query = "INSERT INTO Memberships (stage_name, group_name) VALUES (%s, %s)"
                cursor.execute(insert_query, (stage_name, group_name))
                conn.commit()

                MessageBox.showinfo("Insert Status", "Inserted Successfully")

                # Clear output
                stage_name_entry.destroy()
                group_name_entry.destroy()
                for label in labels:
                    label.destroy()

                return True

        except Exception as e:
            print(f"Error: {e}")
            MessageBox.showerror("Error", f"Error: {e}")

        finally:
            cursor.close()
            conn.close()

        return False

    def insert_membership_and_destroy(stage_name_entry, group_name_entry, labels, insert_button):
        """
        Wrapper function for insert_membership, destroying the insert button afterward.

        Args:
            stage_name_entry (Entry): Entry widget for the stage name.
            group_name_entry (Entry): Entry widget for the group name.
            labels (list): List of labels to be destroyed at the end of the function.
            insert_button (Button): The insert button widget to be destroyed.

        Returns:
            None
        """
        success = insert_membership(stage_name_entry, group_name_entry, labels)
        if success:
            insert_button.destroy()
            return
        else:
            return

    def insert_performance_list(event_name_entry, group_name_entry, labels):
        """
        Insert a new performance into the 'PerformanceList' table.

        Args:
            event_name_entry (Entry): Entry widget for the event name.
            group_name_entry (Entry): Entry widget for the group name.
            labels (list): List of labels to be destroyed at the end of the function.

        Note:
            The function assumes a MariaDB database connection and handles validation,
            insertion, and widget destruction upon a successful insert.

        Returns:
            True or False (depending on whether the insertion was completed)
        """
        event_name = event_name_entry.get()
        group_name = group_name_entry.get()

        try:
            conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
            cursor = conn.cursor()
            
            
            check_entry_query = "SELECT * FROM PerformanceList WHERE event_name = %s AND group_name = %s"
            cursor.execute(check_entry_query, (event_name, group_name))
            existing_entry = cursor.fetchone()

            if existing_entry:
                MessageBox.showinfo("Insert Status:", "Entry already exists. Please provide unique Event and Group names.")
                return False

            
            check_event_query = "SELECT event_name FROM Events WHERE event_name = %s"
            cursor.execute(check_event_query, (event_name,))
            existing_event_name = cursor.fetchone()

            check_group_query = "SELECT group_name FROM Groups WHERE group_name = %s"
            cursor.execute(check_group_query, (group_name,))
            existing_group_name = cursor.fetchone()

            if not existing_event_name:
                MessageBox.showinfo("Insert Status:", f"Event name {event_name} does not exist. Please select a valid event. You may have to create an Event first in 'Events'")
            elif not existing_group_name:
                MessageBox.showinfo("Insert Status:", f"Group name {group_name} does not exist. Please select a valid group. You may have to create a Group first in 'Groups'")
            else:
                insert_query = "INSERT INTO PerformanceList (event_name, group_name) VALUES (%s, %s)"
                cursor.execute(insert_query, (event_name, group_name))
                conn.commit()

                MessageBox.showinfo("Insert Status", "Inserted Successfully")

                # Clear output
                event_name_entry.destroy()
                group_name_entry.destroy()
                for label in labels:
                    label.destroy()

                return True

        except Exception as e:
            print(f"Error: {e}")
            MessageBox.showerror("Error", f"Error: {e}")

        finally:
            cursor.close()
            conn.close()

        return False

    def insert_performance_and_destroy(event_name_entry, group_name_entry, labels, insert_button):
        """
        Wrapper function for insert_performance_list, destroying the insert button afterward.

        Args:
            event_name_entry (Entry): Entry widget for the event name.
            group_name_entry (Entry): Entry widget for the group name.
            labels (list): List of labels to be destroyed at the end of the function.
            insert_button (Button): The insert button widget to be destroyed.

        Returns:
            None
        """
        success = insert_performance_list(event_name_entry, group_name_entry, labels)
        if success:
            insert_button.destroy()
            return
        else:
            return

    def insert_ticket(event_name_entry, purchased_by_entry, price_entry, labels):
        """
        Insert a new ticket into the 'Tickets' table.

        Args:
            event_name_entry (Entry): Entry widget for the event name.
            purchased_by_entry (Entry): Entry widget for the user ID purchasing the ticket.
            price_entry (Entry): Entry widget for the ticket price.
            labels (list): List of labels to be destroyed at the end of the function.

        Note:
            The function assumes a MariaDB database connection and handles validation,
            insertion, and widget destruction upon a successful insert.
            Ticket ID will be generated.

        Returns:
            True or False (depending on whether the insertion was completed)
        """
        event_name = event_name_entry.get()
        purchased_by = purchased_by_entry.get()
        price = price_entry.get()

        try:
            conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
            cursor = conn.cursor()

            check_event_query = "SELECT event_name FROM Events WHERE event_name = %s"
            cursor.execute(check_event_query, (event_name,))
            existing_event_name = cursor.fetchone()

            if purchased_by.upper() != 'N/A':
                check_user_query = "SELECT id FROM Users WHERE id = %s"
                cursor.execute(check_user_query, (purchased_by,))
                existing_user_id = cursor.fetchone()

                if not existing_user_id:
                    MessageBox.showinfo("Insert Status:", f"User with ID {purchased_by} does not exist. Please select a valid user.")
                    return False

            # Validate price as a positive float
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be a positive value")
            except ValueError:
                MessageBox.showinfo("Insert Status:", "Price must be a valid positive number")
                return False

            if not existing_event_name:
                MessageBox.showinfo("Insert Status:", f"Event name {event_name} does not exist. Please select a valid event.")
            elif event_name == '' or price == '':
                MessageBox.showinfo("Insert Status:", "All Fields are required")
            else:
                # Get the maximum ID for the specified event
                max_id_query = "SELECT MAX(id) FROM Tickets WHERE event_name = %s"
                cursor.execute(max_id_query, (event_name,))
                max_id_result = cursor.fetchone()
                max_id = max_id_result[0] if max_id_result[0] is not None else 0

                # Generate a new ID
                new_id = max_id + 1

                insert_query = "INSERT INTO Tickets (id, event_name, purchased_by, price) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_query, (new_id, event_name, purchased_by if purchased_by.upper() != 'N/A' else None, price))
                conn.commit()

                MessageBox.showinfo("Insert Status", f"Inserted Successfully. Generated Ticket ID: {new_id}")

                # Clear output
                event_name_entry.destroy()
                purchased_by_entry.destroy()
                price_entry.destroy()
                for label in labels:
                    label.destroy()

                return True

        except Exception as e:
            print(f"Error: {e}")
            MessageBox.showerror("Error", f"Error: {e}")

        finally:
            cursor.close()
            conn.close()

    def insert_ticket_and_destroy(event_name_entry, purchased_by_entry, price_entry, labels, insert_button):
        """
        Wrapper function for insert_ticket, destroying the insert button afterward.

        Args:
            event_name_entry (Entry): Entry widget for the event name.
            purchased_by_entry (Entry): Entry widget for the user ID purchasing the ticket.
            price_entry (Entry): Entry widget for the ticket price.
            labels (list): List of labels to be destroyed at the end of the function.
            insert_button (Button): The insert button widget to be destroyed.

        Returns:
            None
        """
        success = insert_ticket(event_name_entry, purchased_by_entry, price_entry, labels)
        if success:
            insert_button.destroy()
            return
        else:
            return
    
    
    combobox_index = tab2.winfo_children().index(table_drop_down)

    # Destroy only the widgets below the combobox
    for widget in tab2.winfo_children()[combobox_index + 1:]:
        widget.destroy()
    
    
    for table_name in all_tables:
        if table_drop_down.get() == table_name:

            selected_table = table_name
            if selected_table == 'Users':
                
                top_label = Label(tab2, text='Please Input User Information', font=('bold', 15))
                top_label.place(x=80, y=30)
                id_label = Label(tab2, text='Enter ID (int)', font= ('bold', 10)) 
                id_label.place(x=20, y=60)
                name_label = Label(tab2, text='Enter Name (str)', font= ('bold', 10)) 
                name_label.place(x=20, y=90) 
                phone_label = Label(tab2, text='Enter Phone (int)', font= ('bold', 10)) 
                phone_label.place(x=20, y=120)
                dob_label = Label(tab2, text='Enter DOB (YYYY-MM-DD)', font= ('bold', 10))
                dob_label.place(x=20, y=150)

                id_entry = Entry(tab2) 
                id_entry.place(x=250, y=60) 

                name_entry = Entry(tab2)
                name_entry.place(x=250, y=90)
                
                phone_entry = Entry(tab2) 
                phone_entry.place(x=250, y=120) 

                dob_entry = Entry(tab2) 
                dob_entry.place(x=250, y=150) 

                label_list = [top_label, id_label, name_label, phone_label, dob_label]
                
                insert_button = Button(tab2, text="insert", font=("italic", 10), bg="white", command=lambda: insert_user_and_destroy(id_entry, name_entry, phone_entry, dob_entry, label_list, insert_button)) 
                insert_button.place(x=20, y=250) 
            
            elif selected_table == 'Venue':
                top_label = Label(tab2, text='Please Input Venue Information', font=('bold', 15))
                top_label.place(x=80, y=30)
                venue_name_label = Label(tab2, text='Enter Venue Name', font=('bold', 10))
                venue_name_label.place(x=20, y=60)
                city_label = Label(tab2, text='Enter City', font=('bold', 10))
                city_label.place(x=20, y=90)
                capacity_label = Label(tab2, text='Enter Capacity', font=('bold', 10))
                capacity_label.place(x=20, y=120)

                venue_name_entry = Entry(tab2)
                venue_name_entry.place(x=250, y=60)

                city_entry = Entry(tab2)
                city_entry.place(x=250, y=90)

                capacity_entry = Entry(tab2)
                capacity_entry.place(x=250, y=120)

                label_list = [top_label, venue_name_label, city_label, capacity_label]

                insert_button = Button(tab2, text="insert", font=("italic", 10), bg="white", command=lambda: insert_venue_and_destroy(venue_name_entry, city_entry, capacity_entry, label_list, insert_button))
                insert_button.place(x=20, y=250)
            
            elif selected_table == 'Events':
                top_label = Label(tab2, text='Please Input Event Information', font=('bold', 15))
                top_label.place(x=80, y=30)
                event_name_label = Label(tab2, text='Enter Event Name (str)', font=('bold', 10))
                event_name_label.place(x=20, y=60)
                venue_name_label = Label(tab2, text='Enter Venue Name (str)', font=('bold', 10))
                venue_name_label.place(x=20, y=90)
                event_date_label = Label(tab2, text='Enter Event Date (YYYY-MM-DD)', font=('bold', 10))
                event_date_label.place(x=20, y=120)
                start_time_label = Label(tab2, text='Enter Start Time (HH:MM)', font=('bold', 10))
                start_time_label.place(x=20, y=150)

                event_name_entry = Entry(tab2)
                event_name_entry.place(x=250, y=60)

                venue_name_entry = Entry(tab2)
                venue_name_entry.place(x=250, y=90)


                event_date_entry = Entry(tab2)
                event_date_entry.place(x=250, y=120)

                start_time_entry = Entry(tab2)
                start_time_entry.place(x=250, y=150)

                label_list = [top_label, event_name_label, venue_name_label, event_date_label, start_time_label]

                insert_button = Button(tab2, text="insert", font=("italic", 10), bg="white", command=lambda: insert_event_and_destroy(event_name_entry, venue_name_entry, event_date_entry, start_time_entry, label_list, insert_button))
                insert_button.place(x=20, y=250)  
                
            elif selected_table == 'IndividualPerformers':
                top_label = Label(tab2, text='Please Input Performer Information', font=('bold', 15))
                top_label.place(x=80, y=30)
                stage_name_label = Label(tab2, text='Enter Stage Name (str)', font=('bold', 10))
                stage_name_label.place(x=20, y=60)
                individual_name_label = Label(tab2, text='Enter Individual Name (str)', font=('bold', 10))
                individual_name_label.place(x=20, y=90)
                age_label = Label(tab2, text='Enter Age (int)', font=('bold', 10))
                age_label.place(x=20, y=120)

                stage_name_entry = Entry(tab2)
                stage_name_entry.place(x=250, y=60)

                individual_name_entry = Entry(tab2)
                individual_name_entry.place(x=250, y=90)

                age_entry = Entry(tab2)
                age_entry.place(x=250, y=120)

                label_list = [top_label, stage_name_label, individual_name_label, age_label]

                insert_button = Button(tab2, text="insert", font=("italic", 10), bg="white",
                                       command=lambda: insert_individual_performer_and_destroy(stage_name_entry, individual_name_entry, age_entry, label_list, insert_button))
                insert_button.place(x=20, y=250)
            
            elif selected_table == 'Groups':
                top_label = Label(tab2, text='Please Input Group Information', font=('bold', 15))
                top_label.place(x=80, y=30)

                group_name_label = Label(tab2, text='Enter Group Name', font=('bold', 10))
                group_name_label.place(x=20, y=60)

                founded_label = Label(tab2, text='Enter Founded Date (YYYY-MM-DD)', font=('bold', 10))
                founded_label.place(x=20, y=90)

                group_name_entry = Entry(tab2)
                group_name_entry.place(x=250, y=60)

                founded_entry = Entry(tab2)
                founded_entry.place(x=250, y=90)

                label_list = [top_label, group_name_label, founded_label]

                insert_button = Button(tab2, text="insert", font=("italic", 10), bg="white", command=lambda: insert_group_and_destroy(group_name_entry, founded_entry, label_list, insert_button))
                insert_button.place(x=20, y=250)
            
            elif selected_table == 'Memberships':
                top_label = Label(tab2, text='Please Input Membership Information', font=('bold', 15))
                top_label.place(x=80, y=30)
                stage_name_label = Label(tab2, text='Enter Stage Name (str)', font=('bold', 10))
                stage_name_label.place(x=20, y=60)
                group_name_label = Label(tab2, text='Enter Group Name (str)', font=('bold', 10))
                group_name_label.place(x=20, y=90)

                stage_name_entry = Entry(tab2)
                stage_name_entry.place(x=250, y=60)

                group_name_entry = Entry(tab2)
                group_name_entry.place(x=250, y=90)

                label_list = [top_label, stage_name_label, group_name_label]

                insert_button = Button(tab2, text="insert", font=("italic", 10), bg="white", command=lambda: insert_membership_and_destroy(stage_name_entry, group_name_entry, label_list, insert_button))
                insert_button.place(x=20, y=250)
            
            elif selected_table == 'PerformanceList':
                top_label = Label(tab2, text='Please Input Performance Information', font=('bold', 15))
                top_label.place(x=80, y=30)

                event_name_label = Label(tab2, text='Enter Event Name (str)', font=('bold', 10))
                event_name_label.place(x=20, y=60)
                group_name_label = Label(tab2, text='Enter Group Name (str)', font=('bold', 10))
                group_name_label.place(x=20, y=90)

                event_name_entry = Entry(tab2)
                event_name_entry.place(x=250, y=60)

                group_name_entry = Entry(tab2)
                group_name_entry.place(x=250, y=90)

                label_list = [top_label, event_name_label, group_name_label]

                insert_button = Button(tab2, text="insert", font=("italic", 10), bg="white",
                                       command=lambda: insert_performance_and_destroy(event_name_entry, group_name_entry, label_list, insert_button))
                insert_button.place(x=20, y=250)
            
            elif selected_table == 'Tickets':
                top_label = Label(tab2, text='Please Input Ticket Information', font=('bold', 15))
                top_label.place(x=80, y=30)
                event_name_label = Label(tab2, text='Enter Event Name', font=('bold', 10))
                event_name_label.place(x=20, y=60)
                purchased_by_label = Label(tab2, text="Enter Purchased By (User ID or 'N/A')", font=('bold', 10))
                purchased_by_label.place(x=20, y=90)
                price_label = Label(tab2, text='Enter Ticket Price', font=('bold', 10))
                price_label.place(x=20, y=120)

                event_name_entry = Entry(tab2)
                event_name_entry.place(x=250, y=60)

                purchased_by_entry = Entry(tab2)
                purchased_by_entry.place(x=250, y=90)

                price_entry = Entry(tab2)
                price_entry.place(x=250, y=120)

                # Note about ticket ID generation
                note_label = Label(tab2, text='Note: Ticket ID will be generated.', font=('italic', 10), fg='gray')
                note_label.place(x=20, y=150)
                
                label_list = [top_label, event_name_label, purchased_by_label, price_label, note_label]

                insert_button = Button(tab2, text="insert", font=("italic", 10), bg="white",
                                       command=lambda: insert_ticket_and_destroy(event_name_entry, purchased_by_entry,
                                                                                price_entry, label_list, insert_button))
                insert_button.place(x=20, y=250)
                
    return


def delete_pick_table(event):
      
    def delete_user_and_destroy(user_id, labels, delete_button):
        """
        Wrapper function for delete_user_by_id, destroying the delete button afterward.

        Args:
            user_id (int): The user ID for the user to be deleted.
            labels (list): List of labels to be destroyed at the end of the function.
            delete_button (Button): The delete button widget to be destroyed.

        Returns:
            True or False (depending on whether deletion was successful)
        """
        # Inner function for handling the actual deletion
        def delete_user(user_id, labels, delete_button):
            """
            Delete a user from the 'Users' table based on the user ID.

            Args:
                user_id (int): The user ID for the user to be deleted.
                labels (list): List of labels to be destroyed at the end of the function.
                delete_button (Button): The delete button widget to be destroyed.

            Returns:
                None
            """
            # Extract the user ID from the entry widget
            id = user_id.get()

            try:
                # Establish database connection
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                # Check if the user exists before attempting deletion
                check_query = "SELECT id FROM Users WHERE id = %s"
                cursor.execute(check_query, (id,))
                existing_id = cursor.fetchone()

                if user_info:
                    check_tickets_query = "SELECT * FROM Tickets WHERE purchased_by = %s"
                    cursor.execute(check_tickets_query, (user_id,))
                    tickets_info = cursor.fetchone()
                    
                    if tickets_info:
                        MessageBox.showinfo("Delete Status", f"Cannot delete user with ID {user_id} because they have entries in the 'Tickets' table.\nYou must delete all tickets associated with the user prior to deletion")
                        cursor.close()
                        conn.close()
                        return False
                    
                    # Display user information for confirmation
                    confirmation = MessageBox.askyesno("Delete Confirmation",
                                                    f"Do you want to delete the following user?\n{user_info}")

                    if confirmation:
                        # Execute the delete query
                        delete_query = "DELETE FROM Users WHERE id = %s"
                        cursor.execute(delete_query, (user_id, ))
                        conn.commit()

                        MessageBox.showinfo("Delete Status", "User deleted successfully.")

                        # Destroy old widgets
                        for label in labels:
                            label.destroy()
                        delete_button.destroy()
                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Delete Status", f"User with ID {user_id} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False
        
        success = delete_user(user_id, labels, delete_button)
        if success:
            delete_button.destroy()
            return
        else:
            return

    def delete_event_and_destroy(event_name, labels, delete_button):
        """
        Wrapper function for delete_event, destroying the delete button afterward.

        Args:
            event_name (str): The event name for the event to be deleted.
            labels (list): List of labels to be destroyed at the end of the function.
            delete_button (Button): The delete button widget to be destroyed.

        Returns:
            None
        """
        
        def delete_event(event_name, labels, delete_button):
            """
            Delete an event from the 'Events' table based on the event name.

            Args:
                event_name (str): The event name for the event to be deleted.
                labels (list): List of labels to be destroyed at the end of the function.
                delete_button (Button): The delete button widget to be destroyed.

            Returns:
                True or False (depending on whether deletion was successful)
            """
            
            try:
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                check_event_query = "SELECT * FROM Events WHERE event_name = %s"
                cursor.execute(check_event_query, (event_name,))
                event_info = cursor.fetchone()

                if event_info:
                    # Display event information for confirmation
                    confirmation = MessageBox.askyesno("Delete Confirmation",
                                                    f"Do you want to delete the following event?\n\n{event_info}\n\nWILL DELETE ALL ASSOCIATED PerformanceList AND Tickets ENTRIES")

                    if confirmation:
                        # Execute the delete query
                        # Before deleting, also delete related entries in PerformanceList and Tickets
                        delete_performance_query = "DELETE FROM PerformanceList WHERE event_name = %s"
                        cursor.execute(delete_performance_query, (event_name,))
                        
                        delete_tickets_query = "DELETE FROM Tickets WHERE event_name = %s"
                        cursor.execute(delete_tickets_query, (event_name,))
                        
                        delete_query = "DELETE FROM Events WHERE event_name = %s"
                        cursor.execute(delete_query, (event_name,))
                        conn.commit()

                        MessageBox.showinfo("Delete Status", "Event deleted successfully.")

                        # Destroy old widgets
                        for label in labels:
                            label.destroy()
                        delete_button.destroy()
                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Delete Status", f"Event with name {event_name} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False
        
        success = delete_event(event_name, labels, delete_button)
        if success:
            delete_button.destroy()
            return
        else:
            return

    def delete_group_and_destroy(group_name, labels, delete_button):
        """
        Wrapper function for delete_group, destroying the delete button afterward.

        Args:
            group_name (str): The group name for the group to be deleted.
            labels (list): List of labels to be destroyed at the end of the function.
            delete_button (Button): The delete button widget to be destroyed.

        Returns:
            None
        """
        
        def delete_group(group_name, labels, delete_button):
            """
            Delete a group from the 'Groups' table based on the group name.

            Args:
                group_name (str): The group name for the group to be deleted.
                labels (list): List of labels to be destroyed at the end of the function.
                delete_button (Button): The delete button widget to be destroyed.

            Returns:
                True or False (depending on whether deletion was successful)
            """
            
            try:
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                check_group_query = "SELECT * FROM Groups WHERE group_name = %s"
                cursor.execute(check_group_query, (group_name,))
                group_info = cursor.fetchone()

                if group_info:
                    # Check if there are any events that the group is/has performed at and if so, cannot delete 
                    check_performance_query = "SELECT * FROM PerformanceList WHERE group_name = %s"
                    cursor.execute(check_performance_query, (group_name,))
                    performance_info = cursor.fetchone()

                    if performance_info:
                        # Retrieve events associated with the group_name in PerformanceList
                        events_query = "SELECT DISTINCT event_name FROM PerformanceList WHERE group_name = %s"
                        cursor.execute(events_query, (group_name,))
                        events_info = cursor.fetchall()

                        event_names = ', '.join(event[0] for event in events_info)

                        MessageBox.showinfo("Delete Status", f"Cannot delete group with name {group_name} because it has entries in the 'PerformanceList' table.\nYou must delete the following associated events first: {event_names}")
                        cursor.close()
                        conn.close()
                        return False            
                    
                    # Display group information for confirmation
                    confirmation = MessageBox.askyesno("Delete Confirmation",
                                                    f"Do you want to delete the following group?\n\n{group_info}\n\nWILL DELETE ALL ASSOCIATED Memberships ENTRIES")

                    if confirmation:
                        # Execute the delete query
                        delete_memberships_query = "DELETE FROM Memberships WHERE group_name = %s"
                        cursor.execute(delete_memberships_query, (group_name,))
                        
                        delete_query = "DELETE FROM Groups WHERE group_name = %s"
                        cursor.execute(delete_query, (group_name,))
                        conn.commit()

                        MessageBox.showinfo("Delete Status", "Group deleted successfully.")

                        # Destroy old widgets
                        for label in labels:
                            label.destroy()
                        delete_button.destroy()
                        print('post destroy')
                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Delete Status", f"Group with name {group_name} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False
        
        
        success = delete_group(group_name, labels, delete_button)

        if success:
            delete_button.destroy()
            return
        else:
            return

    def delete_individual_performer_and_destroy(stage_name, labels, delete_button):
        """
        Wrapper function for delete_individual_performer, destroying the delete button afterward.

        Args:
            stage_name (str): The stage name for the individual performer to be deleted.
            labels (list): List of labels to be destroyed at the end of the function.
            delete_button (Button): The delete button widget to be destroyed.

        Returns:
            None
        """
        
        def delete_individual_performer(stage_name, labels, delete_button):
            """
            Delete an individual performer from the 'IndividualPerformers' table based on the stage name.

            Args:
                stage_name (str): The stage name for the individual performer to be deleted.
                labels (list): List of labels to be destroyed at the end of the function.
                delete_button (Button): The delete button widget to be destroyed.

            Returns:
                True or False (depending on whether deletion was successful)
            """
            try:
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                check_individual_performer_query = "SELECT * FROM IndividualPerformers WHERE stage_name = %s"
                cursor.execute(check_individual_performer_query, (stage_name,))
                individual_performer_info = cursor.fetchone()

                if individual_performer_info:
                    # Display individual performer information for confirmation
                    confirmation = MessageBox.askyesno("Delete Confirmation",
                                                        f"Do you want to delete the following individual performer?\n\n{individual_performer_info}\n\nWILL DELETE ALL ASSOCIATED Memberships ENTRIES")

                    if confirmation:
                        # Execute the delete query
                        # Before deleting, also delete related entries in Memberships
                        delete_memberships_query = "DELETE FROM Memberships WHERE stage_name = %s"
                        cursor.execute(delete_memberships_query, (stage_name,))

                        delete_query = "DELETE FROM IndividualPerformers WHERE stage_name = %s"
                        cursor.execute(delete_query, (stage_name,))
                        conn.commit()

                        MessageBox.showinfo("Delete Status", "Individual performer deleted successfully.")

                        # Destroy old widgets
                        for label in labels:
                            label.destroy()
                        delete_button.destroy()
                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Delete Status", f"Individual performer with stage name {stage_name} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False
        
        success = delete_individual_performer(stage_name, labels, delete_button)
        if success:
            delete_button.destroy()
            return
        else:
            return

    def delete_membership_and_destroy(stage_name, group_name, labels, delete_button):
        """
        Wrapper function for delete_membership, destroying the delete button afterward.

        Args:
            stage_name (str): The stage name for the membership to be deleted.
            group_name (str): The group name for the membership to be deleted.
            labels (list): List of labels to be destroyed at the end of the function.
            delete_button (Button): The delete button widget to be destroyed.

        Returns:
            None
        """
        
        def delete_membership(stage_name, group_name, labels, delete_button):
            """
            Delete a membership from the 'Memberships' table based on the stage name and group name.

            Args:
                stage_name (str): The stage name for the membership to be deleted.
                group_name (str): The group name for the membership to be deleted.
                labels (list): List of labels to be destroyed at the end of the function.
                delete_button (Button): The delete button widget to be destroyed.

            Returns:
                True or False (depending on whether deletion was successful)
            """
            try:
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                check_membership_query = "SELECT * FROM Memberships WHERE stage_name = %s AND group_name = %s"
                cursor.execute(check_membership_query, (stage_name, group_name))
                membership_info = cursor.fetchone()

                if membership_info:
                    # Display membership information for confirmation
                    confirmation = MessageBox.askyesno("Delete Confirmation",
                                                        f"Do you want to delete the following membership?\n\n{membership_info}")

                    if confirmation:
                        # Execute the delete query
                        delete_query = "DELETE FROM Memberships WHERE stage_name = %s AND group_name = %s"
                        cursor.execute(delete_query, (stage_name, group_name))
                        conn.commit()

                        MessageBox.showinfo("Delete Status", "Membership deleted successfully.")

                        # Destroy old widgets
                        for label in labels:
                            label.destroy()
                        delete_button.destroy()
                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Delete Status", f"Membership with stage name {stage_name} and group name {group_name} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False
        
        success = delete_membership(stage_name, group_name, labels, delete_button)
        if success:
            delete_button.destroy()
            return
        else:
            return

    def delete_performance_and_destroy(event_name, group_name, labels, delete_button):
        """
        Wrapper function for delete_performance, destroying the delete button afterward.

        Args:
            event_name (str): The event name for the performance to be deleted.
            group_name (str): The group name for the performance to be deleted.
            labels (list): List of labels to be destroyed at the end of the function.
            delete_button (Button): The delete button widget to be destroyed.

        Returns:
            None
        """
        
        def delete_performance(event_name, group_name, labels, delete_button):
            """
            Delete a performance from the 'PerformanceList' table based on event name and group name.

            Args:
                event_name (str): The event name for the performance to be deleted.
                group_name (str): The group name for the performance to be deleted.
                labels (list): List of labels to be destroyed at the end of the function.
                delete_button (Button): The delete button widget to be destroyed.

            Returns:
                True or False (depending on whether deletion was successful)
            """
            try:
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                check_performance_query = "SELECT * FROM PerformanceList WHERE event_name = %s AND group_name = %s"
                cursor.execute(check_performance_query, (event_name, group_name))
                performance_info = cursor.fetchone()

                if performance_info:
                    # Display performance information for confirmation
                    confirmation = MessageBox.askyesno("Delete Confirmation",
                                                    f"Do you want to delete the following performance?\n\n{performance_info}")

                    if confirmation:
                        # Execute the delete query
                        delete_query = "DELETE FROM PerformanceList WHERE event_name = %s AND group_name = %s"
                        cursor.execute(delete_query, (event_name, group_name))
                        conn.commit()

                        MessageBox.showinfo("Delete Status", "Performance deleted successfully.")

                        # Destroy old widgets
                        for label in labels:
                            label.destroy()
                        delete_button.destroy()
                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Delete Status", f"Performance with event name '{event_name}' and group name '{group_name}' not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False
        
        success = delete_performance(event_name, group_name, labels, delete_button)
        if success:
            delete_button.destroy()
            return
        else:
            return

    def delete_ticket_and_destroy(ticket_id, event_name, labels, delete_button):
        """
        Wrapper function for delete_ticket, destroying the delete button afterward.

        Args:
            ticket_id (int): The ticket ID for the ticket to be deleted.
            event_name (str): The event name for the ticket to be deleted.
            labels (list): List of labels to be destroyed at the end of the function.
            delete_button (Button): The delete button widget to be destroyed.

        Returns:
            None
        """
        
        def delete_ticket(ticket_id, event_name, labels, delete_button):
            """
            Delete a ticket from the 'Tickets' table based on the ticket ID and event name.

            Args:
                ticket_id (int): The ticket ID for the ticket to be deleted.
                event_name (str): The event name for the ticket to be deleted.
                labels (list): List of labels to be destroyed at the end of the function.
                delete_button (Button): The delete button widget to be destroyed.

            Returns:
                None
            """
            try:
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                check_ticket_query = "SELECT * FROM Tickets WHERE id = %s AND event_name = %s"
                cursor.execute(check_ticket_query, (ticket_id, event_name))
                ticket_info = cursor.fetchone()

                if ticket_info:
                    # Display ticket information for confirmation
                    confirmation = MessageBox.askyesno("Delete Confirmation",
                                                    f"Do you want to delete the following ticket?\n\n{ticket_info}")

                    if confirmation:
                        # Execute the delete query
                        delete_query = "DELETE FROM Tickets WHERE id = %s AND event_name = %s"
                        cursor.execute(delete_query, (ticket_id, event_name))
                        conn.commit()

                        MessageBox.showinfo("Delete Status", "Ticket deleted successfully.")

                        # Destroy old widgets
                        for label in labels:
                            label.destroy()
                        delete_button.destroy()
                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Delete Status", f"Ticket with ID {ticket_id} and event name {event_name} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False
        
        
        success = delete_ticket(ticket_id, event_name, labels, delete_button)
        if success:
            delete_button.destroy()
            return
        else:
            return

    def delete_venue_and_destroy(venue_name, labels, delete_button):
        """
        Wrapper function for delete_venue, destroying the delete button afterward.

        Args:
            venue_name (str): The venue name for the venue to be deleted.
            labels (list): List of labels to be destroyed at the end of the function.
            delete_button (Button): The delete button widget to be destroyed.

        Returns:
            None
        """
        
        def delete_venue(venue_name, labels, delete_button):
            """
            Delete a venue from the 'Venue' table based on the venue name.

            Args:
                venue_name (str): The venue name for the venue to be deleted.
                labels (list): List of labels to be destroyed at the end of the function.
                delete_button (Button): The delete button widget to be destroyed.

            Returns:
                True or False (depending on whether deletion was successful)
            """
            try:
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                check_venue_query = "SELECT * FROM Venue WHERE venue_name = %s"
                cursor.execute(check_venue_query, (venue_name,))
                venue_info = cursor.fetchone()

                if venue_info:
                    # Check if there are associated events
                    check_events_query = "SELECT * FROM Events WHERE venue_name = %s"
                    cursor.execute(check_events_query, (venue_name,))
                    events_info = cursor.fetchone()

                    if events_info:
                        # Display associated events information
                        events_str = "\n".join([f"{event}" for event in events_info])
                        MessageBox.showinfo("Associated Events",
                                            f"The venue {venue_name} is associated with the following events:\n\n{events_str}\n\nYou must delete these events prior to venue deletion.")
                        cursor.close()
                        conn.close()
                        return False
                    
                    # Display venue information for confirmation
                    confirmation = MessageBox.askyesno("Delete Confirmation",
                                                        f"Do you want to delete the following venue?\n\n{venue_info}")

                    if confirmation:
                        # Execute the delete query
                        delete_query = "DELETE FROM Venue WHERE venue_name = %s"
                        cursor.execute(delete_query, (venue_name,))
                        conn.commit()

                        MessageBox.showinfo("Delete Status", "Venue deleted successfully.")

                        # Destroy old widgets
                        for label in labels:
                            label.destroy()
                        delete_button.destroy()
                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Delete Status", f"Venue with name {venue_name} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False
        
        success = delete_venue(venue_name, labels, delete_button)
        if success:
            delete_button.destroy()
            return
        else:
            return
    
    
    
    selected_table = delete_drop_down.get()
    
    combobox_index = tab3.winfo_children().index(delete_drop_down)

    # Destroy only the widgets below the combobox
    for widget in tab3.winfo_children()[combobox_index + 1:]:
        widget.destroy()


    if selected_table == 'Users':
        primary_key_label = Label(tab3, text=f'Enter User ID for deletion:', font=('bold', 10))
        primary_key_label.place(x=20, y=90)

        primary_key_entry = Entry(tab3)
        primary_key_entry.place(x=250, y=90)
        
        destroy_labels = [primary_key_entry, primary_key_label]
        
        delete_button = Button(tab3, text="Delete", font=("italic", 10), bg="white",
                               command=lambda: delete_user_and_destroy(primary_key_entry.get(), destroy_labels, delete_button))
        delete_button.place(x=20, y=150)
    
    elif selected_table == 'Events':
        event_name_label = Label(tab3, text=f'Enter Event Name for deletion:', font=('bold', 10))
        event_name_label.place(x=20, y=90)

        event_name_entry = Entry(tab3)
        event_name_entry.place(x=250, y=90)

        destroy_labels = [event_name_entry, event_name_label]

        delete_button = Button(tab3, text="Delete", font=("italic", 10), bg="white",
                               command=lambda: delete_event_and_destroy(event_name_entry.get(), destroy_labels, delete_button))
        delete_button.place(x=20, y=150)

    elif selected_table == 'Groups':
        group_name_label = Label(tab3, text=f'Enter Group Name for deletion:', font=('bold', 10))
        group_name_label.place(x=20, y=90)

        group_name_entry = Entry(tab3)
        group_name_entry.place(x=250, y=90)

        destroy_labels = [group_name_entry, group_name_label]

        delete_button = Button(tab3, text="Delete", font=("italic", 10), bg="white",
                               command=lambda: delete_group_and_destroy(group_name_entry.get(), destroy_labels, delete_button))
        delete_button.place(x=20, y=150)

    elif selected_table == 'IndividualPerformers':
        stage_name_label = Label(tab3, text=f'Enter Stage Name for deletion:', font=('bold', 10))
        stage_name_label.place(x=20, y=90)

        stage_name_entry = Entry(tab3)
        stage_name_entry.place(x=250, y=90)

        destroy_labels = [stage_name_entry, stage_name_label]

        delete_button = Button(tab3, text="Delete", font=("italic", 10), bg="white",
                               command=lambda: delete_individual_performer_and_destroy(stage_name_entry.get(), destroy_labels, delete_button))
        delete_button.place(x=20, y=150)

    elif selected_table == 'Memberships':
        stage_name_label = Label(tab3, text='Enter Stage Name for deletion:', font=('bold', 10))
        stage_name_label.place(x=20, y=90)

        stage_name_entry = Entry(tab3)
        stage_name_entry.place(x=250, y=90)

        group_name_label = Label(tab3, text='Enter Group Name for deletion:', font=('bold', 10))
        group_name_label.place(x=20, y=120)

        group_name_entry = Entry(tab3)
        group_name_entry.place(x=250, y=120)

        destroy_labels = [stage_name_entry, stage_name_label, group_name_entry, group_name_label]

        delete_button = Button(tab3, text='Delete', font=('italic', 10), bg='white',
                            command=lambda: delete_membership_and_destroy(stage_name_entry.get(), group_name_entry.get(), destroy_labels, delete_button))
        delete_button.place(x=20, y=180)

    elif selected_table == 'PerformanceList':
        event_name_label = Label(tab3, text=f'Enter Event Name for deletion:', font=('bold', 10))
        event_name_label.place(x=20, y=90)

        group_name_label = Label(tab3, text=f'Enter Group Name for deletion:', font=('bold', 10))
        group_name_label.place(x=20, y=120)

        event_name_entry = Entry(tab3)
        event_name_entry.place(x=250, y=90)

        group_name_entry = Entry(tab3)
        group_name_entry.place(x=250, y=120)

        destroy_labels = [event_name_entry, event_name_label, group_name_entry, group_name_label]

        delete_button = Button(tab3, text="Delete", font=("italic", 10), bg="white",
                               command=lambda: delete_performance_and_destroy(event_name_entry.get(), group_name_entry.get(), destroy_labels, delete_button))
        delete_button.place(x=20, y=180)
    
    elif selected_table == 'Tickets':
        ticket_id_label = Label(tab3, text=f'Enter Ticket ID for deletion:', font=('bold', 10))
        ticket_id_label.place(x=20, y=90)

        ticket_id_entry = Entry(tab3)
        ticket_id_entry.place(x=250, y=90)

        event_name_label = Label(tab3, text=f'Enter Event Name for deletion:', font=('bold', 10))
        event_name_label.place(x=20, y=120)

        event_name_entry = Entry(tab3)
        event_name_entry.place(x=250, y=120)

        destroy_labels = [ticket_id_entry, ticket_id_label, event_name_entry, event_name_label]

        delete_button = Button(tab3, text="Delete", font=("italic", 10), bg="white",
                               command=lambda: delete_ticket_and_destroy(ticket_id_entry.get(), event_name_entry.get(), destroy_labels, delete_button))
        delete_button.place(x=20, y=180)
    
    elif selected_table == 'Venue':
        venue_name_label = Label(tab3, text=f'Enter Venue Name for deletion:', font=('bold', 10))
        venue_name_label.place(x=20, y=90)

        venue_name_entry = Entry(tab3)
        venue_name_entry.place(x=250, y=90)

        destroy_labels = [venue_name_entry, venue_name_label]

        delete_button = Button(tab3, text="Delete", font=("italic", 10), bg="white",
                               command=lambda: delete_venue_and_destroy(venue_name_entry.get(), destroy_labels, delete_button))
        delete_button.place(x=20, y=150)

def update_pick_table(event):
    
    # Helper function for updating individual performer records
    # Provides a wrapper that handles both the database update and UI cleanup
    def update_individual_performer_and_destroy(stage_name, individual_name, age, labels, update_button):
        # Inner function that handles the actual database update operation
        def update_individual_performer(stage_name, individual_name, age):
            try:
                # Establish database connection
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                # Check if the individual performer with the specified stage name exists
                check_individual_query = "SELECT * FROM IndividualPerformers WHERE stage_name = %s"
                cursor.execute(check_individual_query, (stage_name,))
                performer_info = cursor.fetchone()

                if performer_info:
                    # Request confirmation from the user before updating
                    confirmation = MessageBox.askyesno("Update Confirmation",
                                                        f"Do you want to update the following individual performer?\n{performer_info}")

                    if confirmation:
                        # Validate age
                        if not age.isdigit():
                            MessageBox.showerror("Validation Error", "Age must be a numeric value.")
                            cursor.close()
                            conn.close()
                            return False

                        # Check if all fields are not blank strings
                        if not all(field.strip() for field in [individual_name, age]):
                            MessageBox.showerror("Validation Error", "All fields must be filled.")
                            cursor.close()
                            conn.close()
                            return False

                        # Execute the update query
                        update_query = "UPDATE IndividualPerformers SET individual_name = %s, age = %s WHERE stage_name = %s"
                        cursor.execute(update_query, (individual_name, age, stage_name))
                        conn.commit()

                        MessageBox.showinfo("Update Status", "Individual performer updated successfully.")

                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Update Status", f"Individual performer with stage name {stage_name} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False

        # Call the update function and handle widget destruction
        success = update_individual_performer(stage_name, individual_name, age)
        if success:
            # Destroy old widgets
            for label in labels:
                label.destroy()
            update_button.destroy()
        return success

    # Helper function for updating user records
    # Provides a wrapper that handles both the database update and UI cleanup
    def update_user_and_destroy(user_id, user_name, phone_number, date_of_birth, labels, update_button):
        """
        Wrapper function for update_user_info, destroying the update button afterward.

        Args:
            user_id (int): The user ID for the user to be updated.
            user_name (str): The new user name.
            phone_number (str): The new phone number.
            date_of_birth (str): The new date of birth.
            labels (list): List of labels to be destroyed at the end of the function.
            update_button (Button): The update button widget to be destroyed.

        Returns:
            True or False (depending on whether update was successful)
        """
        # Inner function that performs the actual update operation
        def update_user_info(user_id, user_name, phone_number, date_of_birth):
            """
            Update user information in the 'Users' table based on the user ID.

            Args:
                user_id (int): The user ID for the user to be updated.
                user_name (str): The new user name.
                phone_number (str): The new phone number.
                date_of_birth (str): The new date of birth.

            Returns:
                None
            """
            try:
                # Establish database connection
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                # Check if the user with the specified ID exists
                check_user_query = "SELECT * FROM Users WHERE id = %s"
                cursor.execute(check_user_query, (user_id,))
                user_info = cursor.fetchone()

                if user_info:
                    # Get confirmation from user before proceeding with update
                    confirmation = MessageBox.askyesno("Update Confirmation",
                                                        f"Do you want to update the following user?\n{user_info}")

                    if confirmation:
                        # Validate phone number
                        if not phone_number.isdigit():
                            MessageBox.showerror("Validation Error", "Phone number must be a numeric value.")
                            cursor.close()
                            conn.close()
                            return False

                        # Validate date format
                        if not is_valid_date_format(date_of_birth):
                            MessageBox.showerror("Validation Error", "Invalid date format or components.")
                            cursor.close()
                            conn.close()
                            return False

                        # Check if all fields are not blank strings
                        if not all(field.strip() for field in [user_name, phone_number, date_of_birth]):
                            MessageBox.showerror("Validation Error", "All fields must be filled.")
                            cursor.close()
                            conn.close()
                            return False

                        # Execute the update query
                        update_query = "UPDATE Users SET user_name = %s, phone_number = %s, date_of_birth = %s WHERE id = %s"
                        cursor.execute(update_query, (user_name, phone_number, date_of_birth, user_id))
                        conn.commit()

                        # Notify user of success
                        MessageBox.showinfo("Update Status", "User updated successfully.")

                        cursor.close()
                        conn.close()
                        return True
                else:
                    # Notify if user ID doesn't exist
                    MessageBox.showinfo("Update Status", f"User with ID {user_id} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                # Handle errors during update
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False

        # Call update function and clean up UI on success
        success = update_user_info(user_id, user_name, phone_number, date_of_birth)
        if success:
            # Destroy old widgets
            for label in labels:
                label.destroy()
            update_button.destroy()
            return
        else:
            return

    def update_event_and_destroy(event_name, venue_name, event_date, start_time, labels, update_button):
        def update_event(event_name, venue_name, event_date, start_time):
            try:
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                # Check if the event with the specified name exists
                check_event_query = "SELECT * FROM Events WHERE event_name = %s"
                cursor.execute(check_event_query, (event_name,))
                event_info = cursor.fetchone()

                if event_info:
                    confirmation = MessageBox.askyesno("Update Confirmation",
                                                        f"Do you want to update the following event?\n{event_info}")

                    if confirmation:
                        if not is_valid_date_format(event_date):
                            MessageBox.showerror("Validation Error", "Invalid date format or components.")
                            cursor.close()
                            conn.close()
                            return False

                        # Check if all fields are not blank strings
                        if not all(field.strip() for field in [venue_name, event_date, start_time]):
                            MessageBox.showerror("Validation Error", "All fields must be filled.")
                            cursor.close()
                            conn.close()
                            return False

                        # Check if the venue with the specified name exists 
                        check_venue_query = "SELECT * FROM Venue WHERE venue_name = %s"
                        cursor.execute(check_venue_query, (venue_name,))
                        venue_info = cursor.fetchone()

                        if not venue_info:
                            MessageBox.showerror("Foreign Key Error", f"Venue with name {venue_name} not found.")
                            cursor.close()
                            conn.close()
                            return False

                        update_query = "UPDATE Events SET venue_name = %s, event_date = %s, start_time = %s WHERE event_name = %s"
                        cursor.execute(update_query, (venue_name, event_date, start_time, event_name))
                        conn.commit()

                        MessageBox.showinfo("Update Status", "Event updated successfully.")

                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Update Status", f"Event with name {event_name} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False

        # Call the update function and handle widget destruction
        success = update_event(event_name, venue_name, event_date, start_time)
        if success:
            # Destroy old widgets
            for label in labels:
                label.destroy()
            update_button.destroy()
        return success

    def update_group_and_destroy(group_name, founded, labels, update_button):
        def update_group(group_name, founded):
            try:
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                check_group_query = "SELECT * FROM Groups WHERE group_name = %s"
                cursor.execute(check_group_query, (group_name,))
                group_info = cursor.fetchone()

                if group_info:
                    confirmation = MessageBox.askyesno("Update Confirmation",
                                                        f"Do you want to update the following group?\n{group_info}")

                    if confirmation:
                        # Validate date format
                        if not is_valid_date_format(founded):
                            MessageBox.showerror("Validation Error", "Invalid date format or components.")
                            cursor.close()
                            conn.close()
                            return False

                        # Check if all fields are not blank strings
                        if not all(field.strip() for field in [founded]):
                            MessageBox.showerror("Validation Error", "All fields must be filled.")
                            cursor.close()
                            conn.close()
                            return False

                        update_query = "UPDATE Groups SET founded = %s WHERE group_name = %s"
                        cursor.execute(update_query, (founded, group_name))
                        conn.commit()

                        MessageBox.showinfo("Update Status", "Group updated successfully.")

                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Update Status", f"Group with name {group_name} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False

        # Call the update function and handle widget destruction
        success = update_group(group_name, founded)
        if success:
            # Destroy old widgets
            for label in labels:
                label.destroy()
            update_button.destroy()
        return success

    def update_ticket_and_destroy(ticket_id, event_name, purchased_by, price, labels, update_button):
        def update_ticket(ticket_id, event_name, purchased_by, price):
            try:
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                # Check if the ticket with the specified ID and event name exists
                check_ticket_query = "SELECT * FROM Tickets WHERE id = %s AND event_name = %s"
                cursor.execute(check_ticket_query, (ticket_id, event_name))
                ticket_info = cursor.fetchone()

                if ticket_info:
                    # Display ticket information for confirmation
                    confirmation = MessageBox.askyesno("Update Confirmation",
                                                        f"Do you want to update the following ticket?\n{ticket_info}")

                    if confirmation:
                        # Validate purchased_by (check if the user with the specified ID exists)
                        if purchased_by is not None:
                            check_user_query = "SELECT * FROM Users WHERE id = %s"
                            cursor.execute(check_user_query, (purchased_by,))
                            user_info = cursor.fetchone()
                            
                            if not user_info and purchased_by != 'NULL':
                                MessageBox.showerror("Validation Error", f"User with ID {purchased_by} not found.")
                                cursor.close()
                                conn.close()
                                return False
                            
                        # Validate price
                        try:
                            price = float(price)
                            if price <= 0:
                                raise ValueError
                        except ValueError:
                            MessageBox.showerror("Validation Error", "Price must be a positive numeric value.")
                            cursor.close()
                            conn.close()
                            return False

                        update_query = "UPDATE Tickets SET event_name = %s, purchased_by = %s, price = %s WHERE id = %s AND event_name = %s"
                        cursor.execute(update_query, (event_name, purchased_by, price, ticket_id, event_name))
                        conn.commit()

                        MessageBox.showinfo("Update Status", "Ticket updated successfully.")

                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Update Status", f"Ticket with ID {ticket_id} and event name {event_name} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False

        # Call the update function and handle widget destruction
        success = update_ticket(ticket_id, event_name, purchased_by, price)
        if success:
            # Destroy old widgets
            for label in labels:
                label.destroy()
            update_button.destroy()
        return success

    def update_venue_and_destroy(venue_name, city, capacity, labels, update_button):
        def update_venue_info(venue_name, city, capacity):
            try:
                conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
                cursor = conn.cursor()

                check_venue_query = "SELECT * FROM Venue WHERE venue_name = %s"
                cursor.execute(check_venue_query, (venue_name,))
                venue_info = cursor.fetchone()

                if venue_info:
                    confirmation = MessageBox.askyesno("Update Confirmation",
                                                        f"Do you want to update the following venue?\n{venue_info}")

                    if confirmation:
                        # Validate capacity
                        try:
                            capacity = int(capacity)
                        except ValueError:
                            MessageBox.showerror("Validation Error", "Capacity must be an integer.")
                            cursor.close()
                            conn.close()
                            return False

                        # Check if all fields are not blank strings
                        if not all(field.strip() for field in [city]):
                            MessageBox.showerror("Validation Error", "All fields must be filled.")
                            cursor.close()
                            conn.close()
                            return False

                        update_query = "UPDATE Venue SET city = %s, capacity = %s WHERE venue_name = %s"
                        cursor.execute(update_query, (city, capacity, venue_name))
                        conn.commit()

                        MessageBox.showinfo("Update Status", "Venue updated successfully.")

                        cursor.close()
                        conn.close()
                        return True
                else:
                    MessageBox.showinfo("Update Status", f"Venue with name {venue_name} not found.")
                    cursor.close()
                    conn.close()
                    return False
            except Exception as e:
                print(f"Error: {e}")
                MessageBox.showerror("Error", f"Error: {e}")
                cursor.close()
                conn.close()
                return False

        success = update_venue_info(venue_name, city, capacity)
        if success:
            for label in labels:
                label.destroy()
            update_button.destroy()
            return
        else:
            return

    
    selected_table = update_drop_down.get()
    
    combobox_index = tab4.winfo_children().index(update_drop_down)

    # Destroy only the widgets below the combobox
    for widget in tab4.winfo_children()[combobox_index + 1:]:
        widget.destroy()

    # Create appropriate update forms based on the selected table
    # Each section creates input fields, validation, and update functionality for a specific table
    
    # Form for updating IndividualPerformers table records
    if selected_table == 'IndividualPerformers':
        # Create and position labels and entry fields for performer data
        stage_name_label = Label(tab4, text='Enter Stage Name for update:', font=('bold', 10))
        stage_name_label.place(x=20, y=90)

        stage_name_entry = Entry(tab4)
        stage_name_entry.place(x=250, y=90)

        individual_name_label = Label(tab4, text='Enter New Individual Name:', font=('bold', 10))
        individual_name_label.place(x=20, y=120)

        individual_name_entry = Entry(tab4)
        individual_name_entry.place(x=250, y=120)

        age_label = Label(tab4, text='Enter New Age:', font=('bold', 10))
        age_label.place(x=20, y=150)

        age_entry = Entry(tab4)
        age_entry.place(x=250, y=150)

        # Track all widgets for cleanup after update
        update_labels = [stage_name_entry, stage_name_label, individual_name_entry, individual_name_label,
                        age_entry, age_label]

        # Create update button that calls the update function with form values
        update_button = Button(tab4, text="Update", font=("italic", 10), bg="white",
                                command=lambda: update_individual_performer_and_destroy(stage_name_entry.get(),
                                                                                        individual_name_entry.get(),
                                                                                        age_entry.get(),
                                                                                        update_labels,
                                                                                        update_button))
        update_button.place(x=20, y=220)
    
    # Form for updating Users table records
    elif selected_table == 'Users':
        # Create and position labels and entry fields for user data
        venue_name_label = Label(tab4, text='Enter User Id for update:', font=('bold', 10))
        venue_name_label.place(x=20, y=90)

        venue_name_entry = Entry(tab4)
        venue_name_entry.place(x=250, y=90)

        user_name_label = Label(tab4, text='Enter New User Name:', font=('bold', 10))
        user_name_label.place(x=20, y=120)

        user_name_entry = Entry(tab4)
        user_name_entry.place(x=250, y=120)

        phone_number_label = Label(tab4, text='Enter New Phone Number:', font=('bold', 10))
        phone_number_label.place(x=20, y=150)

        phone_number_entry = Entry(tab4)
        phone_number_entry.place(x=250, y=150)

        date_of_birth_label = Label(tab4, text='Enter New Date of Birth:', font=('bold', 10))
        date_of_birth_label.place(x=20, y=180)

        date_of_birth_entry = Entry(tab4)
        date_of_birth_entry.place(x=250, y=180)

        # Track all widgets for cleanup after update
        update_labels = [venue_name_entry, venue_name_label, user_name_entry, user_name_label,
                        phone_number_entry, phone_number_label, date_of_birth_entry, date_of_birth_label]

        # Create update button that calls the update function with form values
        update_button = Button(tab4, text="Update", font=("italic", 10), bg="white",
                            command=lambda: update_user_and_destroy(venue_name_entry.get(),
                                                                    user_name_entry.get(),
                                                                    phone_number_entry.get(),
                                                                    date_of_birth_entry.get(),
                                                                    update_labels,
                                                                    update_button))
        update_button.place(x=20, y=220)
    
    # Form for updating Events table records
    elif selected_table == 'Events':
        event_name_label = Label(tab4, text='Enter Event Name for update:', font=('bold', 10))
        event_name_label.place(x=20, y=90)

        event_name_entry = Entry(tab4)
        event_name_entry.place(x=250, y=90)

        venue_name_label = Label(tab4, text='Enter New Venue Name:', font=('bold', 10))
        venue_name_label.place(x=20, y=120)

        venue_name_entry = Entry(tab4)
        venue_name_entry.place(x=250, y=120)

        event_date_label = Label(tab4, text='Enter New Event Date (YYYY-MM-DD):', font=('bold', 10))
        event_date_label.place(x=20, y=150)

        event_date_entry = Entry(tab4)
        event_date_entry.place(x=250, y=150)

        start_time_label = Label(tab4, text='Enter New Start Time:', font=('bold', 10))
        start_time_label.place(x=20, y=180)

        start_time_entry = Entry(tab4)
        start_time_entry.place(x=250, y=180)

        update_labels = [event_name_entry, event_name_label, venue_name_entry, venue_name_label,
                        event_date_entry, event_date_label,
                        start_time_entry, start_time_label]

        update_button = Button(tab4, text="Update", font=("italic", 10), bg="white",
                            command=lambda: update_event_and_destroy(event_name_entry.get(),
                                                                        venue_name_entry.get(),
                                                                        event_date_entry.get(),
                                                                        start_time_entry.get(),
                                                                        update_labels,
                                                                        update_button))
        update_button.place(x=20, y=250)

    elif selected_table == 'Groups':
        group_name_label = Label(tab4, text='Enter Group Name for update:', font=('bold', 10))
        group_name_label.place(x=20, y=90)

        group_name_entry = Entry(tab4)
        group_name_entry.place(x=300, y=90)

        founded_label = Label(tab4, text='Enter New Founded Date (YYYY-MM-DD):', font=('bold', 10))
        founded_label.place(x=20, y=120)

        founded_entry = Entry(tab4)
        founded_entry.place(x=300, y=120)

        update_labels = [group_name_entry, group_name_label, founded_entry, founded_label]

        update_button = Button(tab4, text="Update", font=("italic", 10), bg="white",
                            command=lambda: update_group_and_destroy(group_name_entry.get(),
                                                                    founded_entry.get(),
                                                                    update_labels,
                                                                    update_button))
        update_button.place(x=20, y=180)

    elif selected_table == 'Tickets':
        ticket_id_label = Label(tab4, text='Enter Ticket ID for update:', font=('bold', 10))
        ticket_id_label.place(x=20, y=90)

        ticket_id_entry = Entry(tab4)
        ticket_id_entry.place(x=300, y=90)

        event_name_label = Label(tab4, text='Enter Event Name for update:', font=('bold', 10))
        event_name_label.place(x=20, y=120)

        event_name_entry = Entry(tab4)
        event_name_entry.place(x=300, y=120)

        purchased_by_label = Label(tab4, text='Enter New Purchased By (User ID):', font=('bold', 10))
        purchased_by_label.place(x=20, y=150)

        purchased_by_entry = Entry(tab4)
        purchased_by_entry.place(x=300, y=150)

        price_label = Label(tab4, text='Enter New Price:', font=('bold', 10))
        price_label.place(x=20, y=180)

        price_entry = Entry(tab4)
        price_entry.place(x=300, y=180)

        update_labels = [ticket_id_entry, ticket_id_label, event_name_entry, event_name_label,
                        purchased_by_entry, purchased_by_label, price_entry, price_label]

        update_button = Button(tab4, text="Update", font=("italic", 10), bg="white",
                            command=lambda: update_ticket_and_destroy(ticket_id_entry.get(),
                                                                        event_name_entry.get(),
                                                                        purchased_by_entry.get(),
                                                                        price_entry.get(),
                                                                        update_labels,
                                                                        update_button))
        update_button.place(x=20, y=240)

    elif selected_table == 'Venue':
        venue_name_label = Label(tab4, text='Enter Venue Name for update:', font=('bold', 10))
        venue_name_label.place(x=20, y=90)

        venue_name_entry = Entry(tab4)
        venue_name_entry.place(x=300, y=90)

        city_label = Label(tab4, text='Enter New City:', font=('bold', 10))
        city_label.place(x=20, y=120)

        city_entry = Entry(tab4)
        city_entry.place(x=300, y=120)

        capacity_label = Label(tab4, text='Enter New Capacity:', font=('bold', 10))
        capacity_label.place(x=20, y=150)

        capacity_entry = Entry(tab4)
        capacity_entry.place(x=300, y=150)

        update_labels = [venue_name_entry, venue_name_label, city_entry, city_label, capacity_entry, capacity_label]

        update_button = Button(tab4, text="Update", font=("italic", 10), bg="white",
                            command=lambda: update_venue_and_destroy(venue_name_entry.get(),
                                                                    city_entry.get(),
                                                                    capacity_entry.get(),
                                                                    update_labels,
                                                                    update_button))
        update_button.place(x=20, y=210)


def search_tickets():

    min_price = min_price_entry.get() or 0  # Auto fill min price when empty on generating entry box
    max_price = max_price_entry.get()
    purchased_by_null = purchased_by_var.get()
    selected_cities = [city_listbox.get(idx) for idx in city_listbox.curselection()]

    try:
        min_price = int(min_price)
    except ValueError:
        MessageBox.showerror("Error", "Min price must be a valid integer.")
        return

    if max_price:
        try:
            max_price = int(max_price)
        except ValueError:
            MessageBox.showerror("Error", "Max price must be a valid integer.")
            return



    # Construct the SQL query based on the selected filters
    search_query = "SELECT id, event_name, purchased_by, price FROM Tickets JOIN Events USING (event_name) JOIN Venue USING (venue_name) WHERE "
    
    # Add conditions based on user input
    conditions = []
    values = []

    if min_price:
        conditions.append("price >= %s")
        values.append(float(min_price))

    if max_price:
        conditions.append("price <= %s")
        values.append(float(max_price))

    if purchased_by_null:
        conditions.append("purchased_by IS NULL")

    if selected_cities:
        if len(selected_cities) == 1:
            input_string = selected_cities[0]
            conditions.append("event_name IN (SELECT event_name FROM Events WHERE city = %s)")
            values.append(input_string)
        else:
            # creates string to append to command
            append_string = ''
            append_string += "event_name IN (SELECT event_name FROM Events WHERE city IN ("
            for i in range(len(selected_cities)):
                append_string += '%s'
                if i < len(selected_cities) - 1:
                    append_string += ', '
            append_string += '))'
            conditions.append(append_string)
            for city in selected_cities:
                values.append(city)

    # Combine conditions into the final query
    if conditions:
        search_query += " AND ".join(conditions)
    else:
        search_query += "1"  # To avoid syntax error if no conditions are specified
    
    try:
        conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
        cursor = conn.cursor()
        
        cursor.execute(search_query, values)
        results = cursor.fetchall()

        # Clear previous results
        for row in result_tree.get_children():
            result_tree.delete(row)

        # Display the search results in a table
        for result in results:
            result_tree.insert("", "end", values=result)

    except Exception as e:
        print(f"Error: {e}")
        MessageBox.showerror("Error", f"Error: {e}")

    finally:
        cursor.close()
        conn.close()

def show_ticket_info(treeview):
    selected_item = treeview.selection()
    if selected_item:
        # Get data from the selected item
        item_data = treeview.item(selected_item)
        values = item_data['values']
        
        # Extract ticket information
        ticket_id, event_name, purchased_by, price = values
        
        # Query the database for additional event information using the associated ticket ID
        try:
            conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
            cursor = conn.cursor()

            # Customize this query based on your database schema
            query = "SELECT e.venue_name, e.event_date, e.start_time FROM Events e JOIN Tickets t USING (event_name) WHERE t.id = %s"
            
            cursor.execute(query, (ticket_id,))
            event_info = cursor.fetchone()
            if event_info:
                # Assuming event_info is a tuple or list containing the event information
                venue_name, event_date, start_time = event_info
                MessageBox.showinfo("Ticket Information", f"ID: {ticket_id}\nEvent Name: {event_name}\nPurchased By: {purchased_by}\nPrice: {price}\n\nAdditional Event Information:\nVenue: {venue_name}\nDate: {event_date}\nStart Time: {start_time}")
            else:
                MessageBox.showinfo("Error", "Event information not found.")

        except Exception as e:
            print(f"Error: {e}")
            MessageBox.showerror("Error", f"Error: {e}")

        finally:
            cursor.close()
            conn.close()


def refresh_tab5(widgets_to_destroy):
        
    # Destroy only the widgets below the combobox
    for widget in widgets_to_destroy:
        widget.destroy()

    # Nested function that performs the actual search operation based on user inputs
    # This function is called when the search button is clicked
    def search_tickets_refresh():

        # Get search parameters from input widgets
        min_price = min_price_entry.get() or 0  # Default to 0 if empty
        max_price = max_price_entry.get()
        purchased_by_null = purchased_by_var.get()
        selected_cities = [city_listbox.get(idx) for idx in city_listbox.curselection()]

        # Construct the SQL query based on the selected filters
        search_query = "SELECT id, event_name, purchased_by, price FROM Tickets JOIN Events USING (event_name) JOIN Venue USING (venue_name) WHERE "
        
        # Add conditions based on user input
        conditions = []
        values = []

        # Add price minimum filter if provided
        if min_price:
            conditions.append("price >= %s")
            values.append(float(min_price))

        # Add price maximum filter if provided
        if max_price:
            conditions.append("price <= %s")
            values.append(float(max_price))

        # Add filter for tickets that haven't been purchased yet
        if purchased_by_null:
            conditions.append("purchased_by IS NULL")

        # Add city filter if cities are selected
        if selected_cities:
            if len(selected_cities) == 1:
                # Simple case - only one city selected
                input_string = selected_cities[0]
                conditions.append("event_name IN (SELECT event_name FROM Events WHERE city = %s)")
                values.append(input_string)
            else:
                # Complex case - multiple cities selected
                # Build a parameterized IN clause for multiple cities
                append_string = ''
                append_string += "event_name IN (SELECT event_name FROM Events WHERE city IN ("
                for i in range(len(selected_cities)):
                    append_string += '%s'
                    if i < len(selected_cities) - 1:
                        append_string += ', '
                append_string += '))'
                conditions.append(append_string)
                # Add each city as a separate parameter value
                for city in selected_cities:
                    values.append(city)

        # Combine conditions into the final query
        if conditions:
            search_query += " AND ".join(conditions)
        else:
            search_query += "1"  # To avoid syntax error if no conditions are specified
        
        try:
            conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
            cursor = conn.cursor()
            
            # Execute the search query with the parameter values
            cursor.execute(search_query, values)
            results = cursor.fetchall()

            # Clear previous results
            for row in result_tree.get_children():
                result_tree.delete(row)

            # Display the search results in a table
            for result in results:
                result_tree.insert("", "end", values=result)

        except Exception as e:
            print(f"Error: {e}")
            MessageBox.showerror("Error", f"Error: {e}")

        finally:
            # Ensure database connections are properly closed
            cursor.close()
            conn.close()


    # widget list for destruction on refresh
    widgets_to_destroy = []

    # Create widgets for search in tab5
    min_price_label = tk.Label(tab5, text='Min Price:')
    min_price_label.pack(pady=10)
    widgets_to_destroy.append(min_price_label)

    min_price_entry = tk.Entry(tab5)
    min_price_entry.insert(0, "0")  # Set default value to zero
    min_price_entry.pack()
    widgets_to_destroy.append(min_price_entry)

    # Create and configure the maximum price input section
    max_price_label = tk.Label(tab5, text='Max Price:')
    max_price_label.pack(pady=10)
    widgets_to_destroy.append(max_price_label)

    max_price_entry = tk.Entry(tab5)
    max_price_entry.pack()
    widgets_to_destroy.append(max_price_entry)

    # Create checkbox for filtering unpurchased tickets
    purchased_by_var = tk.IntVar()
    purchased_by_checkbox = tk.Checkbutton(tab5, text='Not Purchased', variable=purchased_by_var)
    purchased_by_checkbox.pack(pady=10)
    widgets_to_destroy.append(purchased_by_checkbox)

    # Create city selection section
    city_label = tk.Label(tab5, text='Select Cities:')
    city_label.pack(pady=10)
    widgets_to_destroy.append(city_label)

    # Create a listbox for cities based on tickets' event's cities
    try:
        conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
        cursor = conn.cursor()

        # Get unique cities that have events with tickets
        cursor.execute("SELECT DISTINCT city FROM Venue JOIN (Tickets JOIN Events USING (event_name)) USING (venue_name)")
        cities = [row[0] for row in cursor.fetchall()]

    except Exception as e:
        print(f"Error: {e}")
        MessageBox.showerror("Error", f"Error: {e}")

    finally:
        cursor.close()
        conn.close()

    # Generate cities to be selected from 
    city_listbox = tk.Listbox(tab5, selectmode=tk.MULTIPLE, exportselection=0)
    for city in cities:
        city_listbox.insert(tk.END, city)
    city_listbox.pack(pady=10)
    widgets_to_destroy.append(city_listbox)

    # Create the search button
    search_button = tk.Button(tab5, text="Search", command=search_tickets_refresh)
    search_button.pack(pady=10)
    widgets_to_destroy.append(search_button)

    # Create a Treeview for displaying results in tabular format
    result_tree = ttk.Treeview(tab5, columns=("ID", "Event Name", "Purchased By", "Price"), show="headings", selectmode='browse')
    result_tree.heading("ID", text="ID")
    result_tree.heading("Event Name", text="Event Name")
    result_tree.heading("Purchased By", text="Purchased By")
    result_tree.heading("Price", text="Price")
    result_tree.pack(pady=10)
    # Enable double-click on a result to show detailed ticket information
    result_tree.bind("<Double-1>", lambda event: show_ticket_info(result_tree))

    widgets_to_destroy.append(result_tree)

    # Add a refresh button that will rebuild the entire search interface
    # This allows users to reset their search or update after database changes
    refresh_button = tk.Button(tab5, text="Refresh", command=lambda: refresh_tab5(widgets_to_destroy))
    refresh_button.pack(pady=10)
    widgets_to_destroy.append(refresh_button)


def search_all_entries(table_name, result_tree):
    """
    Search and display all entries from the specified table.

    Args:
        table_name (str): The name of the table to search for all entries.
        result_tree (ttk.Treeview): The Treeview widget to display the results.

    Returns:
        None
    """
    try:
        conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
        cursor = conn.cursor()

        # Fetch the column names for the selected table
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column[0] for column in cursor.fetchall()]

        search_all_query = f"SELECT * FROM {table_name}"
        cursor.execute(search_all_query)
        results = cursor.fetchall()

        # Clear existing data in the result tree and dynamically create columns
        result_tree["columns"] = columns
        for col in columns:
            result_tree.heading(col, text=col)
            result_tree.column(col, anchor="center", width=100)

        for item in result_tree.get_children():
            result_tree.delete(item)

        # Populate the result tree with the query results
        for result in results:
            result_tree.insert("", "end", values=result)

    except Exception as e:
        print(f"Error: {e}")
        MessageBox.showerror("Error", f"Error: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
