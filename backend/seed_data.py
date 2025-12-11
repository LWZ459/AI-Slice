"""
Seed data script for AI-Slice database.
Covers all user flows for demo.

Usage:
    python seed_data.py
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import (
    User, UserType, UserStatus,
    Manager, Chef, DeliveryPerson, Customer
)
from app.models.menu import Dish, DishCategory
from app.models.wallet import Wallet
from app.models.reputation import Reputation, Complaint, Compliment, ComplaintStatus
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.delivery import Delivery, DeliveryStatus, DeliveryBid
from app.core.database import Base


def clear_database():
    """Clear all tables"""
    print("🗑️  Clearing existing data...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Database cleared and tables recreated")


def create_users(db):
    """Create all users for demo"""
    print("\n👥 Creating users...")
    
    users_created = []
    
    # ==================== MANAGER ====================
    manager_user = User(
        username="manager",
        email="manager@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Sarah Manager",
        phone="555-0001",
        user_type=UserType.MANAGER,
        status=UserStatus.ACTIVE,
        created_at=datetime.utcnow()
    )
    db.add(manager_user)
    db.flush()
    
    manager = Manager(user_id=manager_user.id, department="Operations", access_level=1)
    db.add(manager)
    print(f"  ✓ Manager: manager@test.com")
    users_created.append(manager_user)
    
    # ==================== CHEF (1) ====================
    chef_user = User(
        username="chef",
        email="chef@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Mario Chef",
        phone="555-0101",
        user_type=UserType.CHEF,
        status=UserStatus.ACTIVE,
        created_at=datetime.utcnow()
    )
    db.add(chef_user)
    db.flush()
    
    chef = Chef(
        user_id=chef_user.id,
        specialization="Italian & International",
        salary=3500.0,
        average_rating=4.5,
        total_orders_completed=50
    )
    db.add(chef)
    db.add(Reputation(user_id=chef_user.id, score=100))
    print(f"  ✓ Chef: chef@test.com (Mario Chef)")
    users_created.append(chef_user)
    
    # ==================== DELIVERY DRIVERS (2) ====================
    delivery1_user = User(
        username="delivery",
        email="delivery@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Dan Driver",
        phone="555-0201",
        user_type=UserType.DELIVERY,
        status=UserStatus.ACTIVE,
        created_at=datetime.utcnow()
    )
    db.add(delivery1_user)
    db.flush()
    
    delivery1 = DeliveryPerson(
        user_id=delivery1_user.id,
        vehicle_type="Motorcycle",
        salary=2000.0,
        average_rating=4.3,
        total_deliveries=30
    )
    db.add(delivery1)
    db.add(Reputation(user_id=delivery1_user.id, score=100))
    print(f"  ✓ Delivery #1: delivery@test.com (Dan Driver - Motorcycle)")
    users_created.append(delivery1_user)
    
    delivery2_user = User(
        username="delivery2",
        email="delivery2@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Lisa Swift",
        phone="555-0202",
        user_type=UserType.DELIVERY,
        status=UserStatus.ACTIVE,
        created_at=datetime.utcnow()
    )
    db.add(delivery2_user)
    db.flush()
    
    delivery2 = DeliveryPerson(
        user_id=delivery2_user.id,
        vehicle_type="Bicycle",
        salary=1800.0,
        average_rating=4.7,
        total_deliveries=45
    )
    db.add(delivery2)
    db.add(Reputation(user_id=delivery2_user.id, score=100))
    print(f"  ✓ Delivery #2: delivery2@test.com (Lisa Swift - Bicycle)")
    users_created.append(delivery2_user)
    
    # ==================== CUSTOMERS (2 regular) ====================
    customer1_user = User(
        username="customer",
        email="customer@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Alice Customer",
        phone="555-0301",
        user_type=UserType.CUSTOMER,
        status=UserStatus.ACTIVE,
        created_at=datetime.utcnow()
    )
    db.add(customer1_user)
    db.flush()
    
    customer1 = Customer(
        user_id=customer1_user.id,
        address="123 Main St, Apt 4B",
        is_vip=False,
        total_orders=2,
        total_spent=45.0
    )
    db.add(customer1)
    db.add(Wallet(user_id=customer1_user.id, balance=150.0))
    db.add(Reputation(user_id=customer1_user.id, score=100))
    print(f"  ✓ Customer #1: customer@test.com (Alice - $150)")
    users_created.append(customer1_user)
    
    customer2_user = User(
        username="customer2",
        email="customer2@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Bob Smith",
        phone="555-0302",
        user_type=UserType.CUSTOMER,
        status=UserStatus.ACTIVE,
        created_at=datetime.utcnow()
    )
    db.add(customer2_user)
    db.flush()
    
    customer2 = Customer(
        user_id=customer2_user.id,
        address="456 Oak Ave",
        is_vip=False,
        total_orders=0,
        total_spent=0.0
    )
    db.add(customer2)
    db.add(Wallet(user_id=customer2_user.id, balance=75.0))
    db.add(Reputation(user_id=customer2_user.id, score=100))
    print(f"  ✓ Customer #2: customer2@test.com (Bob - $75)")
    users_created.append(customer2_user)
    
    # ==================== VIP CUSTOMER ====================
    vip_user = User(
        username="vip",
        email="vip@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Victoria VIP",
        phone="555-0303",
        user_type=UserType.VIP,
        status=UserStatus.ACTIVE,
        created_at=datetime.utcnow()
    )
    db.add(vip_user)
    db.flush()
    
    vip_customer = Customer(
        user_id=vip_user.id,
        address="500 Luxury Lane, Penthouse",
        is_vip=True,
        vip_since=datetime.utcnow() - timedelta(days=30),
        total_orders=15,
        total_spent=500.0
    )
    db.add(vip_customer)
    db.add(Wallet(user_id=vip_user.id, balance=500.0))
    db.add(Reputation(user_id=vip_user.id, score=100))
    print(f"  ⭐ VIP: vip@test.com (Victoria VIP - $500)")
    users_created.append(vip_user)
    
    # ==================== PENDING USERS (for approval demo) ====================
    # Pending Customer
    pending_cust = User(
        username="john_new",
        email="john@email.com",
        hashed_password=get_password_hash("password123"),
        full_name="John Newuser",
        phone="555-9901",
        user_type=UserType.CUSTOMER,
        status=UserStatus.PENDING,
        created_at=datetime.utcnow() - timedelta(hours=2)
    )
    db.add(pending_cust)
    db.flush()
    db.add(Customer(user_id=pending_cust.id, address="789 New St"))
    print(f"  ⏳ Pending Customer: john@email.com (John Newuser)")
    users_created.append(pending_cust)
    
    # Pending Delivery Driver
    pending_del = User(
        username="mike_driver",
        email="mike.driver@email.com",
        hashed_password=get_password_hash("password123"),
        full_name="Mike Driver",
        phone="555-9902",
        user_type=UserType.DELIVERY,
        status=UserStatus.PENDING,
        created_at=datetime.utcnow() - timedelta(hours=5)
    )
    db.add(pending_del)
    db.flush()
    db.add(DeliveryPerson(user_id=pending_del.id, vehicle_type="Car", salary=0))
    print(f"  ⏳ Pending Delivery: mike.driver@email.com (Mike Driver)")
    users_created.append(pending_del)
    
    # Pending Chef
    pending_chef = User(
        username="anna_chef",
        email="anna.chef@email.com",
        hashed_password=get_password_hash("password123"),
        full_name="Anna Baker",
        phone="555-9903",
        user_type=UserType.CHEF,
        status=UserStatus.PENDING,
        created_at=datetime.utcnow() - timedelta(days=1)
    )
    db.add(pending_chef)
    db.flush()
    db.add(Chef(user_id=pending_chef.id, specialization="French Pastry", salary=0))
    print(f"  ⏳ Pending Chef: anna.chef@email.com (Anna Baker)")
    users_created.append(pending_chef)
    
    db.commit()
    print(f"✅ Created {len(users_created)} users (3 pending for approval)")
    
    return users_created


def create_menu(db):
    """Create menu with VIP items clearly marked"""
    print("\n🍕 Creating menu items...")
    
    chef = db.query(Chef).first()
    
    # Categories
    categories = {}
    for name in ["Pizza", "Pasta", "Salads", "Desserts", "Drinks", "VIP Specials"]:
        cat = DishCategory(name=name, description=f"Our {name}")
        db.add(cat)
        db.flush()
        categories[name] = cat
        print(f"  ✓ Category: {name}")
    
    # Regular dishes
    dishes_data = [
        # Pizza
        {"name": "Margherita Pizza", "price": 12.99, "category": "Pizza", 
         "description": "Classic tomato, mozzarella, fresh basil",
         "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400"},
        {"name": "Pepperoni Pizza", "price": 14.99, "category": "Pizza",
         "description": "Spicy pepperoni, melted mozzarella",
         "image_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400"},
        {"name": "BBQ Chicken Pizza", "price": 15.99, "category": "Pizza",
         "description": "Grilled chicken, BBQ sauce, red onions",
         "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400"},
        # Pasta
        {"name": "Spaghetti Carbonara", "price": 13.99, "category": "Pasta",
         "description": "Creamy egg sauce, crispy bacon, parmesan",
         "image_url": "https://images.unsplash.com/photo-1612874742237-6526221588e3?w=400"},
        {"name": "Penne Arrabbiata", "price": 11.99, "category": "Pasta",
         "description": "Spicy tomato sauce, garlic, chili flakes",
         "image_url": "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?w=400"},
        # Salads
        {"name": "Caesar Salad", "price": 8.99, "category": "Salads",
         "description": "Romaine, croutons, parmesan, caesar dressing",
         "image_url": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400"},
        {"name": "Greek Salad", "price": 9.99, "category": "Salads",
         "description": "Feta, olives, tomatoes, cucumber",
         "image_url": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400"},
        # Desserts
        {"name": "Tiramisu", "price": 7.99, "category": "Desserts",
         "description": "Coffee-soaked ladyfingers, mascarpone",
         "image_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=400"},
        {"name": "Chocolate Lava Cake", "price": 8.99, "category": "Desserts",
         "description": "Warm cake with molten chocolate center",
         "image_url": "https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=400"},
        # Drinks
        {"name": "Fresh Lemonade", "price": 3.99, "category": "Drinks",
         "description": "Freshly squeezed, hint of mint",
         "image_url": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400"},
        {"name": "Espresso", "price": 2.99, "category": "Drinks",
         "description": "Rich Italian roast",
         "image_url": "https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=400"},
    ]
    
    # VIP SPECIAL dishes
    vip_dishes = [
        {"name": "🌟 Truffle Pizza", "price": 29.99, "category": "VIP Specials",
         "description": "Black truffle, truffle oil, aged parmesan, arugula",
         "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400",
         "is_special": True},
        {"name": "🌟 Lobster Linguine", "price": 39.99, "category": "VIP Specials",
         "description": "Fresh Maine lobster, white wine cream sauce",
         "image_url": "https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=400",
         "is_special": True},
        {"name": "🌟 Wagyu Beef Burger", "price": 34.99, "category": "VIP Specials",
         "description": "A5 Wagyu patty, foie gras, truffle aioli",
         "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",
         "is_special": True},
        {"name": "🌟 Gold Leaf Cheesecake", "price": 24.99, "category": "VIP Specials",
         "description": "NY cheesecake topped with 24k edible gold",
         "image_url": "https://images.unsplash.com/photo-1508737027454-e6454ef45afd?w=400",
         "is_special": True},
    ]
    
    regular_count = 0
    for d in dishes_data:
        dish = Dish(
            name=d["name"], description=d["description"], price=d["price"],
            category_id=categories[d["category"]].id, chef_id=chef.id,
            is_available=True, is_special=False, average_rating=4.5,
            image_url=d.get("image_url", "")
        )
        db.add(dish)
        regular_count += 1
        print(f"  ✓ {d['name']} (${d['price']})")
    
    vip_count = 0
    for d in vip_dishes:
        dish = Dish(
            name=d["name"], description=d["description"], price=d["price"],
            category_id=categories[d["category"]].id, chef_id=chef.id,
            is_available=True, is_special=True, average_rating=4.9,
            image_url=d.get("image_url", "")
        )
        db.add(dish)
        vip_count += 1
        print(f"  ⭐ {d['name']} (${d['price']}) - VIP ONLY")
    
    db.commit()
    print(f"✅ Created {regular_count} regular dishes + {vip_count} VIP specials")
    return categories


def create_sample_orders(db):
    """Create orders covering different statuses"""
    print("\n📦 Creating sample orders...")
    
    customer1 = db.query(Customer).join(User).filter(User.username == "customer").first()
    customer2 = db.query(Customer).join(User).filter(User.username == "customer2").first()
    vip_customer = db.query(Customer).join(User).filter(User.username == "vip").first()
    delivery1 = db.query(DeliveryPerson).join(User).filter(User.username == "delivery").first()
    delivery2 = db.query(DeliveryPerson).join(User).filter(User.username == "delivery2").first()
    dishes = db.query(Dish).filter(Dish.is_special == False).all()
    vip_dishes = db.query(Dish).filter(Dish.is_special == True).all()
    
    orders = []
    
    # ==================== ORDER 1: DELIVERED (for customer - can rate/compliment) ====================
    order1 = Order(
        customer_id=customer1.id, order_number="ORD-001",
        status=OrderStatus.DELIVERED, payment_status=PaymentStatus.PAID,
        subtotal=27.98, discount_amount=0, delivery_fee=3.99, total_amount=31.97,
        delivery_address=customer1.address,
        created_at=datetime.utcnow() - timedelta(days=2)
    )
    db.add(order1)
    db.flush()
    
    db.add(OrderItem(order_id=order1.id, dish_id=dishes[0].id, quantity=1, 
                     unit_price=dishes[0].price, total_price=dishes[0].price))
    db.add(OrderItem(order_id=order1.id, dish_id=dishes[3].id, quantity=1,
                     unit_price=dishes[3].price, total_price=dishes[3].price))
    
    db.add(Delivery(
        order_id=order1.id, delivery_person_id=delivery1.id,
        pickup_address="AI-Slice Kitchen", delivery_address=customer1.address,
        status=DeliveryStatus.DELIVERED, delivery_fee=3.99,
        actual_delivery_time=datetime.utcnow() - timedelta(days=2, hours=-1)
    ))
    orders.append(order1)
    print(f"  ✓ Order #1: DELIVERED (customer - can give feedback)")
    
    # ==================== ORDER 2: DELIVERED (for customer - rated) ====================
    order2 = Order(
        customer_id=customer1.id, order_number="ORD-002",
        status=OrderStatus.DELIVERED, payment_status=PaymentStatus.PAID,
        subtotal=14.99, discount_amount=0, delivery_fee=3.99, total_amount=18.98,
        delivery_address=customer1.address, food_rating=5.0, delivery_rating=4.5,
        created_at=datetime.utcnow() - timedelta(days=1)
    )
    db.add(order2)
    db.flush()
    
    db.add(OrderItem(order_id=order2.id, dish_id=dishes[1].id, quantity=1,
                     unit_price=dishes[1].price, total_price=dishes[1].price))
    
    db.add(Delivery(
        order_id=order2.id, delivery_person_id=delivery2.id,
        pickup_address="AI-Slice Kitchen", delivery_address=customer1.address,
        status=DeliveryStatus.DELIVERED, delivery_fee=3.99
    ))
    orders.append(order2)
    print(f"  ✓ Order #2: DELIVERED + RATED (customer)")
    
    # ==================== ORDER 3: PREPARING (chef working on it) ====================
    order3 = Order(
        customer_id=customer2.id, order_number="ORD-003",
        status=OrderStatus.PREPARING, payment_status=PaymentStatus.PAID,
        subtotal=24.98, discount_amount=0, delivery_fee=3.99, total_amount=28.97,
        delivery_address=customer2.address,
        created_at=datetime.utcnow() - timedelta(minutes=15)
    )
    db.add(order3)
    db.flush()
    
    db.add(OrderItem(order_id=order3.id, dish_id=dishes[0].id, quantity=1,
                     unit_price=dishes[0].price, total_price=dishes[0].price))
    db.add(OrderItem(order_id=order3.id, dish_id=dishes[4].id, quantity=1,
                     unit_price=dishes[4].price, total_price=dishes[4].price))
    
    # Delivery awaiting - chef will mark ready
    db.add(Delivery(
        order_id=order3.id, pickup_address="AI-Slice Kitchen",
        delivery_address=customer2.address, status=DeliveryStatus.PENDING_BIDDING,
        delivery_fee=3.99
    ))
    orders.append(order3)
    print(f"  ✓ Order #3: PREPARING (chef can mark ready)")
    
    # ==================== ORDER 4: READY - PENDING BIDDING (delivery can bid) ====================
    order4 = Order(
        customer_id=customer1.id, order_number="ORD-004",
        status=OrderStatus.READY_FOR_DELIVERY, payment_status=PaymentStatus.PAID,
        subtotal=8.99, discount_amount=0, delivery_fee=3.99, total_amount=12.98,
        delivery_address=customer1.address,
        created_at=datetime.utcnow() - timedelta(minutes=30)
    )
    db.add(order4)
    db.flush()
    
    db.add(OrderItem(order_id=order4.id, dish_id=dishes[5].id, quantity=1,
                     unit_price=dishes[5].price, total_price=dishes[5].price))
    
    delivery4 = Delivery(
        order_id=order4.id, pickup_address="AI-Slice Kitchen",
        delivery_address=customer1.address, status=DeliveryStatus.PENDING_BIDDING,
        delivery_fee=3.99
    )
    db.add(delivery4)
    db.flush()
    
    # Add a sample bid from delivery2
    db.add(DeliveryBid(
        delivery_id=delivery4.id, delivery_person_id=delivery2.id,
        bid_amount=4.99, estimated_time=20,
        created_at=datetime.utcnow() - timedelta(minutes=5)
    ))
    orders.append(order4)
    print(f"  ✓ Order #4: READY - waiting for bids (has 1 bid)")
    
    # ==================== ORDER 5: VIP ORDER - PLACED (new) ====================
    order5 = Order(
        customer_id=vip_customer.id, order_number="ORD-005",
        status=OrderStatus.PLACED, payment_status=PaymentStatus.PAID,
        subtotal=39.99, discount_amount=2.00, delivery_fee=0, total_amount=37.99,
        is_vip_order=True, is_free_delivery=True,
        delivery_address=vip_customer.address,
        created_at=datetime.utcnow() - timedelta(minutes=5)
    )
    db.add(order5)
    db.flush()
    
    db.add(OrderItem(order_id=order5.id, dish_id=vip_dishes[1].id, quantity=1,
                     unit_price=vip_dishes[1].price, total_price=vip_dishes[1].price))
    
    db.add(Delivery(
        order_id=order5.id, pickup_address="AI-Slice Kitchen",
        delivery_address=vip_customer.address, status=DeliveryStatus.PENDING_BIDDING,
        delivery_fee=0
    ))
    orders.append(order5)
    print(f"  ⭐ Order #5: VIP ORDER - PLACED (chef should see)")
    
    db.commit()
    print(f"✅ Created {len(orders)} orders covering all statuses")
    return orders


def create_sample_feedback(db):
    """Create complaints and compliments"""
    print("\n💬 Creating sample feedback...")
    
    customer1 = db.query(User).filter(User.username == "customer").first()
    customer2 = db.query(User).filter(User.username == "customer2").first()
    vip = db.query(User).filter(User.username == "vip").first()
    chef = db.query(User).filter(User.username == "chef").first()
    delivery1 = db.query(User).filter(User.username == "delivery").first()
    delivery2 = db.query(User).filter(User.username == "delivery2").first()
    orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).all()
    
    # ==================== COMPLIMENTS ====================
    # Customer → Chef
    db.add(Compliment(
        giver_id=customer1.id, receiver_id=chef.id,
        order_id=orders[0].id if orders else None,
        title="Best Pizza Ever!",
        description="The Margherita was perfectly cooked. Crispy crust, fresh ingredients!",
        weight=1, created_at=datetime.utcnow() - timedelta(hours=12)
    ))
    print(f"  ✓ Compliment: customer → chef (Best Pizza!)")
    
    # Customer → Delivery
    db.add(Compliment(
        giver_id=customer1.id, receiver_id=delivery1.id,
        order_id=orders[0].id if orders else None,
        title="Lightning Fast Delivery",
        description="Arrived in 15 minutes, food was still hot!",
        weight=1, created_at=datetime.utcnow() - timedelta(hours=10)
    ))
    print(f"  ✓ Compliment: customer → delivery (Fast Delivery)")
    
    # VIP → Chef (counts double)
    db.add(Compliment(
        giver_id=vip.id, receiver_id=chef.id,
        title="Exceptional VIP Experience",
        description="The Lobster Linguine was restaurant quality. Worth every penny!",
        weight=2, created_at=datetime.utcnow() - timedelta(hours=5)
    ))
    print(f"  ⭐ Compliment: VIP → chef (Exceptional - 2x weight)")
    
    # Customer2 → Delivery2
    db.add(Compliment(
        giver_id=customer2.id, receiver_id=delivery2.id,
        title="Super Friendly!",
        description="Lisa was so nice and even helped carry groceries.",
        weight=1, created_at=datetime.utcnow() - timedelta(hours=3)
    ))
    print(f"  ✓ Compliment: customer2 → delivery2 (Friendly)")
    
    # ==================== COMPLAINTS ====================
    # Resolved complaint
    db.add(Complaint(
        complainant_id=vip.id, subject_id=delivery1.id,
        order_id=orders[1].id if len(orders) > 1 else None,
        title="Late Delivery",
        description="Order arrived 30 minutes late. The pasta was cold.",
        status=ComplaintStatus.RESOLVED,
        manager_decision="Warning issued to driver. Customer credited $5.",
        weight=2, created_at=datetime.utcnow() - timedelta(days=3)
    ))
    print(f"  ✓ Complaint: VIP → delivery (Late - RESOLVED)")
    
    # Pending complaint (manager needs to review)
    db.add(Complaint(
        complainant_id=customer1.id, subject_id=chef.id,
        title="Missing Item",
        description="Ordered 2 pizzas but only received 1. Please check.",
        status=ComplaintStatus.PENDING,
        weight=1, created_at=datetime.utcnow() - timedelta(hours=2)
    ))
    print(f"  ⚠️ Complaint: customer → chef (Missing Item - PENDING)")
    
    # Another pending complaint
    db.add(Complaint(
        complainant_id=customer2.id, subject_id=delivery1.id,
        title="Rude Behavior",
        description="Driver was impatient and threw the bag at my door.",
        status=ComplaintStatus.PENDING,
        weight=1, created_at=datetime.utcnow() - timedelta(hours=1)
    ))
    print(f"  ⚠️ Complaint: customer2 → delivery (Rude - PENDING)")
    
    db.commit()
    print(f"✅ Created 4 compliments + 3 complaints (2 pending for manager)")


def print_summary():
    """Print summary"""
    print("\n" + "=" * 70)
    print("🎉 DATABASE SEEDED SUCCESSFULLY!")
    print("=" * 70)
    
    print("""
