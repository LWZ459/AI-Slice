# API Endpoints Reference

Complete API endpoints for AI-Slice backend.

**Base URL**: `http://localhost:8000`  
**API Docs**: `http://localhost:8000/docs` (Interactive Swagger UI)

---

## 🔐 Authentication (`/api/auth`)

### POST `/api/auth/register`
Register a new user (requires manager approval)
- **Body**: `{email, username, password, user_type}`
- **Returns**: User object
- **Status**: 201 Created

### POST `/api/auth/login`
Login and get JWT token
- **Body**: `{username, password}`
- **Returns**: `{access_token, token_type}`
- **Use**: Include token in headers: `Authorization: Bearer <token>`

### GET `/api/auth/me`
Get current user info
- **Auth**: Required
- **Returns**: User object

### POST `/api/auth/logout`
Logout (client-side token discard)
- **Auth**: Required

---

## 📦 Orders (`/api/orders`)

### POST `/api/orders/`
Create a new order
- **Auth**: Customer/VIP only
- **Body**: `{items: [{dish_id, quantity}], delivery_address}`
- **Returns**: Order confirmation
- **Features**: Auto VIP discount, wallet validation

### GET `/api/orders/`
List your orders
- **Auth**: Required
- **Query**: `skip`, `limit`, `status_filter`
- **Returns**: List of orders

### GET `/api/orders/{order_id}`
Get order details
- **Auth**: Required (own orders only)
- **Returns**: Full order info with items

### PUT `/api/orders/{order_id}/rate`
Rate an order
- **Auth**: Customer/VIP only
- **Body**: `{food_rating, delivery_rating}` (1-5 stars)
- **Must**: Order be completed

### DELETE `/api/orders/{order_id}`
Cancel an order
- **Auth**: Required
- **Returns**: Cancellation confirmation + refund

---

## 🍽️ Menu (`/api/menu`)

### GET `/api/menu/`
Browse available dishes
- **Query**: `category_id`, `chef_id`, `search`, `min_price`, `max_price`, `include_special`
- **Returns**: List of dishes

### GET `/api/menu/recommendations`
Get personalized recommendations
- **Auth**: Required
- **Query**: `time_of_day` (morning/lunch/dinner/night)
- **Returns**: Recommended dishes based on history

### GET `/api/menu/{dish_id}`
Get dish details
- **Returns**: Dish information

### POST `/api/menu/`
Create a new dish
- **Auth**: Chef only
- **Body**: `{name, description, price, category_id, is_special}`
- **Returns**: Created dish

### PUT `/api/menu/{dish_id}`
Update a dish
- **Auth**: Chef only (own dishes)
- **Body**: Fields to update
- **Returns**: Updated dish

### DELETE `/api/menu/{dish_id}`
Delete a dish
- **Auth**: Chef only (own dishes)
- **Action**: Marks as unavailable

### GET `/api/menu/categories/`
List all categories
- **Returns**: List of categories

### POST `/api/menu/categories/`
Create a category
- **Auth**: Manager only
- **Body**: `{name, description}`

---

## 🚚 Delivery (`/api/delivery`)

### GET `/api/delivery/available`
List deliveries for bidding
- **Auth**: Delivery personnel only
- **Returns**: Active delivery listings

### POST `/api/delivery/{delivery_id}/bid`
Place a bid on delivery
- **Auth**: Delivery personnel only
- **Body**: `{bid_amount, estimated_time, notes}`
- **Returns**: Bid confirmation

### GET `/api/delivery/{delivery_id}/bids`
View all bids for a delivery
- **Auth**: Manager only
- **Returns**: List of bids (sorted by amount)

### POST `/api/delivery/{delivery_id}/assign`
Assign delivery (manual)
- **Auth**: Manager only
- **Body**: `{delivery_person_id, justification}`
- **Note**: Justification required if not lowest bidder

### POST `/api/delivery/{delivery_id}/auto-assign`
Auto-assign to lowest bidder
- **Auth**: Manager only
- **Returns**: Assignment confirmation

### PUT `/api/delivery/{delivery_id}/status`
Update delivery status
- **Auth**: Delivery personnel only (assigned deliveries)
- **Body**: `{status}` (picked_up/in_transit/delivered)

