# Virtual-Wallet

Virtual Wallet is a web application designed to help users manage their budget. It allows users to send and receive money between each other and transfer funds from a bank account to their virtual wallet.

## 1.Project description

- User Management: Enables user registration, login, profile management, and admin functions like user authorization and account blocking.
- Transaction Handling: Supports money transfers between users and from bank accounts, including recurring transactions and category-based tracking.
- Card Management: Allows users to register, update, and delete credit/debit cards, enabling fund transfers to and from their virtual wallets.
- Search and Contact Features: Provides functionality to search users by username, email, or phone number and manage contact lists for easy transactions.
- Admin Capabilities: Admins can approve registrations, block/unblock users, view and manage transactions, and deny pending transactions, ensuring smooth operation and security.

## 2.Database

![database](./database.jpg)

## 3.Architecture Diagram

![architecture](./architecture.jpg)

## 4.Hosting

Required:
pip install uvicorn
pip install fastapi
pip install python jose
pip install supabase
pip install passlib
pip install apscheduler

How to interact with the API:
- To run the FastAPI project locally, use Uvicorn as the server. Navigate to your project directory in the terminal and execute the following command: uvicorn main:app --reload. This command will start the FastAPI server in development mode with automatic reloading enabled. The application will be accessible at the URL:
http://127.0.0.1:8000/docs. By visiting this URL in your web browser, you can interact with your FastAPI application using SWAGGER.

- Once the server is running, you can find the documentation for each endpoint in the ReDoc interface at: http://127.0.0.1:8000/redoc

- To navigate to the Front-end of the application, run the URL http://127.0.0.1:8000 - the Home Page of the application will be visualized and you will be able to either login or register in the app in order to continue to interact with other functionalities.

[DB -> Supabase](https://supabase.com/dashboard/project/lcrwokhdqhyvbcjmuedq/editor/29471?sort=id%3Aasc)

## 5. Technologies implemented:

- Python
- Supabase
- FastAPI
- Jinja2
- HTML
- CSS
