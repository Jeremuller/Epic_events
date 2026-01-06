Student project for OpenClassrooms:

***Develop a Secure Back-End Architecture with Python and SQL***

1. Project Overview

   1.1 Context

After organizing hundreds of events, we have dozens of regular clients. Unfortunately, our teams have always relied on
inadequate tools, and a proper Customer Relationship Management (CRM) solution is sorely missing.

The main goal is to create a database that allows secure storage and manipulation of client information, contracts, and
events. The system is developed in Python, and error tracking and logging is integrated via Sentry to ensure reliability
and traceability.

   1.2 Project Objectives

The main objectives of this project are:

- Design and implement a secure database from scratch using Python and SQL (without frameworks like Django).

- Implement a CRM system to manage clients, contracts, and events.

- Provide secure user authentication and role-based access control.

- Ensure traceability and monitoring via logging (Sentry).

- Deliver a fully functional application that can be initialized and used by other users with minimal setup.

1.3 Scope and Limitations

**Scope**:

  - The project focuses on the back-end architecture of a CRM system.

- Provides a Command-Line Interface (CLI) for user interaction.

- Supports user roles (management, commercial, support) and corresponding access control.

- Includes secure password storage and session management.

- Database initialization and the creation of the first management user are automated via scripts.

**Limitations**:

  - This project does not include a web interface; it is CLI-only.

  - External integrations (payment systems, email notifications, third-party APIs) are out of scope.

  - Reporting and analytics are limited to basic queries through the CLI.

  - Scalability considerations for large datasets are minimal, as this is a proof-of-concept for internal use.

2. Features

   2.1 User Authentication and Session Management:

   The system provides secure authentication for all users. Passwords are hashed and salted using industry-standard techniques. Sessions are managed with timeouts to prevent unauthorized access if a user leaves their session open. Users can log in and log out via the CLI interface, ensuring that all interactions with the system are authenticated and traceable.

   2.2 Role-Based Access Control

   Users are assigned specific roles: management, commercial, or support. Each role has a distinct set of permissions, limiting access to certain actions or data. For example, only management users can create or modify other users, while commercial users can manage clients and contracts. This ensures that sensitive operations are restricted and system integrity is maintained.
   
   2.3 Client Management

   The CRM allows users to add, update, and view client information securely. Each client can be associated with a commercial contact responsible for managing their account. Client data is stored in a structured and secure way, ensuring that all interactions are logged and auditable.
   
   2.4 Contract Management

   Contracts between the company and clients can be created, modified, and tracked within the system. Contracts are linked to both clients and the responsible commercial user. This feature ensures accurate tracking of business agreements and supports reporting and operational workflows.    
   
   2.5 Event Management

   The CRM includes functionality to manage events organized for clients. Events are associated with clients and support contacts, allowing for clear assignment and accountability. Users can add, modify, and view events via the CLI, and all actions are logged to maintain traceability.
   
   2.6 Logging and Error Tracking

   The system integrates logging for critical events and operations. Errors and exceptions are tracked using Sentry, providing detailed information for debugging and monitoring system health. This ensures that the application maintains high reliability and that any issues can be quickly identified and addressed.


3. Technical Stack
   The CRM system is built using the following technologies:

- Programming Language: Python 3.8+

- Database: MySQL

- MySQL Command line Client or MySQL WorkBench, for initialisation purposes.

- ORM: SQLAlchemy for database access and object-relational mapping

- CLI Framework: Click for command-line interaction

- Logging and Monitoring: Sentry for error tracking and logging

- Security Libraries: Bcrypt for secure password hashing and salting, dotenv for environment variable management

This stack was chosen to provide a secure, maintainable, and portable back-end architecture, while keeping the project simple enough for educational purposes.

Testing and Validation

The CRM application has been rigorously tested to ensure reliability and correctness. This includes:

- Unit tests covering individual functions and classes, with and without mocks depending on the case.

- Integration tests to verify interactions between modules (e.g., database operations, CLI workflows).

- Manual testing to validate end-to-end usage scenarios and critical operations.

These measures ensure that the application is stable, secure, and behaves as expected under real usage conditions.

4. Project Architecture

The CRM application follows a modular architecture to ensure maintainability, clarity, and security. It uses a Model-View-Controller (MVC) pattern adapted for a CLI application, with a clear separation between data, business logic, and user interaction.

Architecture overview:

- Models: Represent the core entities of the system, including Users, Clients, Contracts, and Events. Each model is mapped to the database using SQLAlchemy.

- Controllers / Services: Contain business logic, enforce role-based access control, and handle operations on models.

- Views (CLI): Provide the command-line interface for users, including menus, prompts, and outputs. All user interactions go through this layer.

- Utilities:

    - utils.py – general helper functions, such as formatting and common utilities.

    - auth.py – handles password hashing, authentication, and session management.

    - permissions.py – manages user roles and access rights.
    - database.py – sets up the SQLAlchemy engine, session factory (SessionLocal), and provides the init_db() function to create all tables.
    - init_db.py – initializes the database and its tables.

    - create_first_manager.py – bootstrap script to create the first management user.