📊 DATA SUMMARY:
  • Users: 10 total
    - 1 Manager
    - 1 Chef  
    - 2 Delivery Drivers
    - 2 Customers + 1 VIP
    - 3 Pending (1 customer, 1 delivery, 1 chef)
  • Menu: 11 regular + 4 VIP specials = 15 dishes
  • Orders: 5 (various statuses)
  • Feedback: 4 compliments + 3 complaints
""")
    
    print("=" * 70)
    print("🔑 LOGIN ACCOUNTS (password: password123)")
    print("=" * 70)
    
    print("""
┌────────────────────────────────────────────────────────────────────┐
│  ROLE           │  EMAIL                │  NAME          │ NOTES  │
├────────────────────────────────────────────────────────────────────┤
│  👔 Manager     │  manager@test.com     │  Sarah Manager │ Admin  │
│  👨‍🍳 Chef        │  chef@test.com        │  Mario Chef    │        │
│  🚴 Delivery    │  delivery@test.com    │  Dan Driver    │ Motor  │
│  🚴 Delivery    │  delivery2@test.com   │  Lisa Swift    │ Bike   │
│  👤 Customer    │  customer@test.com    │  Alice         │ $150   │
│  👤 Customer    │  customer2@test.com   │  Bob Smith     │ $75    │
│  ⭐ VIP         │  vip@test.com         │  Victoria VIP  │ $500   │
├────────────────────────────────────────────────────────────────────┤
│  ⏳ PENDING     │  john@email.com       │  John Newuser  │ Cust   │
│  ⏳ PENDING     │  mike.driver@email.com│  Mike Driver   │ Deliv  │
│  ⏳ PENDING     │  anna.chef@email.com  │  Anna Baker    │ Chef   │
└────────────────────────────────────────────────────────────────────┘
""")
    
    print("""
