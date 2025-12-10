"""
Seed script to create menu items.
Run this script to populate the database with dishes matching the frontend mock data.
"""
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, init_db
from app.models.menu import Dish, DishCategory
from app.models.user import Chef

def seed_menu():
    """Create mock menu items."""
    db = SessionLocal()
    
    try:
        # Check if we have any chefs
        chef = db.query(Chef).first()
        if not chef:
            print("❌ No chefs found in database. Please run seed_users.py first.")
            return

        print(f"👨‍🍳 Using Chef ID: {chef.id}")

        # Create categories if they don't exist
        categories_data = ["Italian", "American", "Healthy", "Dessert"]
        categories = {}
        
        for cat_name in categories_data:
            category = db.query(DishCategory).filter(DishCategory.name == cat_name).first()
            if not category:
                category = DishCategory(name=cat_name, description=f"{cat_name} cuisine")
                db.add(category)
                db.flush()
            categories[cat_name] = category
            
        # Mock dishes data from frontend/src/searchComps/MenuBrowse.js
        # We try to preserve IDs 1-6 if possible, but auto-increment might make it tricky if data exists.
        # Since table is empty (checked previously), IDs should start at 1 if we insert in order.
        mock_dishes = [
            {
                "name": 'Margherita Pizza', 
                "price": 12.99, 
                "category": "Italian",
                "is_available": True, 
                "description": 'Classic Italian pizza with fresh tomatoes, mozzarella cheese, and basil leaves on a thin crust.',
                "tags": "italian,vegetarian,pizza"
            },
            {
                "name": 'Pepperoni Pizza', 
                "price": 14.99, 
                "category": "Italian",
                "is_available": True, 
                "description": 'Traditional pepperoni pizza with spicy pepperoni slices and melted mozzarella cheese.',
                "tags": "italian,pizza,meat"
            },
            {
                "name": 'Caesar Salad', 
                "price": 8.99, 
                "category": "Healthy",
                "is_available": True, 
                "description": 'Fresh romaine lettuce with Caesar dressing, parmesan cheese, and croutons.',
                "tags": "salad,healthy,vegetarian"
            },
            {
                "name": 'Pasta Carbonara', 
                "price": 13.99, 
                "category": "Italian",
                "is_available": True, 
                "description": 'Creamy pasta dish with bacon, eggs, parmesan cheese, and black pepper.',
                "tags": "italian,pasta,meat"
            },
            {
                "name": 'Chicken Burger', 
                "price": 11.99, 
                "category": "American",
                "is_available": True, 
                "description": 'Juicy grilled chicken patty with lettuce, tomato, and special sauce on a toasted bun.',
                "tags": "american,burger,chicken"
            },
            {
                "name": 'Chocolate Cake', 
                "price": 7.99, 
                "category": "Dessert",
                "is_available": True, 
                "description": 'Rich and moist chocolate cake with chocolate frosting, perfect for dessert lovers.',
                "tags": "dessert,sweet,cake"
            }
        ]
        
        created_count = 0
        
        for dish_data in mock_dishes:
            # Check if dish already exists
            existing_dish = db.query(Dish).filter(Dish.name == dish_data["name"]).first()
            
            if existing_dish:
                print(f"⚠️  Dish '{dish_data['name']}' already exists. Updating availability...")
                existing_dish.is_available = True
                continue
            
            category = categories.get(dish_data["category"])
            
            dish = Dish(
                name=dish_data["name"],
                description=dish_data["description"],
                price=dish_data["price"],
                chef_id=chef.id,
                category_id=category.id if category else None,
                is_available=dish_data["is_available"],
                tags=dish_data["tags"],
                average_rating=4.5, # Default rating
                rating_count=10
            )
            
            db.add(dish)
            created_count += 1
            
        db.commit()
        
        print(f"\n✅ Successfully created {created_count} menu items!")
        
        # Verify IDs
        all_dishes = db.query(Dish).all()
        print("\nCurrent Menu Items:")
        for d in all_dishes:
            print(f"ID: {d.id} | Name: {d.name} | Price: ${d.price} | Available: {d.is_available}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding menu: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_menu()

