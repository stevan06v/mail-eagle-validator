import random
import string

def generate_email():
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10)))
    domain = random.choice(domains)
    return f"{username}@{domain}"

email_list = [generate_email() for _ in range(200)]

# Print the generated email addresses
for email in email_list:
    print(email)