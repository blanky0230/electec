import sqlite3
import random
from faker import Faker

random.seed("DemTomSteigIchAufsDach")
Faker.seed("DemTomSteigIchAufsDach")
fake = Faker()

# Drop all tables if they exist
tables = ['OrderDetails', 'Orders', 'Products', 'Customers', 'OrderStatus', 'SupportTickets', 'SupportTicketStatus']

def clear_db():
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('elec_tec_ecommerce.db')
    cursor = conn.cursor()

    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')

    # Recreate the tables

    # Customers table
    cursor.execute('''
        CREATE TABLE Customers (
        CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
        CompanyName TEXT NOT NULL,
        ContactName TEXT,
        ContactEmail TEXT,
        Phone TEXT,
        Address TEXT,
        City TEXT,
        PostalCode TEXT,
        Country TEXT
    )
    ''')

    # Products table
    cursor.execute('''
    CREATE TABLE Products (
        ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
        ProductName TEXT NOT NULL,
        Category TEXT,
        Price REAL NOT NULL,
        StockQuantity INTEGER NOT NULL
    )
    ''')

    # Orders table
    cursor.execute('''
    CREATE TABLE Orders (
        OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerID INTEGER,
        OrderDate TEXT NOT NULL,
        TotalAmount REAL NOT NULL,
        Status TEXT NOT NULL,
        FOREIGN KEY (CustomerID) REFERENCES Customers (CustomerID)
    )
    ''')

    # OrderDetails table
    cursor.execute('''
    CREATE TABLE OrderDetails (
        OrderDetailID INTEGER PRIMARY KEY AUTOINCREMENT,
        OrderID INTEGER,
        ProductID INTEGER,
        Quantity INTEGER NOT NULL,
        Price REAL NOT NULL,
        FOREIGN KEY (OrderID) REFERENCES Orders (OrderID),
        FOREIGN KEY (ProductID) REFERENCES Products (ProductID)
    )
    ''')

    # OrderStatus table
    cursor.execute('''
    CREATE TABLE OrderStatus (
        StatusID INTEGER PRIMARY KEY AUTOINCREMENT,
        StatusName TEXT NOT NULL
    )
    ''')

    # SupportTickets table
    cursor.execute('''
    CREATE TABLE SupportTickets (
        TicketID INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerID INTEGER,
        IssueDescription TEXT NOT NULL,
        DateCreated TEXT NOT NULL,
        Status TEXT NOT NULL,
        FOREIGN KEY (CustomerID) REFERENCES Customers (CustomerID)
    )
    ''')

    # SupportTicketStatus table
    cursor.execute('''
    CREATE TABLE SupportTicketStatus (
        TicketStatusID INTEGER PRIMARY KEY AUTOINCREMENT,
        StatusName TEXT NOT NULL
    )
    ''')

    # Save (commit) the changes and close the connection
    conn.commit()
    conn.close()
    print("Database cleared and tables recreated.")


def fill_db():
    # Initialize Faker to generate synthetic data

    # Establish a connection to the SQLite database
    conn = sqlite3.connect('elec_tec_ecommerce.db')
    cursor = conn.cursor()

    # Function to generate customers
    def generate_customers(n):
        customers = []
        for _ in range(n):
            customers.append((fake.company(), fake.name(), fake.email(), fake.phone_number(), fake.address(), fake.city(), fake.postcode(), fake.country()))
        return customers

    # Function to generate products
    def generate_products(n):
        categories = ['Electronics', 'Computer', 'Mobile', 'Appliances']
        products = []
        for _ in range(n):
            products.append((fake.word(), random.choice(categories), round(random.uniform(10.0, 30000.0), 2), random.randint(1, 10000)))
        return products

    # Function to generate order statuses
    def generate_order_statuses():
        statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
        return [(status,) for status in statuses]

    # Function to generate orders
    def generate_orders(n, customer_ids):
        orders = []
        for _ in range(n):
            orders.append((random.choice(customer_ids), fake.date_this_year(), round(random.uniform(100.0, 5000.0), 2), random.choice(['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'])))
        return orders

    # Function to generate order details
    def generate_order_details(order_ids, product_ids):
        order_details = []
        for order_id in order_ids:
            num_products = random.randint(1, 100)
            selected_products = random.sample(product_ids, num_products)
            for product_id in selected_products:
                quantity = random.randint(1, 1000)
                price = round(random.uniform(10.0, 30000.0), 2)
                order_details.append((order_id, product_id, quantity, price))
        return order_details

    # Function to generate support ticket statuses
    def generate_support_ticket_statuses():
        statuses = ['Open', 'In Progress', 'Closed', 'On Hold', 'Resolved']
        return [(status,) for status in statuses]

    # Generate support tickets with meaningful issue descriptions
    def generate_support_tickets(n, customer_ids, issue_descriptions):
        tickets = []
        for _ in range(n):
            tickets.append((random.choice(customer_ids), random.choice(issue_descriptions), fake.date_this_year(), random.choice(['Open', 'In Progress', 'Closed', 'On Hold', 'Resolved'])))
        return tickets

    # Define sample issue descriptions
    issue_descriptions = [
        "The device does not power on after charging overnight.",
        "Intermittent connectivity issues with the wireless network.",
        "Screen flickers and displays artifacts during operation.",
        "Software update failed and the system is now unresponsive.",
        "Unable to log in to the account despite using the correct credentials.",
        "Received an error message when trying to process a payment.",
        "The application crashes when attempting to open certain files.",
        "Received the wrong item in the shipment.",
        "Order status remains 'Processing' for an unusually long time.",
        "Need assistance setting up the new hardware device.",
        "Looking for documentation and user manual for the purchased software.",
        "Requesting help with integrating the product into existing systems.",
        "The user interface is not intuitive and requires improvements.",
        "Product arrived damaged and is not functioning properly.",
        "Feature request: Add support for multi-factor authentication.",
        "Suggestion: Provide more detailed error messages for troubleshooting."
    ]



    # Generate data
    customers = generate_customers(233)
    products = generate_products(3000)
    order_statuses = generate_order_statuses()
    orders = generate_orders(300, list(range(1, 234)))
    order_details = generate_order_details(list(range(1, 234)), list(range(1, 3001)))
    support_ticket_statuses = generate_support_ticket_statuses()

    support_tickets = generate_support_tickets(1000, list(range(1, 234) ), issue_descriptions)

    # Insert data into the database
    cursor.executemany('INSERT INTO Customers (CompanyName, ContactName, ContactEmail, Phone, Address, City, PostalCode, Country) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', customers)
    cursor.executemany('INSERT INTO Products (ProductName, Category, Price, StockQuantity) VALUES (?, ?, ?, ?)', products)
    cursor.executemany('INSERT INTO OrderStatus (StatusName) VALUES (?)', order_statuses)
    cursor.executemany('INSERT INTO Orders (CustomerID, OrderDate, TotalAmount, Status) VALUES (?, ?, ?, ?)', orders)
    cursor.executemany('INSERT INTO OrderDetails (OrderID, ProductID, Quantity, Price) VALUES (?, ?, ?, ?)', order_details)
    cursor.executemany('INSERT INTO SupportTicketStatus (StatusName) VALUES (?)', support_ticket_statuses)
    cursor.executemany('INSERT INTO SupportTickets (CustomerID, IssueDescription, DateCreated, Status) VALUES (?, ?, ?, ?)', support_tickets)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    clear_db()
    fill_db()
    print("Database filled with synthetic data.")