This structure ensures that the application is secure, modular, and maintainable, while keeping the user interface simple and intuitive. Critical operations such as authentication, permissions, and database initialization are clearly separated to minimize risks and improve reliability.

5. Prerequisites
   Before installing and running the CRM application, make sure your system meets the following requirements:

    - Python 3.8+ – The application is built in Python and requires version 3.8 or higher.

    - MySQL Server – Used as the relational database. The user must have privileges to create databases and tables. You'll need to create an account on "https://www.mysql.com/fr/" to get credentials needed for the following part.

    - Virtual Environment (venv) – Recommended to isolate project dependencies from the system Python installation.

    - Git – To clone the repository.

    - Environment Variables – The application uses a .env file to store sensitive information such as database credentials. The following variables must be set:

        - DB_USER – MySQL username

        - DB_PASSWORD – MySQL password

        - DB_HOST – MySQL host (e.g., localhost)

        - DB_PORT – MySQL port (default: 3306)

        - DB_NAME – Name of the database to be used

        - SENTRY_DSN – for error tracking

Ensuring these prerequisites are in place will allow a smooth installation, initialization, and usage of the CRM application.
6. Installation


   6.1 Clone the Repository

    Open a terminal and run:

        git clone https://github.com/Jeremuller/Epic_events
        cd epic_events
   

   6.2 Create and Activate a Virtual Environment


   It is recommended to use a virtual environment to isolate project dependencies, open a terminal and run:



On Windows (cmd or PowerShell):
    
    python -m venv env
    env\Scripts\activate    # cmd
    env\Scripts\Activate.ps1    # PowerShell

On macOS/Linux:

    python3 -m venv env
    source env/bin/activate

Once activated, you should see (env) before the command prompt.


   6.3 Install Python Dependencies

Install all required Python packages from requirements.txt:

        pip install -r requirements.txt


   6.4 Configure Environment Variables (.env)

Create a .env file in the project root and add the following variables:

    DB_USER=your_mysql_user
    DB_PASSWORD=your_mysql_password
    DB_HOST=localhost
    DB_PORT=3306
    DB_NAME=epic_events
    SENTRY_DSN=your_sentry_dsn

Replace the placeholders with your actual credentials. These environment variables are loaded automatically by the application using dotenv.


7. Database Initialization

The CRM application relies on a MySQL database.
For security and clarity reasons, the database initialization process is split between manual SQL steps and automated SQLAlchemy scripts.

The following steps describe the required initialization procedure, in the correct order.

**_Prerequisites:_**

Make sure you have access to one of the following tools:

- MySQL Command Line Client

- MySQL Workbench

Database connection parameters must be defined in the .env file.

Step 1 – Create the database and grant privileges (SQL)

Before running any Python script, the database must be created manually and the application user must be granted the appropriate privileges.

Connect to MySQL as an administrator (for example, root), then execute:

      CREATE DATABASE epic_events
      CHARACTER SET utf8mb4
      COLLATE utf8mb4_unicode_ci;

      CREATE USER 'epic_user'@'localhost' IDENTIFIED BY 'strong_password';

      GRANT ALL PRIVILEGES ON epic_events.* TO 'epic_user'@'localhost';

      FLUSH PRIVILEGES;

All credentials writen above between '' are for demonstration purposes, make sure to replace it with proper ones.

This step ensures that:

- The database exists

- The application user has full access to it

- SQLAlchemy can create tables without permission errors

Step 2 – Initialize tables with SQLAlchemy

The CRM application relies on a MySQL database. To simplify setup, the project provides the init_db.py script, which handles both the creation of the database (if it does not exist) and the creation of all required tables.

How to use in a terminal from epic_events:

    python init_db.py


What this script does:

- Reads database connection parameters from the .env file.

- Connects to the MySQL server and creates the database if it does not exist.

- Initializes all tables (Users, Clients, Contracts, Events) using SQLAlchemy’s metadata.

- Prints status messages to indicate progress and success.

Notes:

- The script can be safely re-run multiple times without overwriting existing tables.

- After running this script, the database is fully set up and ready for the first management user to be created using create_first_manager.py.

Step 3 – Select the database and adjust the schema (SQL)


After the tables are created, a manual schema adjustment is required to ensure consistency with the application’s domain model.

Connect again to MySQL and select the database:

      USE epic_events;

Then modify the users table to replace the legacy password column with password_hash:

      ALTER TABLE users
      DROP COLUMN password,
      ADD COLUMN password_hash VARCHAR(100) NOT NULL;

If you have followed those steps properly, you should run smoothly through the next part.

8. Initial User Bootstrap


   After the database is initialized, the CRM requires a first management user to be created. This user has the privileges necessary to manage other users and perform administrative operations.

Why a bootstrap script is required:

- The system cannot function without at least one management user.

- The script ensures that the first user is created securely, following the same validation and password hashing mechanisms used throughout the application.

- It prevents accidentally creating multiple conflicting administrative accounts.

How to create the first management user, from epic_events in a terminal:

        python create_first_manager.py

