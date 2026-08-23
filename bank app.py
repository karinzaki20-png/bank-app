import streamlit as st
import sqlite3
import hashlib
import joblib
import os
from datetime import datetime


# ==================================================
# CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="MyBank",
    page_icon="🏦",
    layout="wide"
)


# ==================================================
# DATABASE
# ==================================================

conn = sqlite3.connect(
    "bank.db",
    check_same_thread=False
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    account_number TEXT UNIQUE NOT NULL,
    balance REAL DEFAULT 0
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    date TEXT NOT NULL
)
""")


conn.commit()


# ==================================================
# LOAD JOBLIB MODEL
# ==================================================

try:

    fraud_model = joblib.load(
        "bank_model.joblib"
    )

except FileNotFoundError:

    fraud_model = None


# ==================================================
# FUNCTIONS
# ==================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def generate_account_number():

    import random

    while True:

        number = (
            "1000"
            + str(
                random.randint(
                    10000000,
                    99999999
                )
            )
        )

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE account_number = ?
            """,
            (number,)
        )

        if cursor.fetchone() is None:

            return number


def get_user():

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (st.session_state.user_id,)
    )

    return cursor.fetchone()


def add_transaction(
    user_id,
    transaction_type,
    amount,
    description
):

    cursor.execute(
        """
        INSERT INTO transactions
        (
            user_id,
            type,
            amount,
            description,
            date
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            transaction_type,
            amount,
            description,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )

    conn.commit()


# ==================================================
# SESSION
# ==================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


if "user_id" not in st.session_state:

    st.session_state.user_id = None


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("🏦 MyBank")

if st.session_state.logged_in:

    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Deposit",
            "Withdraw",
            "Transfer",
            "Transactions",
            "Fraud Check"
        ]
    )

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.user_id = None

        st.rerun()

else:

    page = st.sidebar.radio(
        "Navigation",
        [
            "Login",
            "Register"
        ]
    )


# ==================================================
# REGISTER
# ==================================================

if page == "Register":

    st.title("🏦 Create Your Bank Account")

    name = st.text_input(
        "Full Name"
    )

    email = st.text_input(
        "Email"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )


    if st.button(
        "Create Account",
        use_container_width=True
    ):

        if not name or not email or not password:

            st.error(
                "Please complete all fields."
            )

        elif password != confirm_password:

            st.error(
                "Passwords do not match."
            )

        elif len(password) < 6:

            st.error(
                "Password must contain at least 6 characters."
            )

        else:

            try:

                account_number = (
                    generate_account_number()
                )

                cursor.execute(
                    """
                    INSERT INTO users
                    (
                        name,
                        email,
                        password,
                        account_number,
                        balance
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        email,
                        hash_password(password),
                        account_number,
                        0
                    )
                )

                conn.commit()

                st.success(
                    "Account created successfully!"
                )

                st.info(
                    f"Your account number is: "
                    f"{account_number}"
                )

            except sqlite3.IntegrityError:

                st.error(
                    "This email is already registered."
                )


# ==================================================
# LOGIN
# ==================================================