🎬 DEMO FLOWS:
═══════════════════════════════════════════════════════════════════

1️⃣  MANAGER APPROVAL (manager@test.com)
    • "Hiring" tab → 3 pending users to approve/reject
    • Approve John (customer), Mike (delivery), Anna (chef)

2️⃣  CHEF WORKFLOW (chef@test.com)
    • Order #3: PREPARING → Click "Mark Ready for Delivery"
    • Order #5: PLACED (VIP) → Click "Start Cooking"
    • "My Feedback" → See compliments & pending complaint

3️⃣  DELIVERY BIDDING (delivery@test.com or delivery2@test.com)
    • See Order #4 ready for delivery
    • Place bid → Manager assigns in "Deliveries" tab
    • delivery2 already has 1 bid on Order #4

4️⃣  CUSTOMER FLOW (customer@test.com)
    • 2 delivered orders → Can rate/compliment
    • "My Feedback" → See filed complaints/compliments
    • Browse menu → Order more food

5️⃣  VIP EXCLUSIVE (vip@test.com)
    • Browse Menu → See VIP SPECIALS (🌟 items)
    • 5% discount + Free delivery
    • Order #5 is their pending VIP order

6️⃣  COMPLAINT RESOLUTION (manager@test.com)
    • "Complaints" tab → 2 pending complaints
    • Review and resolve with decision

═══════════════════════════════════════════════════════════════════
""")


def main():
    print("🌱 AI-Slice Database Seeder")
    print("=" * 70)
    
    response = input("\n⚠️  This will CLEAR all existing data. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    db = SessionLocal()
    
    try:
        clear_database()
        create_users(db)
        create_menu(db)
        create_sample_orders(db)
        create_sample_feedback(db)
        print_summary()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
