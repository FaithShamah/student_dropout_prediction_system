from dotenv import load_dotenv
load_dotenv()

from database import Database
db = Database()
users = db.get_all_users()
for u in users:
    email = u['email']
    print(f"Username: {u['username']}")
    print(f"  Email: '{email}'")
    print(f"  Length: {len(email)}")
    print(f"  Repr: {repr(email)}")
    print()