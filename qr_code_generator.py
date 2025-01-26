import csv
import qrcode
import os

# Load the CSV file into a dictionary
def load_users(csv_file):
    users = []
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            users.append(row['username'])
    return users

# Generate QR codes for each user
def generate_qr_codes(users, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for username in users:
        qr_data = {'username': username}
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save(os.path.join(output_dir, f'{username}.png'))

# Example usage
users = load_users('users.csv')
generate_qr_codes(users, 'qr_codes')
