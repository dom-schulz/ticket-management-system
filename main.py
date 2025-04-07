############################################################################
 # NAME: Dominick Schulz
 # CLASS: CPSC 321 
 # DATE: 12/3/2023
 # DESCRIPTION: Ticket Master Spin off Using Python Tkinter
############################################################################



import tkinter as tk 
from tkinter import *
import tkinter.messagebox as MessageBox
import tkinter.ttk as ttk
import mariadb 
from configparser import ConfigParser
from ticket_utils import *

# scrapes input from config file for db connection
config = ConfigParser()
config.read("my_config.ini")
serv = config.get('db_info', 'host')
usern = config.get('db_info', 'user')
passw =config.get('db_info', 'password')
db = config.get('db_info', 'database')


# General format for layout of application
root = tk.Tk()
root.title("Final Project")
root.geometry('1000x800')
tabControl = ttk.Notebook(root)
tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)
tab3 = ttk.Frame(tabControl)
tab4 = ttk.Frame(tabControl)
tab5 = ttk.Frame(tabControl)
tab6 = ttk.Frame(tabControl)
tabControl.add(tab1, text='Admin Dashboard')
tabControl.add(tab2, text='Add Entries')
tabControl.add(tab3, text='Delete Entries')
tabControl.add(tab4, text='Update Entries')
tabControl.add(tab5, text='Search Tickets')
tabControl.add(tab6, text='Search All')
tabControl.pack(expand=1, fill="both")

# can dynamically create a list of tables, but update tables cannot be used for certain tables (those that consist solely of primary keys)
# so decided for this application (where we are not creating tables), that explicitly defining them is easier
all_tables = ['Events', 'Groups', 'IndividualPerformers', 'Memberships', 'PerformanceList', 'Tickets', 'Users', 'Venue']
update_tables = ['Events', 'Groups', 'IndividualPerformers', 'Tickets', 'Users', 'Venue']


# Dashboard

# Selectes Top 10 Users that have purchased the most tickets. Keeps ties
label1 = tk.Label(tab1, text="Top 10 Users With Most Tickets")
label1.pack(pady=20)

# Create Top Ticket counts
top_ticket_count = '''
SELECT
    user_id,
    user_name,
    ticket_count
FROM (
    SELECT
        user_id,
        user_name,
        ticket_count,
        RANK() OVER (ORDER BY ticket_count DESC) AS rank
    FROM (
        SELECT
            t.purchased_by AS user_id,
            u.user_name,
            COUNT(t.id) AS ticket_count
        FROM Tickets t JOIN Users u ON u.id = t.purchased_by
        WHERE t.purchased_by IS NOT NULL
        GROUP BY t.purchased_by, u.user_name
    ) AS ranked_users
) AS final_result
WHERE rank <= 10
ORDER BY ticket_count DESC; 
'''

top_ticket_tree = ttk.Treeview(tab1, columns=("ID", "user_name", "ticket_count"), show="headings", height=5)
top_ticket_tree.heading("ID", text="ID")
top_ticket_tree.heading("ticket_count", text="Ticket Count")
top_ticket_tree.heading("user_name", text="User Name")
top_ticket_tree.pack(pady=10)

columns1 = ("ID", "User Name", "Ticket Count")
populate_result_tree(top_ticket_tree, top_ticket_count, columns1)


# Query to Generate the top 5 Revenue Generating Events. Joins with User tickets and uses those prices that are not NULL (must be purchased ticket)
top_revenue_query = '''
WITH RankedEvents AS (
    SELECT
        Events.event_name,
        SUM(price) AS total_revenue,
        RANK() OVER (ORDER BY SUM(price) DESC) AS rank
    FROM Tickets JOIN Events ON Tickets.event_name = Events.event_name
    WHERE Tickets.purchased_by IS NOT NULL
    GROUP BY Events.event_name
)
SELECT
    event_name,
    total_revenue
FROM RankedEvents
WHERE rank <= 5;
'''

label_revenue = tk.Label(tab1, text="Top 5 Events with Highest Revenue")
label_revenue.pack(pady=20)

result_tree_revenue = ttk.Treeview(tab1, columns=("Event Name", "Total Revenue"), show="headings", height=5)
result_tree_revenue.heading("Event Name", text="Event Name")
result_tree_revenue.heading("Total Revenue", text="Total Revenue")
result_tree_revenue.pack(pady=10)

columns_revenue = ("Event Name", "Total Revenue")
populate_result_tree(result_tree_revenue, top_revenue_query, columns_revenue)

top_users_query = '''
WITH RankedUsers AS (
    SELECT
        u.id AS user_id,
        u.user_name,
        COUNT(t.id) AS ticket_count,
        SUM(t.price) AS total_spent,
        RANK() OVER (ORDER BY SUM(t.price) DESC) AS rank
    FROM Tickets t
    JOIN Users u ON t.purchased_by = u.id
    WHERE t.purchased_by IS NOT NULL
    GROUP BY u.id, u.user_name
)
SELECT
    user_id,
    user_name,
    ticket_count,
    total_spent
FROM RankedUsers
WHERE rank <= 10
ORDER BY total_spent DESC;
'''

