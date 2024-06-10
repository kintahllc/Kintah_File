import pandas as pd

# Sample data for employees
data = {
    'name': ['John Doe', 'Jane Smith'],
    'work_email': ['john.doe@example.com', 'jane.smith@example.com'],
    'work_phone': ['1234567890', '2345678901'],
    'mobile_phone': ['0987654321', '8765432109'],
    'work_location': ['Head Office', 'Branch Office'],
    'job_id': [1, 2],
    'department_id': [1, 2],
    'manager_id': [3, 4],
    'address_home_id': [5, 6],
    'country_id': [1, 2],
    'identification_id': ['ID123456', 'ID654321'],
    'passport_id': ['AB1234567', 'CD7654321'],
    'gender': ['male', 'female'],
    'marital': ['single', 'married'],
    'birthday': ['1985-01-01', '1990-02-02'],
    'place_of_birth': ['New York', 'Los Angeles'],
    'children': [2, 1],
    'notes': ['Top performer', 'Promising new hire'],
    'work_address_id': [7, 8],
    'barcode': ['123456', '654321'],
    'pin': ['1234', '5678'],
    'active': [True, True],
    'visa_no': ['12345678', '87654321'],
    'permit_no': ['23456789', '98765432'],
    'visa_expire': ['2025-01-01', '2026-02-02'],
    'certificate': ['Bachelor of Science', 'Master of Arts'],
    'study_field': ['Computer Science', 'Business Administration'],
    'study_school': ['XYZ University', 'ABC College'],
    'emergency_contact': ['Jane Doe', 'John Smith'],
    'emergency_phone': ['9876543210', '0123456789'],
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
file_path = '/home/sohel/Downloads/additional ERP configuration automation to add (1)/employees.csv'
df.to_csv(file_path, index=False)

print(f"CSV file saved to {file_path}")