The script will prompt for:

- Username

- Email

- Password (hidden input with confirmation)

Once completed, the user is created with the management role and can log in to the CRM.

Security considerations:

- Passwords are hashed and salted using bcrypt before being stored in the database.

- The script refuses to run if at least one user already exists, preventing accidental overrides.

It can only be executed manually and is not accessible from the main application workflow, ensuring that automated attacks cannot create privileged accounts.


9. Application Usage
   9.1 Launching the Application
        To start the CRM application, run the main script from epic_events in a terminal:
            
            python -m controllers

   9.2 Authentication Workflow

After launching controllers.py users are required to log in with their username and password. Passwords are verified against the securely hashed versions stored in the database.

Only authenticated users can access the application features.
   
9.3 Role-Based CLI Navigation

The application uses role-based access control to restrict functionality:

- Management users can create, modify, and delete other users, clients, contracts, and events.

- Commercial users can manage clients and contracts but have no administrative privileges.

- Support users can manage events and access related client information.

The CLI menus automatically adjust according to the logged-in user’s role.
   
9.4 Session Timeout and Logout

- Sessions are time-limited to enhance security.

- Users are automatically logged out after a period of inactivity.

- Manual logout is also available via the CLI menu, ensuring that no session persists beyond the intended usage.

This setup ensures a secure and guided experience, keeping data access strictly aligned with user roles.

10. Logging and Monitoring

The CRM application includes a logging and monitoring system to track important events and detect errors, ensuring security and maintainability.

10.1 Application Logs

The application records key events in log files for auditing and debugging purposes.

Logged events include:

- User creation and modification

- Contract signing

- Unexpected errors

Logs provide a clear record of actions performed in the system and help diagnose issues efficiently.

10.2 Error Tracking with Sentry

The system is integrated with Sentry.io for real-time error tracking.

Critical exceptions are automatically sent to Sentry, providing detailed context (stack trace, user, timestamp).

This allows developers or administrators to quickly identify and fix issues before they impact the application.

10.3 Sentry setup guide:


To enable Sentry monitoring:

1) Go to Sentry.io and create an account (or log in if you already have one).

2) Create a new project and select “Python” as the platform.

3) Copy the DSN (Data Source Name) provided by Sentry.

4) Paste the DSN into your .env file:

       SENTRY_DSN=your_sentry_dsn_here
Once the DSN is configured, the application automatically sends errors and events to Sentry.

Example of a logged event in the code (contract signing):

        # Sentry - log contract signature
    if updated_data.get("signed") is True:
        sentry_sdk.set_tag("event_type", "contract_signed")

    sentry_sdk.set_context(
        "contract_signed",
        {
            "contract_id": contract.contract_id,
            "client_id": contract.client_id,
            "client_name": contract.client.business_name if contract.client else "N/A",
            "total_price": contract.total_price,
        }
    )

    sentry_sdk.set_context(
        "actor",
        {
            "actor_id": session.user_id,
            "actor_role": session.role,
        }
    )

    sentry_sdk.capture_message("Contract signed successfully")

The code automatically tracks all critical events; users only need to configure the DSN.

This logging and monitoring system ensures transparency, security, and accountability, giving administrators full visibility into the application’s activity.

11. Security Design

The CRM application is built with security in mind, following best practices for password storage, authentication, session management, and role-based access control.
    
11.1 Password Hashing Strategy

- User passwords are never stored in plain text.

- The application uses bcrypt to hash and salt all passwords.

- Passwords are verified securely during login, preventing exposure even if the database is compromised.
    
11.2 Authentication and Session Security

- Users must log in with a valid username and password to access the application.

- Sessions are time-limited to prevent long-lived credentials from being reused maliciously.

- Manual logout is supported, and all session data is cleared on logout.

11.3 Access Control Rules

The system uses role-based access control to restrict functionality:

- Management: full access, including user creation and modification.

- Commercial: manage clients and contracts.

- Support: manage events only.

Unauthorized actions are blocked at the controller level, ensuring data integrity and security.

11.4 Bootstrap and Initialization Security

- The first management user is created using a dedicated bootstrap script (create_first_manager.py) to ensure secure account creation.

- The script enforces validation, password hashing, and prevents creating multiple management accounts accidentally.

- Database initialization (init_db.py) and environment variables setup are required before running the bootstrap, ensuring the system cannot be misconfigured or accessed without proper setup.

12. Known Limitations and Future Improvements

12.1 Current Limitations

- The CRM is a CLI-based application, which may limit usability compared to a web interface.

- No email or notification system is implemented.

- Some advanced reporting and analytics features are not available.


12.2 Possible Improvements

- Implement a web interface for easier access and usability.

- Add email notifications for contract updates and event reminders.

- Introduce advanced reporting and analytics to monitor client activity and events.

13. Author and Contact

Author: Jeremy Muller
GitHub Repository: https://github.com/Jeremuller/Epic_events
Contact: jeremymuller92@gmail.com

Feel free to report issues, request features, or reach out for questions regarding the CRM project.