import pandas as pd

# Sample data for suppliers
data = {
    'name': ['Supplier A', 'Supplier B'],
    'company_name': ['Company A', 'Company B'],
    'parent_id': [None, None],  # Parent company ID
    'type': ['contact', 'contact'],  # Contact type
    'email': ['supplier.a@example.com', 'supplier.b@example.com'],
    'phone': ['1234567890', '2345678901'],
    'mobile': ['0987654321', '8765432109'],
    'street': ['123 Main St', '456 High St'],
    'street2': ['Suite 100', 'Apt 202'],
    'city': ['New York', 'Los Angeles'],
    'state_id': [1, 2],  # State ID
    'zip': ['10001', '90001'],
    'country_id': [1, 2],  # Country ID
    'title': [None, None],  # Title ID
    'function': ['Manager', 'Director'],  # Job position
    'website': ['www.companya.com', 'www.companyb.com'],
    'comment': ['Preferred supplier', 'New supplier'],
    'customer_rank': [0, 0],
    'supplier_rank': [1, 1],  # Ensure supplier_rank is set
    'is_company': [True, True],
    'vat': ['US123456789', 'US987654321'],  # VAT number
    'lang': ['en_US', 'en_US'],  # Language
    'active': [True, True],
    'category_id': ['1,2', '2,3'],  # Tags (comma-separated IDs)
    'bank_account': ['123456789', '987654321'],
    'bank_id': [1, 2],  # Bank ID
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
file_path = '/home/sohel/Downloads/additional ERP configuration automation to add (1)/suppliers.csv'
df.to_csv(file_path, index=False)

print(f"CSV file saved to {file_path}")
