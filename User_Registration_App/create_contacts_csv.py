import pandas as pd

# Sample data
data = {
    'name': ['John Doe', 'Jane Smith'],
    'company_name': ['Acme Inc.', ''],
    'parent_id': [1, 2],
    'type': ['contact', 'invoice'],
    'email': ['john.doe@example.com', 'jane.smith@example.com'],
    'phone': ['1234567890', '2345678901'],
    'mobile': ['0987654321', '8765432109'],
    'street': ['123 Main St', '456 Elm St'],
    'street2': ['Suite 100', ''],
    'city': ['Anytown', 'Othertown'],
    'state_id': [1, 2],
    'zip': ['12345', '67890'],
    'country_id': [1, 2],
    'title': [1, 2],
    'function': ['CEO', 'CFO'],
    'website': ['http://example.com', 'http://example.org'],
    'comment': ['Important client', 'New client'],
    'customer_rank': [0, 1],
    'supplier_rank': [0, 1],
    'is_company': [True, False],
    'vat': ['AB1234567890', ''],
    'lang': ['en_US', 'es_ES'],
    'active': [True, True],
    'category_id': ['1', '2'],
    'bank_account': ['123456789', '234567890'],
    'bank_id': [1, 2]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
file_path = '/home/sohel/Downloads/additional ERP configuration automation to add (1)/contacts.csv'
df.to_csv(file_path, index=False)
file_path
