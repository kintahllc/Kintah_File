
import xmlrpc.client
from django.conf import settings
import os

def create_company_and_website(url, db, username, password, company_data, website_data):
    """
    Connects to the Odoo server and creates a new company and a website for that company.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username for authentication.
        password (str): Password for authentication.
        company_data (dict): A dictionary containing the company data.
        website_data (dict): A dictionary containing the website data linked to the new company.

    Returns:
        dict: IDs of the created company and website.
    """
    # Authenticate
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})

    # Object proxy
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Create a new company
    try:
        company_id = models.execute_kw(db, uid, password, 'res.company', 'create', [company_data])
        print("New company created with ID:", company_id)
    except Exception as e:
        ee = str(e)
        return None

    # Create a website for the new company
    website_data['company_id'] = company_id

    try:
        website_id = models.execute_kw(db, uid, password, 'website', 'create', [website_data])
        print("New website created for the company with ID:", website_id)
    except Exception as e:
        ee = str(e)
        return None

    return (company_id,  website_id)


def odooo_company_and_website_create(c_name, w_name, domain):
    # Odoo server information for local use


    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD


    # Data for the new company
    company_data = {
        'name': c_name,
        'street': '123 Local Street',
        'city': 'Local City',
        'zip': '12345',
        'country_id': 110,  # Assuming the country ID is known and correct
        'phone': '+1234567890',
        'email': 'info@newlocalcompany.com',
        'website': domain
    }

    # Data for the new website
    website_data = {
        'name': w_name,
        'domain':w_name,
    }

    # Create the company and the website
    result = create_company_and_website(url, db, username, password, company_data, website_data)
    # print("Created entries:", result)
    return result



def create_user_group_new(url, db, username, password, group_name):
    """
    Create a new user group in Odoo via XML-RPC or return the existing group ID if already created.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username of the admin user.
        password (str): Password of the admin user.
        group_name (str): Name of the user group to be created.

    Returns:
        int: ID of the user group (whether newly created or existing).
    """
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Search for the group by name
        group_ids = models.execute_kw(db, uid, password, 'res.groups', 'search', [[['name', '=', group_name]]])

        if group_ids:
            # Group with the same name already exists, return its ID
            group_id = group_ids[0]
            print(f"User group '{group_name}' already exists with ID {group_id}.")
            return group_id
        else:
            # Create the user group
            group_id = models.execute_kw(db, uid, password, 'res.groups', 'create', [{'name': group_name}])
            print(f"User group '{group_name}' created successfully with ID {group_id}.")
            return group_id
    except Exception as e:
        print(f"Failed to create or find user group '{group_name}': {e}")
        return None

def assign_access_rights_to_all(url, db, username, password, group_name):
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service with allow_none enabled
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
        group_exist = models.execute_kw(db, uid, password, 'res.groups', 'search', [[['name', '=', group_name]]])
        if group_exist:
            return group_exist
        # Retrieve all modules using search_read
        all_modules = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read', [[]], {'fields': ['id', 'name']})

        for module in all_modules:
            module_name = module['name']
            module_id = module['id']

            # Retrieve all models in the module
            # model_ids = models.execute_kw(db, uid, password, 'ir.model', 'search', [[('module', '=', module_name)]])
            module_models = models.execute_kw(db, uid, password, 'ir.model', 'read', [module_id])

            for model in module_models:
                model_name = model['model']
                model_id = model['id']

                # Create the user group if it doesn't exist
                group_id = create_user_group_new(url, db, username, password, group_name)

                # Assign access rights to the user group for the model
                access_rights_data = {
                    'name': f"Access rights for {group_name} in model {model_name}",
                    'group_id': group_id,
                    'model_id': model_id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True,
                    # 'implied_ids': [(4, models.execute_kw(db, uid, password, 'res.groups', 'search',
                    #                                       [[('name', '=', 'Base')]])[0])],
                    # 'users': [(4, uid)],
                    # 'users_create': True,
                    # 'users_write': True,
                    # 'users_delete': True,
                }

                models.execute_kw(db, uid, password, 'ir.model.access', 'create', [access_rights_data])
        # k=0
        # k=0
        # k=0
        # print(f"Access rights assigned successfully to user group '{group_name}' for all modules and models.")
        return group_id
    except Exception as e:
        print(f"Failed to assign access rights: {e}")
        return None


