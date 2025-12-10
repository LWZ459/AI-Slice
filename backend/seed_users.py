"""
Seed script to create mock users for testing.
Run this script to populate the database with test users for each role.
"""
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User, UserType, UserStatus, Customer, Chef, DeliveryPerson, Manager, VIPCustomer
from app.models.wallet import Wallet
from app.models.reputation import Reputation


def seed_users():
    """Create mock users for each role."""
    db = SessionLocal()
    
    try:
        # Initialize database tables if they don't exist
        init_db()
        
        # Mock users data
        mock_users = [
            {
                "email": "customer@test.com",
                "username": "customer",
                "password": "password123",
                "full_name": "Test Customer",
                "phone": "1234567890",
                "user_type": UserType.CUSTOMER,
                "wallet_balance": 100.0  # Give customer some money
            },
            {
                "email": "vip@test.com",
                "username": "vip",
                "password": "password123",
                "full_name": "VIP Customer",
                "phone": "1234567891",
                "user_type": UserType.VIP,
                "wallet_balance": 200.0
            },
            {
                "email": "chef@test.com",
                "username": "chef",
                "password": "password123",
                "full_name": "Test Chef",
                "phone": "1234567892",
                "user_type": UserType.CHEF
            },
            {
                "email": "delivery@test.com",
                "username": "delivery",
                "password": "password123",
                "full_name": "Test Delivery",
                "phone": "1234567893",
                "user_type": UserType.DELIVERY
            },
            {
                "email": "manager@test.com",
                "username": "manager",
                "password": "password123",
                "full_name": "Test Manager",
                "phone": "1234567894",
                "user_type": UserType.MANAGER
            }
        ]
        
        created_users = []
        
        for user_data in mock_users:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == user_data["email"]) | (User.username == user_data["username"])
            ).first()
            
            if existing_user:
                print(f"⚠️  User {user_data['username']} already exists. Skipping...")
                continue
            
            # Create user
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                phone=user_data["phone"],
                user_type=user_data["user_type"],
                status=UserStatus.ACTIVE  # Set to ACTIVE so they can login immediately
            )
            
            db.add(user)
            db.flush()  # Get the user ID
            
            # Create type-specific records
            if user.user_type == UserType.CUSTOMER:
                customer = Customer(user_id=user.id)
                db.add(customer)
                
                # Create wallet
                wallet = Wallet(
                    user_id=user.id,
                    balance=user_data.get("wallet_balance", 0.0)
                )
                db.add(wallet)
            
            elif user.user_type == UserType.VIP:
                # VIP users also need Customer record
                customer = Customer(user_id=user.id, is_vip=True)
                db.add(customer)
                
                # Create wallet
                wallet = Wallet(
                    user_id=user.id,
                    balance=user_data.get("wallet_balance", 0.0)
                )
                db.add(wallet)
            
            elif user.user_type == UserType.CHEF:
                chef = Chef(user_id=user.id)
                db.add(chef)
            
            elif user.user_type == UserType.DELIVERY:
                delivery_person = DeliveryPerson(user_id=user.id)
                db.add(delivery_person)
            
            elif user.user_type == UserType.MANAGER:
                manager = Manager(user_id=user.id)
                db.add(manager)
            
            # Create reputation record for all users
            reputation = Reputation(user_id=user.id, score=0)
            db.add(reputation)
            
            created_users.append(user_data["username"])
        
        db.commit()
        
        print("\n✅ Successfully created mock users!\n")
        print("=" * 60)
        print("MOCK USER CREDENTIALS")
        print("=" * 60)
        print("\nAll users have password: password123\n")
        print("1. Customer:")
        print("   Email: customer@test.com")
        print("   Username: customer")
        print("   Wallet Balance: $100.00")
        print("\n2. VIP Customer:")
        print("   Email: vip@test.com")
        print("   Username: vip")
        print("   Wallet Balance: $200.00")
        print("   Status: VIP (5% discount)")
        print("\n3. Chef:")
        print("   Email: chef@test.com")
        print("   Username: chef")
        print("\n4. Delivery:")
        print("   Email: delivery@test.com")
        print("   Username: delivery")
        print("\n5. Manager:")
        print("   Email: manager@test.com")
        print("   Username: manager")
        print("\n" + "=" * 60)
        print(f"\n✅ Created {len(created_users)} users: {', '.join(created_users)}")
        print("\nYou can now login with any of these credentials!\n")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating users: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()