elif page == "Login":

    st.title("🔐 Login")

    email = st.text_input(
        "Email"
    )

    password = st.text_input(
        "Password",
        type="password"
    )


    if st.button(
        "Login",
        use_container_width=True
    ):

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            AND password = ?
            """,
            (
                email,
                hash_password(password)
            )
        )

        user = cursor.fetchone()


        if user:

            st.session_state.logged_in = True
            st.session_state.user_id = user[0]

            st.success(
                "Login successful!"
            )

            st.rerun()

        else:

            st.error(
                "Invalid email or password."
            )


# ==================================================
# CHECK LOGIN
# ==================================================

elif not st.session_state.logged_in:

    st.warning(
        "Please login or register."
    )


# ==================================================
# DASHBOARD
# ==================================================

elif page == "Dashboard":

    user = get_user()

    st.title(
        f"Welcome, {user[1]} 👋"
    )

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Available Balance",
            f"{user[5]:,.2f} EGP"
        )


    with col2:

        st.metric(
            "Account Number",
            user[4]
        )


    with col3:

        st.metric(
            "Account Status",
            "Active"
        )


    st.divider()

    st.subheader(
        "Quick Actions"
    )

    col1, col2, col3 = st.columns(3)


    with col1:

        if st.button(
            "💰 Deposit",
            use_container_width=True
        ):

            st.info(
                "Choose Deposit from the sidebar."
            )


    with col2:

        if st.button(
            "💸 Withdraw",
            use_container_width=True
        ):

            st.info(
                "Choose Withdraw from the sidebar."
            )


    with col3:

        if st.button(
            "🔄 Transfer",
            use_container_width=True
        ):

            st.info(
                "Choose Transfer from the sidebar."
            )


# ==================================================
# DEPOSIT
# ==================================================

elif page == "Deposit":

    user = get_user()

    st.title("💰 Deposit")

    st.write(
        f"Current balance: "
        f"*{user[5]:,.2f} EGP*"
    )

    amount = st.number_input(
        "Amount",
        min_value=0.01,
        step=100.0
    )


    if st.button(
        "Deposit Money",
        use_container_width=True
    ):

        new_balance = (
            user[5] + amount
        )

        cursor.execute(
            """
            UPDATE users
            SET balance = ?
            WHERE id = ?
            """,
            (
                new_balance,
                user[0]
            )
        )

        add_transaction(
            user[0],
            "Deposit",
            amount,
            "Money deposited"
        )

        conn.commit()

        st.success(
            f"Deposited {amount:,.2f} EGP"
        )

        st.rerun()


# ==================================================
# WITHDRAW
# ==================================================

elif page == "Withdraw":

    user = get_user()

    st.title("💸 Withdraw")

    st.write(
        f"Available balance: "
        f"*{user[5]:,.2f} EGP*"
    )

    amount = st.number_input(
        "Amount",
        min_value=0.01,
        step=100.0
    )


    if st.button(
        "Withdraw Money",
        use_container_width=True
    ):

        if amount > user[5]:

            st.error(
                "Insufficient balance."
            )

        else:

            new_balance = (
                user[5] - amount
            )

            cursor.execute(
                """
                UPDATE users
                SET balance = ?
                WHERE id = ?
                """,
                (
                    new_balance,
                    user[0]
                )
            )

            add_transaction(
                user[0],
                "Withdrawal",
                amount,
                "Money withdrawn"
            )

            conn.commit()

            st.success(
                f"Withdrawn {amount:,.2f} EGP"
            )

            st.rerun()


# ==================================================
# TRANSFER
# ==================================================

elif page == "Transfer":

    user = get_user()

    st.title("🔄 Transfer Money")

    st.write(
        f"Available balance: "
        f"*{user[5]:,.2f} EGP*"
    )

    receiver_account = st.text_input(
        "Receiver Account Number"
    )

    amount = st.number_input(
        "Amount",
        min_value=0.01,
        step=100.0
    )


    if st.button(
        "Transfer",
        use_container_width=True
    ):

        if amount > user[5]:

            st.error(
                "Insufficient balance."
            )

        else:

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE account_number = ?
                """,
                (receiver_account,)
            )

            receiver = cursor.fetchone()


            if receiver is None:

                st.error(
                    "Account not found."
                )

            elif receiver[0] == user[0]:

                st.error(
                    "You cannot transfer money to yourself."
                )

            else:

                sender_balance = (
                    user[5] - amount
                )

                receiver_balance = (
                    receiver[5] + amount
                )


                cursor.execute(
                    """
                    UPDATE users
                    SET balance = ?
                    WHERE id = ?
                    """,
                    (
                        sender_balance,
                        user[0]
                    )
                )


                cursor.execute(
                    """
                    UPDATE users
                    SET balance = ?
                    WHERE id = ?
                    """,
                    (
                        receiver_balance,
                        receiver[0]
                    )
                )


                add_transaction(
                    user[0],
                    "Transfer",
                    amount,
                    "Transfer to "
                    + receiver_account
                )


                add_transaction(
                    receiver[0],
                    "Received",
                    amount,
                    "Received from "
                    + user[4]
                )


                conn.commit()


                st.success(
                    "Transfer completed successfully!"
                )

                st.rerun()


# ==================================================
# TRANSACTIONS
# ==================================================

elif page == "Transactions":

    user = get_user()

    st.title("📜 Transaction History")

    cursor.execute(
        """
        SELECT
            type,
            amount,
            description,
            date
        FROM transactions
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user[0],)
    )

    transactions = cursor.fetchall()


    if transactions:

        for transaction in transactions:

            transaction_type = transaction[0]
            amount = transaction[1]
            description = transaction[2]
            date = transaction[3]


            if transaction_type in [
                "Deposit",
                "Received"
            ]:

                st.success(
                    f"*+{amount:,.2f} EGP*  \n"
                    f"{transaction_type} — "
                    f"{description}  \n"
                    f"{date}"
                )

            else:

                st.error(
                    f"*-{amount:,.2f} EGP*  \n"
                    f"{transaction_type} — "
                    f"{description}  \n"
                    f"{date}"
                )

    else:

        st.info(
            "No transactions yet."
        )


# ==================================================
# FRAUD CHECK
# ==================================================

elif page == "Fraud Check":

    st.title(
        "🤖 AI Transaction Risk Check"
    )

    st.info(
        "This is an educational ML demonstration, "
        "not a real banking fraud-detection system."
    )

    amount = st.number_input(
        "Transaction Amount",
        min_value=1.0,
        value=500.0
    )

    transaction_count = st.number_input(
        "Transactions Today",
        min_value=0,
        value=3
    )

    account_age = st.number_input(
        "Account Age (days)",
        min_value=1,
        value=500
    )


    if st.button(
        "Analyze Transaction",
        use_container_width=True
    ):

        if fraud_model is None:

            st.error(
                "bank_model.joblib was not found. "
                "Run model.py first."
            )

        else:

            prediction = fraud_model.predict([
                [
                    amount,
                    transaction_count,
                    account_age
                ]
            ])

            probability = fraud_model.predict_proba([
                [
                    amount,
                    transaction_count,
                    account_age
                ]
            ])[0][1]


            if prediction[0] == 1:

                st.error(
                    "⚠️ Transaction classified as suspicious."
                )

                st.write(
                    f"Estimated risk: "
                    f"*{probability * 100:.1f}%*"
                )

            else:

                st.success(
                    "✅ Transaction classified as normal."
                )

                st.write(
                    f"Estimated risk: "
                    f"*{probability * 100:.1f}%*"
                )
