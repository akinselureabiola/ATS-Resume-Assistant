import bcrypt

users = {
    "admin": "Admin123",
    "bankole": "Test123",
    "ariyo": "Test123",
    "temitayo": "Test123",
    "oluwaseyi": "Test123",
    "ayodeji": "Test123",
    "daizsign": "Test123",
    "ahmed": "Test123"
}

print("\nGenerated Password Hashes:\n")

for username, password in users.items():
    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    print(f"{username}:")
    print(hashed.decode())
    print("-" * 50)