def create_odoo_user_with_manager_role(url, db, username, password, user_data, company_id, website_id, manager_group_id):
    """
    Create a new user for a specific company and website with the manager role in Odoo via XML-RPC.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username of the admin user.
        password (str): Password of the admin user.
        user_data (dict): Data for creating the new user.
        company_id (int): ID of the company to assign the user.
        website_id (int): ID of the website to assign the user.
        manager_group_id (int): ID of the "Manager" group.
    """
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Create the new user
        user_id = models.execute_kw(db, uid, password, 'res.users', 'create', [user_data])
        # user_id = 45

        allow_company_res = models.execute_kw(db, uid, password, 'res.users', 'write', [[user_id], {
            'company_ids': [(4, company_id)]
        }])
        try:
            for i in manager_group_id:
                manager_group_id_without_list = i
        except:
            manager_group_id_without_list = manager_group_id

        # Assign the user to the "Manager" group
        m_res = models.execute_kw(db, uid, password, 'res.users', 'write', [[user_id], {
            'groups_id': [(4, manager_group_id_without_list)]
        }])

        # Assign the user to the specified company and website
        s_c_w_res = models.execute_kw(db, uid, password, 'res.users', 'write', [[user_id], {
            'company_id': company_id,
            'website_id': website_id
        }])

        print(f"User '{user_data['login']}' created successfully with manager role for company ID {company_id} and website ID {website_id}.")
        return user_data
    except Exception as e:
        print(f"Failed to create user: {e}")
        return None



def create_user_manager_role(name, login, email, password, company_id, website_id, GROUP_NAME):
    # Configuration
    ODOO_URL = settings.ODOO_URL
    DB_NAME = settings.DB_NAME
    ADMIN_USERNAME = settings.ADMIN_USERNAME
    ADMIN_PASSWORD = settings.ADMIN_PASSWORD

    if GROUP_NAME == 'Manager':
        res = assign_access_rights_to_all(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, GROUP_NAME)

    if GROUP_NAME == 'User':
        res = create_user_group_new(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, GROUP_NAME)


    # Group ID of the "Manager" group
    MANAGER_GROUP_ID = res  # Replace with the actual ID of the "Manager" group
    # MANAGER_GROUP_ID = [45]  # Replace with the actual ID of the "Manager" group

    # New user information
    new_user_data = {
        'name': name,  # Full name of the user
        'login': login,  # Login username
        'email': email,  # Email address
        'password': password,  # Password (consider using a strong password)
    }

    # ID of the company to assign the user
    # COMPANY_ID = 32  # Replace with the actual ID of the company
    COMPANY_ID = int(company_id)  # Replace with the actual ID of the company

    # ID of the website to assign the user
    # WEBSITE_ID = 13  # Replace with the actual ID of the website
    WEBSITE_ID = int(website_id)  # Replace with the actual ID of the website


    cres = create_odoo_user_with_manager_role(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, new_user_data, COMPANY_ID, WEBSITE_ID, MANAGER_GROUP_ID)


    # company_id=32, website_id=13
    return cres


def get_users_by_company(url, db, username, password, company_id, website_id):
    """
    Connects to the Odoo server and retrieves all users for a specific company.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username for authentication.
        password (str): Password for authentication.
        company_id (int): The ID of the company.

    Returns:
        list: List of users belonging to the specified company.
    """
    # Authenticate
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})

    # Object proxy
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Search for users by company_id
    # user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[['company_id', '=', company_id]]])
    user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[
        ['company_id', '=', company_id],
        ['website_id', '=', website_id],  # Ensure this field exists
        ['active', '=', True]  # Only active users
    ]])
    users = models.execute_kw(db, uid, password, 'res.users', 'read', [user_ids], {'fields': ['id', 'name', 'login', 'email']})

    return users
def user_list_of_a_company(company_id, website_id):
    ODOO_URL = settings.ODOO_URL
    DB_NAME = settings.DB_NAME
    ADMIN_USERNAME = settings.ADMIN_USERNAME
    ADMIN_PASSWORD = settings.ADMIN_PASSWORD
    res = get_users_by_company(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, company_id, website_id)
    return res

def disable_user(url, db, username, password, website_id, company_id, user_id):
    """
    Disables a user in Odoo by setting their 'active' field to False.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username for authentication.
        password (str): Password for authentication.
        website_id (int): The ID of the website.
        company_id (int): The ID of the company.
        user_id (int): The ID of the user to be disabled.

    Returns:
        str: Result message indicating success or failure.
    """
    try:
        # Authenticate
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        # Object proxy
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        # Search for the user with the specified criteria
        user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[
            ['id', '=', user_id],
            ['company_id', '=', company_id],
            ['website_id', '=', website_id],
            ['active', '=', True]
        ]])

        if not user_ids:
            return "User not found or already inactive."

        # Disable the user by setting 'active' field to False
        result = models.execute_kw(db, uid, password, 'res.users', 'write', [[user_id], {
            'active': False
        }])

        if result:
            return "DONE"
        else:
            return "Failed"
    except Exception as e:
        return None

def disable_user_with_user_id(user_id, company_id, website_id):
    # Example usage
    ODOO_URL = settings.ODOO_URL
    DB_NAME = settings.DB_NAME
    ADMIN_USERNAME = settings.ADMIN_USERNAME
    ADMIN_PASSWORD = settings.ADMIN_PASSWORD


    result = disable_user(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, website_id, company_id, user_id)
    return result