### GET `/api/delivery/my-deliveries`
Get my deliveries
- **Auth**: Delivery personnel only
- **Returns**: Current and past deliveries

### GET `/api/delivery/{delivery_id}`
Get delivery details
- **Auth**: Required
- **Returns**: Delivery information

---

## 🤖 AI Chat (`/api/ai`)

### POST `/api/ai/ask`
Ask a question
- **Auth**: Optional (visitors can ask)
- **Body**: `{question}`
- **Returns**: `{question, answer, source, can_rate}`
- **Features**: Local KB → LLM fallback

### POST `/api/ai/rate`
Rate an answer
- **Body**: `{chat_log_id, rating, feedback}` (0-5 stars)
- **Note**: 0-1 ratings flag for manager review

### GET `/api/ai/recommendations`
Get menu recommendations
- **Auth**: Required
- **Query**: `time_of_day`
- **Returns**: Personalized dish list

### GET `/api/ai/knowledge-base`
List KB entries
- **Auth**: Manager only
- **Query**: `flagged_only` (bool)
- **Returns**: KB entries

### POST `/api/ai/knowledge-base`
Create KB entry
- **Auth**: Manager only
- **Body**: `{question, answer, category, tags}`

### PUT `/api/ai/knowledge-base/{kb_id}`
Update KB entry
- **Auth**: Manager only
- **Body**: Updated Q&A

### DELETE `/api/ai/knowledge-base/{kb_id}`
Delete KB entry
- **Auth**: Manager only

---

## 🏆 Reputation (`/api/reputation`)

### POST `/api/reputation/complaint`
File a complaint
- **Auth**: Required
- **Body**: `{subject_id, title, description, order_id?}`
- **Note**: VIP complaints count 2x

### POST `/api/reputation/compliment`
Give a compliment
- **Auth**: Required
- **Body**: `{receiver_id, title, description, order_id?}`
- **Note**: VIP compliments count 2x, cancels 1 complaint

### GET `/api/reputation/complaints`
List complaints
- **Auth**: Required
- **Query**: `status_filter`
- **Returns**: Your complaints or all (if manager)

### GET `/api/reputation/complaints/{complaint_id}`
Get complaint details
- **Auth**: Required (involved parties or manager)

### POST `/api/reputation/complaints/{complaint_id}/dispute`
Dispute a complaint
- **Auth**: Required (subject of complaint)
- **Body**: `{dispute_reason}`

### POST `/api/reputation/complaints/{complaint_id}/decide`
Manager decision on complaint
- **Auth**: Manager only
- **Body**: `{decision, action}` (resolve/reject/warn)

### GET `/api/reputation/{user_id}/reputation`
Get user reputation
- **Auth**: Required
- **Returns**: Reputation score and stats

### GET `/api/reputation/my-warnings`
Get your warning count
- **Auth**: Required
- **Returns**: Warning count and thresholds

### POST `/api/reputation/warn`
Issue a warning
- **Auth**: Manager only
- **Body**: `{user_id, reason}`

---

## 📊 Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {...}
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

### Authentication
Include JWT token in all authenticated requests:
```
Authorization: Bearer <your_token_here>
```

---

## 🎯 Quick Examples

### Register & Login
```bash
# Register
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"testuser","password":"password123","user_type":"customer"}'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### Browse Menu
```bash
curl "http://localhost:8000/api/menu/?limit=10"
```

### Ask AI Question
```bash
curl -X POST "http://localhost:8000/api/ai/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"What are your most popular dishes?"}'
```

### Create Order (requires auth)
```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"dish_id":1,"quantity":2}],"delivery_address":"123 Main St"}'
```

---

## 📚 Interactive Documentation

Visit `http://localhost:8000/docs` for:
- ✅ Complete API documentation
- ✅ Try endpoints directly in browser
- ✅ See all request/response schemas
- ✅ Test authentication
- ✅ View examples

---

**Total Endpoints**: 40+  
**Categories**: 6 (Auth, Orders, Menu, Delivery, AI, Reputation)  
**Authentication**: JWT Bearer tokens  
**Documentation**: Auto-generated Swagger UI

