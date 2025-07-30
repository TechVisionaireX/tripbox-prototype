import requests
import json

def test_expense_functionality():
    # First, login to get tokens
    login_data = {
        'email': 'test@gmail.com',
        'password': 'password123'
    }
    
    try:
        # Login
        login_response = requests.post('http://localhost:5000/api/login', 
                                     json=login_data,
                                     headers={'Content-Type': 'application/json'})
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return
        
        login_data = login_response.json()
        access_token = login_data['access_token']
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("✅ Login successful")
        
        # Test adding an expense
        expense_data = {
            'amount': 50.00,
            'category': 'Food',
            'description': 'Dinner at Italian restaurant'
        }
        
        # Use group ID 2 (created in setup)
        expense_response = requests.post('http://localhost:5000/api/groups/2/expenses',
                                       json=expense_data,
                                       headers=headers)
        
        print(f"Add expense response: {expense_response.status_code}")
        if expense_response.status_code == 201:
            print("✅ Expense added successfully")
            try:
                expense_info = expense_response.json()
                print(f"   Full response: {expense_info}")
                if 'expense' in expense_info:
                    print(f"   Split amount: ${expense_info['expense']['split_amount']}")
                    print(f"   Member count: {expense_info['expense']['member_count']}")
                else:
                    print(f"   Response: {expense_info}")
            except Exception as e:
                print(f"   Response parsing error: {e}")
        else:
            print(f"❌ Failed to add expense: {expense_response.text}")
        
        # Test getting expenses
        expenses_response = requests.get('http://localhost:5000/api/groups/2/expenses',
                                       headers=headers)
        
        print(f"Get expenses response: {expenses_response.status_code}")
        if expenses_response.status_code == 200:
            try:
                expenses = expenses_response.json()
                print(f"✅ Found {len(expenses)} expenses")
                for expense in expenses:
                    print(f"   - ${expense['amount']} for {expense['category']} by {expense.get('user_name', 'Unknown')}")
            except Exception as e:
                print(f"   Response parsing error: {e}")
        else:
            print(f"❌ Failed to get expenses: {expenses_response.text}")
        
        # Test getting expense split
        split_response = requests.get('http://localhost:5000/api/groups/2/expenses/split',
                                    headers=headers)
        
        print(f"Get split response: {split_response.status_code}")
        if split_response.status_code == 200:
            try:
                split_info = split_response.json()
                print("✅ Expense split calculated")
                print(f"   Total: ${split_info['total_expense']}")
                print(f"   Members: {split_info['member_count']}")
                print(f"   Per person: ${split_info['split_per_member']}")
            except Exception as e:
                print(f"   Response parsing error: {e}")
        else:
            print(f"❌ Failed to get split: {split_response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == '__main__':
    test_expense_functionality() 