label_top_users = tk.Label(tab1, text="Top 10 Users with Highest Spending")
label_top_users.pack(pady=20)

result_tree_top_users = ttk.Treeview(tab1, columns=("User ID", "User Name", "Ticket Count", "Total Spent"), show="headings", height=10)
result_tree_top_users.heading("User ID", text="User ID")
result_tree_top_users.heading("User Name", text="User Name")
result_tree_top_users.heading("Ticket Count", text="Ticket Count")
result_tree_top_users.heading("Total Spent", text="Total Spent")
result_tree_top_users.pack(pady=10)

columns_top_users = ("User ID", "User Name", "Ticket Count", "Total Spent")
populate_result_tree(result_tree_top_users, top_users_query, columns_top_users)


# Insertion functionality

text_var = tk.StringVar()
text_var.set('Select Table')
table_drop_down = ttk.Combobox(tab2, textvariable=text_var, values=all_tables)
table_drop_down.pack()
table_drop_down.bind("<<ComboboxSelected>>", insert_pick_table)


# Deletion functionality
    
del_text_var = tk.StringVar()
del_text_var.set('Select Table')
delete_drop_down = ttk.Combobox(tab3, textvariable=del_text_var, values=all_tables)
delete_drop_down.pack()
delete_drop_down.bind("<<ComboboxSelected>>", delete_pick_table)


# Update functionality

update_text_var = tk.StringVar()
update_text_var.set('Select Table')
update_drop_down = ttk.Combobox(tab4, textvariable=update_text_var, values=update_tables)
update_drop_down.pack()
update_drop_down.bind("<<ComboboxSelected>>", update_pick_table)


# Search functionality
# Initially have to genereate the search features, then use refresh button to refresh the page once edits are made
# to the tables. The refresh button then recursively calls itself so multiple searches can happen after refreshing. 

# widget list for destruction on refresh
widgets_to_destroy = []

min_price_label = tk.Label(tab5, text='Min Price:')
min_price_label.pack(pady=10)
widgets_to_destroy.append(min_price_label)

min_price_entry = tk.Entry(tab5)
min_price_entry.insert(0, "0")  # Set default value to zero
min_price_entry.pack()
widgets_to_destroy.append(min_price_entry)

max_price_label = tk.Label(tab5, text='Max Price:')
max_price_label.pack(pady=10)
widgets_to_destroy.append(max_price_label)

max_price_entry = tk.Entry(tab5)
max_price_entry.pack()
widgets_to_destroy.append(max_price_entry)

purchased_by_var = tk.IntVar()
purchased_by_checkbox = tk.Checkbutton(tab5, text='Not Purchased', variable=purchased_by_var)
purchased_by_checkbox.pack(pady=10)
widgets_to_destroy.append(purchased_by_checkbox)

city_label = tk.Label(tab5, text='Select Cities:')
city_label.pack(pady=10)
widgets_to_destroy.append(city_label)

# Create a listbox for cities based on tickets' event's cities
try:
    conn = mariadb.connect(host=serv, user=usern, password=passw, database=db)
    cursor = conn.cursor()

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

search_button = tk.Button(tab5, text="Search", command=search_tickets)
search_button.pack(pady=10)
widgets_to_destroy.append(search_button)

result_tree = ttk.Treeview(tab5, columns=("ID", "Event Name", "Purchased By", "Price"), show="headings", selectmode='browse')
result_tree.heading("ID", text="ID")
result_tree.heading("Event Name", text="Event Name")
result_tree.heading("Purchased By", text="Purchased By")
result_tree.heading("Price", text="Price")
result_tree.pack(pady=10)
result_tree.bind("<Double-1>", lambda event: show_ticket_info(result_tree)) # Bind double click to open new information

widgets_to_destroy.append(result_tree)

refresh_button = tk.Button(tab5, text="Refresh", command=lambda: refresh_tab5(widgets_to_destroy))
refresh_button.pack(pady=10)
widgets_to_destroy.append(refresh_button)



label_search = tk.Label(tab6, text="Search All Entries", font=('bold', 10))
label_search.pack(pady=10)

search_table_var = tk.StringVar()
search_table_var.set('Select Table')
search_table_drop_down = ttk.Combobox(tab6, textvariable=search_table_var, values=all_tables)
search_table_drop_down.pack(pady=10)

result_tree_search = ttk.Treeview(tab6, show="headings", height=10)
result_tree_search.pack(pady=10)

search_all_button = Button(tab6, text="Search All", font=("italic", 10), bg="white",
                           command=lambda: search_all_entries(search_table_var.get(), result_tree_search))
search_all_button.pack(pady=10)

root.mainloop()