def get_all_user_roles(url, db, username, password):
    """
    Retrieves all user roles (groups) available in Odoo.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username for authentication.
        password (str): Password for authentication.

    Returns:
        list: A list of dictionaries containing the IDs and names of all user roles.
    """
    try:
        # Authenticate
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        # Object proxy
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        # Retrieve all user roles (groups)
        group_ids = models.execute_kw(db, uid, password, 'res.groups', 'search', [[]])
        all_groups = models.execute_kw(db, uid, password, 'res.groups', 'read', [group_ids], {'fields': ['id', 'name']})

        return all_groups
    except Exception as e:
        return []

def all_user_role_of_odd():
    # Example usage
    ODOO_URL = settings.ODOO_URL
    DB_NAME = settings.DB_NAME
    ADMIN_USERNAME = settings.ADMIN_USERNAME
    ADMIN_PASSWORD = settings.ADMIN_PASSWORD

    all_user_roles = get_all_user_roles(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD)
    return all_user_roles

def get_users_with_specific_roles(url, db, username, password, company_id, website_id):
    """
    Retrieves all users and their specific roles for a specific company and website in Odoo.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username for authentication.
        password (str): Password for authentication.
        company_id (int): The ID of the company.
        website_id (int): The ID of the website.

    Returns:
        list: A list of dictionaries containing user information and their roles.
    """
    try:
        # Authenticate
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        # Object proxy
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        # Search for users associated with the specific company and website
        user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [
            [['company_id', '=', company_id], ['website_id', '=', website_id]]])

        if not user_ids:
            return "No users found for the specified company and website."

        # Read user data, including group (role) IDs
        users_data = models.execute_kw(db, uid, password, 'res.users', 'read', [user_ids], {'fields': ['id', 'name', 'login', 'groups_id']})

        # Retrieve details of each group (role)
        role_ids = set()
        for user in users_data:
            role_ids.update(user['groups_id'])

        roles_data = models.execute_kw(db, uid, password, 'res.groups', 'read', [list(role_ids)], {'fields': ['id', 'name']})
        roles_dict = {role['id']: role['name'] for role in roles_data}

        # Attach role names to each user
        for user in users_data:
            user['roles'] = [roles_dict[role_id] for role_id in user['groups_id']]

        return users_data

    except Exception as e:
        return str(e)

def get_users_with_roles_from_company_id(company_id, website_id):
    # Example usage
    ODOO_URL = settings.ODOO_URL
    DB_NAME = settings.DB_NAME
    ADMIN_USERNAME = settings.ADMIN_USERNAME
    ADMIN_PASSWORD = settings.ADMIN_PASSWORD



    users_with_roles = get_users_with_specific_roles(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, company_id, website_id)

    return users_with_roles


def get_all_user_roles():
    ODOO_URL = settings.ODOO_URL
    DB_NAME = settings.DB_NAME
    ADMIN_USERNAME = settings.ADMIN_USERNAME
    ADMIN_PASSWORD = settings.ADMIN_PASSWORD
    res = get_all_user_roles_info(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD)
    return res

def get_all_user_roles_info(url, db, username, password):

    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        roles = models.execute_kw(db, uid, password, 'res.groups', 'search_read', [[]], {'fields': ['id', 'name']})

        return roles
    except Exception as e:
        print(f"Error fetching user roles: {e}")
        return []


def get_user_roles(user_id):
    ODOO_URL = settings.ODOO_URL
    DB_NAME = settings.DB_NAME
    ADMIN_USERNAME = settings.ADMIN_USERNAME
    ADMIN_PASSWORD = settings.ADMIN_PASSWORD
    res = get_user_roles_info(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, user_id)
    return res
def get_user_roles_info(url, db, username, password, user_id):
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        user = models.execute_kw(db, uid, password, 'res.users', 'read', [[user_id]], {'fields': ['groups_id']})

        if user:
            return user[0]['groups_id']
        return []
    except Exception as e:
        print(f"Error fetching user roles: {e}")
        return []


def update_user_roles(user_id, group_ids):

    ODOO_URL = settings.ODOO_URL
    DB_NAME = settings.DB_NAME
    ADMIN_USERNAME = settings.ADMIN_USERNAME
    ADMIN_PASSWORD = settings.ADMIN_PASSWORD
    res = update_user_roles_info(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, user_id, group_ids)
    return res
def update_user_roles_info(url, db, username, password, user_id, group_ids):
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        result = models.execute_kw(db, uid, password, 'res.users', 'write', [[user_id], {
            'groups_id': [(6, 0, group_ids)]
        }])

        return result
    except Exception as e:
        print(f"Error updating user roles: {e}")
        return False


def get_or_create_category(models, db, uid, password, category_name):
    category_ids = models.execute_kw(db, uid, password, 'product.category', 'search', [[['name', '=', category_name]]])
    if category_ids:
        return category_ids[0]
    else:
        category_id = models.execute_kw(db, uid, password, 'product.category', 'create', [{'name': category_name}])
        return category_id