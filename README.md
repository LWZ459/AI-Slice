# AI-Slice 🍕🤖

**AI-Enabled Online Restaurant Order & Delivery System**

A sophisticated restaurant management platform that combines traditional online ordering with AI-powered customer interaction, competitive delivery bidding, and comprehensive reputation management.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [User Types & Capabilities](#user-types--capabilities)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Detailed Installation](#detailed-installation)
- [Configuration Guide](#configuration-guide)
- [Running the Application](#running-the-application)
- [Core Services](#core-services)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## 🎯 Overview

AI-Slice is an intelligent restaurant order and delivery system that uses AI (Large Language Models) to provide instant customer support, implements a competitive bidding system for deliveries, and maintains a comprehensive reputation system to ensure quality service.

### Project Goals

- LLM-based customer support (free OSS from Ollama/Hugging Face)
- Independent chef menu management
- Competitive delivery bidding
- AI-powered Q&A with local knowledge base fallback
- Comprehensive reputation tracking for all users
- VIP customer programs with automatic discounts

---

## ✨ Key Features

### 🤖 AI-Powered Support
- **Dual-Mode System**: Queries local knowledge base first, falls back to external LLM
- **Smart Q&A**: Answers questions about menu, restaurant, and policies
- **Quality Tracking**: Users rate answers; poor ratings flag content for manager review
- **Menu Recommendations**: Personalized suggestions based on order history

### 🍽️ Restaurant Operations
- **Independent Chef Management**: Chefs autonomously create and manage dishes
- **Chef Specials**: VIP-exclusive dishes
- **Popularity Tracking**: Real-time dish orders and ratings

### 🚚 Delivery System
- **Competitive Bidding**: Delivery personnel bid on orders
- **Auto-Assignment**: System automatically assigns to lowest bidder
- **Manager Override**: Managers can override with required justification

### 💰 Financial Management
- **Wallet System**: Pre-paid accounts for all customers
- **Automatic Validation**: Orders exceeding balance auto-rejected
- **VIP Discounts**: Automatic 5% discount
- **Free Deliveries**: 1 free delivery per 3 VIP orders

### 🏆 Reputation System
- **Comprehensive Tracking**: Monitors complaints, compliments, warnings
- **VIP Qualification**: Automatic promotion (>$100 spent OR 3+ orders)
- **Weighted Feedback**: VIP complaints/compliments count double
- **Automatic Actions**: Demotions, firings, blacklisting based on reputation

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.9+
- Git

### Installation Steps

```bash
# 1. Clone repository (if not already done)
git clone git@github.com:Ahmedh27/AI-Slice.git
cd AI-Slice

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
cd backend
pip install -r requirements.txt

# 5. Quick config for development (SQLite)
cat > .env << EOF
DATABASE_URL=sqlite:///./aislice.db
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
USE_LOCAL_LLM=true
DEBUG=true
EOF

# 6. Initialize database
python -c "from app.core.database import init_db; init_db()"

# 7. Run the application
python run.py
```

### Access Points

- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

**That's it!** You now have a running AI-Slice server.

### 📮 Testing with Postman

**Import the collection:**
1. Open Postman
2. Click **Import** → **File**
3. Select: `AI-Slice.postman_collection.json`
4. Start testing 42 pre-configured endpoints!

The collection includes auto-token management - just login and the JWT is saved automatically.

---

## 👤 User Types & Capabilities

### 1. Visitors
- Browse menus and restaurant information
- Ask questions via AI chat
- Apply for customer registration
- **Cannot**: Place orders or participate in discussions

### 2. Registered Customers
- All visitor capabilities, plus:
- Place orders and rate food/delivery separately
- File complaints/compliments
- Participate in discussion forums
- Deposit money into wallet
- View personalized homepage

### 3. VIP Customers
**Qualification**: Spending >$100 OR 3+ orders without complaints

**Benefits**:
- 5% discount on all orders
- 1 free delivery per 3 orders
- Access to chef special dishes
- Complaints/compliments count double (2x weight)

**Demotion**: After 2 warnings (clears warnings upon demotion)

### 4. Chefs (Employees)
- Create and manage menu items independently
- View assigned orders
- Receive ratings from customers
- File/dispute complaints

**Performance Rules**:
- Rating <2.0 or 3 complaints → Demotion
- 2 demotions → Fired
- Rating >4.0 or 3 compliments → Bonus

### 5. Delivery Personnel (Employees)
- View available deliveries
- Bid on delivery orders
- Update delivery status
- File/dispute complaints

**Performance Rules**: Same as chefs

### 6. Manager
- Process customer registrations (approve/reject)
- Handle all complaints/compliments
- Make final decisions on disputes
- Hire, fire, promote, demote employees
- Assign deliveries (with justification if overriding)
- Review AI responses
- Manage knowledge base

**🔐 Manager Creation**:

Managers must be created using a special bootstrap endpoint with a secret code:

```bash
POST /api/manager/create-manager
{
  "username": "admin",
  "email": "admin@aislice.com",
  "password": "secure_password",
  "full_name": "Admin User",
  "secret_code": "create-manager-2025"
}
```

**⚠️ Security Note**: The secret code (`create-manager-2025`) should be changed in production and stored securely.

**📋 Customer Approval Workflow**:

1. **New users register** → Status: `PENDING`
2. **Manager reviews** → `GET /api/manager/pending-registrations`
3. **Manager approves** → `POST /api/manager/approve-customer/{user_id}` → Status: `ACTIVE`
4. **OR Manager rejects** → `POST /api/manager/reject-customer/{user_id}?reason=...` → Status: `DEACTIVATED`

**Quick Approve All** (for testing):
```bash
POST /api/manager/activate-all-users
```

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL / SQLite
- **Authentication**: JWT (python-jose)
- **Password**: bcrypt

### AI/ML
- **Local LLM**: Ollama (free, open-source) - Recommended
- **Alternative**: OpenAI API
- **Vector DB**: ChromaDB
- **Framework**: LangChain

### Infrastructure
- **Server**: Uvicorn (ASGI)
- **Tasks**: Celery
- **Cache**: Redis

---

## 📁 Project Structure

```
AI-Slice/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── core/
│   │   │   ├── config.py        # Settings
│   │   │   └── database.py      # DB setup
│   │   ├── models/              # Database models
│   │   │   ├── user.py          # User types
│   │   │   ├── menu.py          # Dishes
│   │   │   ├── order.py         # Orders
│   │   │   ├── wallet.py        # Payments
│   │   │   ├── reputation.py    # Reputation
│   │   │   ├── delivery.py      # Delivery
│   │   │   └── ai.py            # AI/KB
│   │   ├── services/            # Business logic
│   │   │   ├── order_service.py
│   │   │   ├── payment_service.py
│   │   │   ├── delivery_service.py
│   │   │   ├── ai_service.py
│   │   │   └── reputation_service.py
│   │   ├── api/                 # API routes (TODO)
│   │   └── schemas/             # Pydantic schemas (TODO)
│   ├── requirements.txt
│   ├── run.py
│   └── setup.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/      # Shared components
│   │   ├── contexts/        # React Contexts (Auth, Cart)
│   │   ├── config/          # API config
│   │   ├── userComps/       # Customer pages
│   │   ├── chefComps/       # Chef dashboard
│   │   ├── deliveryComps/   # Delivery dashboard
│   │   ├── managerComps/    # Manager dashboard
│   │   ├── discussionComps/ # Chat & Forums
│   │   ├── searchComps/     # Menu browsing
│   │   ├── checkoutComps/   # Checkout flow
│   │   ├── biddingComps/    # Delivery bidding
│   │   ├── navComps/        # Navigation
│   │   ├── App.js           # Main router
│   │   └── index.js         # Entry point
│   └── package.json
├── tests/
├── pseudocode.md                # Implementation pseudocode
└── README.md                    # This file
```

---

## 🔧 Detailed Installation

### Option 1: SQLite (Development - Simplest)

**Pros**: No installation needed, simple setup  
**Cons**: Not for production

```bash
cd backend

# Set in .env
echo "DATABASE_URL=sqlite:///./aislice.db" > .env
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" >> .env

# Initialize
python -c "from app.core.database import init_db; init_db()"
```

### Option 2: PostgreSQL (Production)

**Install PostgreSQL**:

```bash
# macOS
brew install postgresql@14
brew services start postgresql@14

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Create Database**:

```bash
sudo -u postgres psql
CREATE DATABASE aislice_db;
CREATE USER aislice_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE aislice_db TO aislice_user;
\q
```

**Configure**:

```bash
# In .env
DATABASE_URL=postgresql://aislice_user:your_password@localhost:5432/aislice_db
```

### AI/LLM Setup

**Option A: Ollama (Local, Free - Recommended)**

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start server
ollama serve

# Configure in .env
USE_LOCAL_LLM=true
OLLAMA_BASE_URL=http://localhost:11434
```

**Option B: OpenAI API**

```bash
# In .env
USE_LOCAL_LLM=false
OPENAI_API_KEY=sk-your-api-key-here
```

---

## ⚙️ Configuration Guide

Create `.env` file in `backend/` directory:

```bash
# Database
DATABASE_URL=sqlite:///./aislice.db

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration
USE_LOCAL_LLM=true
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=  # Only if USE_LOCAL_LLM=false

# Application
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# VIP Settings
VIP_SPENDING_THRESHOLD=100.0
VIP_ORDER_THRESHOLD=3
VIP_DISCOUNT_PERCENTAGE=5.0
VIP_FREE_DELIVERY_FREQUENCY=3

# Reputation Settings
WARNING_THRESHOLD_DEREGISTER=3
WARNING_THRESHOLD_VIP_DEMOTION=2
BLACKLIST_REPUTATION_THRESHOLD=-50
VIP_REPUTATION_THRESHOLD=100

# Performance Rules
CHEF_LOW_RATING_THRESHOLD=2.0
CHEF_HIGH_RATING_THRESHOLD=4.0
COMPLAINTS_FOR_DEMOTION=3
COMPLIMENTS_FOR_BONUS=3
```

**Generate Secure Secret Key**:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🎮 Running the Application

### Development Mode

```bash
cd backend
python run.py
```

Server starts at `http://localhost:8000` with auto-reload enabled.

### Production Mode

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Systemd (Linux Production)

Create `/etc/systemd/system/aislice.service`:

```ini
[Unit]
Description=AI-Slice API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/AI-Slice/backend
Environment="PATH=/path/to/AI-Slice/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable aislice
sudo systemctl start aislice
```

---

## 🔧 Core Services

### OrderService (`order_service.py`)

Handles order creation and management.

**Key Method**: `create_order(customer_id, cart_items)`

**Features**:
- Cart validation and item availability checking
- Automatic VIP discount application (5%)
- Wallet balance verification
- Automatic rejection on insufficient funds
- Reputation event recording

### PaymentService (`payment_service.py`)

Manages all financial transactions.

**Key Method**: `process_payment(order_id, customer_id, amount)`

**Features**:
- Wallet balance management
- Payment processing with transaction records
- Deposit and refund handling
- Complete transaction history

### DeliveryService (`delivery_service.py`)

Handles delivery bidding and assignment.

**Key Method**: `assign_agent(order_id, override_id, justification)`

**Features**:
- Delivery listing creation
- Bid placement and sorting
- Automatic assignment to lowest bidder
- Manager override with justification
- Status tracking throughout delivery

### AIEngine (`ai_service.py`)

Provides AI-powered features.

**Key Methods**: 
- `answer_question(user_id, question_text)` - Dual-mode Q&A
- `recommend_menu(user_id, context)` - Personalized recommendations

**Features**:
- Local KB search first, LLM fallback
- Answer quality rating and flagging
- Personalized menu recommendations
- Knowledge base management

### ReputationService (`reputation_service.py`)

Tracks and manages user reputation.

**Key Method**: `record_event(user_id, event_type, details)`

**Features**:
- Event recording (complaints, compliments, warnings)
- Score calculation and threshold management
- VIP promotion/demotion
- Blacklist management
- Weighted feedback (VIP = 2x)

---

## 🗄️ Database Schema

### Core Tables

- **users** - Base user info, authentication, account status
- **customers** - Customer data, VIP status, order history
- **chefs** - Chef profiles, specialization, performance
- **delivery_persons** - Delivery staff, vehicle info, availability
- **managers** - Manager profiles and access levels
- **visitors** - Registration applicants

- **dishes** - Menu items with pricing, images, tags
- **dish_categories** - Dish organization

- **orders** - Order records with status workflow
- **order_items** - Individual items in orders

- **wallets** - Customer wallets with balances
- **transactions** - Complete financial history

- **deliveries** - Delivery records with assignments
- **delivery_bids** - Competitive bids for deliveries

- **reputations** - User reputation scores
- **reputation_events** - Reputation history
- **complaints** - Complaint records with resolution
- **compliments** - Compliment records

- **knowledge_base** - AI local answers
- **chat_logs** - AI interaction history
- **question_ratings** - Answer quality tracking

**Total**: 15+ comprehensive tables with relationships

---

## 📚 API Documentation

### 📮 Postman Collection

Import `AI-Slice.postman_collection.json` into Postman for:
- ✅ 42 pre-configured API requests
- ✅ Auto-token management (JWT saved after login)
- ✅ Sample request bodies
- ✅ Organized into 7 categories

### Key Endpoints

**Authentication**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (get JWT token)

**Orders**
- `GET /api/orders` - List orders
- `POST /api/orders` - Create order
- `PUT /api/orders/{id}/rate` - Rate order

**Menu**
- `GET /api/menu` - Browse menu
- `POST /api/menu` - Create dish (chef)
- `GET /api/menu/recommendations` - Get recommendations

**Delivery**
- `GET /api/delivery/available` - List deliveries
- `POST /api/delivery/{id}/bid` - Place bid
- `POST /api/delivery/{id}/assign` - Assign (manager)

**AI**
- `POST /api/ai/ask` - Ask question
- `POST /api/ai/rate` - Rate answer

**Reputation**
- `POST /api/reputation/complaint` - File complaint
- `POST /api/reputation/compliment` - Give compliment

---

## 👨‍💻 Development Guide

### Code Style

```bash
# Format code
black app/

# Lint
flake8 app/

# Type check
mypy app/
```

### Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_orders.py
```

### Adding Features

1. Create models in `app/models/`
2. Implement logic in `app/services/`
3. Add endpoints in `app/api/`
4. Create schemas in `app/schemas/`
5. Write tests in `tests/`

### Database Migrations

```bash
# Install Alembic
pip install alembic

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U aislice_user -d aislice_db -h localhost
```

### Import Errors

```bash
# Ensure venv is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
```

### Ollama Not Connecting

```bash
# Check if running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull model
ollama pull llama2
```

### Database Reset (CAUTION: Deletes Data)

```bash
# SQLite
rm aislice.db
python -c "from app.core.database import init_db; init_db()"

# PostgreSQL
python -c "from app.core.database import Base, engine; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"
```

---

## 🔜 Next Steps

### Immediate Priorities

1. **API Endpoints** - Implement routes in `app/api/`
2. **Authentication** - JWT token generation/validation
3. **Testing** - Unit and integration tests
4. **Seed Data** - Sample data for testing

### Short Term

- Frontend development (React/Vue.js)
- Real-time updates (WebSocket)
- Email notifications
- File uploads for dish images
- Payment gateway integration

### Long Term

- Mobile apps (iOS & Android)
- Analytics dashboard
- Voice ordering
- Route optimization for deliveries
- Multi-language support

---

## 📊 Project Status

**✅ Completed**:
- Backend structure
- 5 core services (Order, Payment, Delivery, AI, Reputation)
- 15+ database models
- Configuration system
- Documentation

**🚧 In Progress**:
- API endpoints
- Authentication
- Testing suite

**📋 Planned**:
- Frontend interface
- Real-time features
- Mobile apps

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Team

**Course**: Software Engineering  
**Semester**: Fall 2025

**Repository**: https://github.com/Ahmedh27/AI-Slice

---

## 🙏 Acknowledgments

- FastAPI framework
- Ollama for local LLM
- SQLAlchemy ORM
- Open-source community

---

**Built with ❤️ and 🤖**

For questions or issues, create an issue on GitHub.
