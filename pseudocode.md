4.  Detailed Design (Pseudo-Code for Core Methods) 

Write for each major class/method: 

4.1 OrderService.createOrder(customerId, cartItems) 

Create a new order from the customer’s cart. Check menu items, apply VIP discount, and make sure the wallet has enough balance. 

Input: customerId, list of cartItems (dishId, quantity) 

Output: orderId if success, or error message if failed 

Pseudo-code (informal): 

If (cartItems is empty)  

→ Error: "Cart is empty. Cannot create order" 

Load customer by customerId 

If (no such customer)  

→ Error: "Customer not found" 

For each item in cartItems 

Check if dish exists and is available in Menu 

If (dish missing OR dish unavailable)  

→ Mark this item as unavailable 

If (all items are unavailable)  

→ Error: "All items unavailable. Order cancelled" 

Remove unavailable items from the cart 

Compute totalAmount = sum(dish.price × quantity) 

If (customer is VIP) 

Apply 5% discount → finalAmount = totalAmount × 0.95 

Else finalAmount = totalAmount 

 

Load wallet for this customer 

If (wallet not found)  

→ Error: "Wallet not found" 

If (wallet.balance < finalAmount) 

Call ReputationService to record event: "INSUFFICIENT_FUNDS_ORDER_REJECTED" 

Error: "Insufficient funds. Order rejected" 

Create order record with status = "PENDING_PAYMENT" 

Call PaymentService.processPayment(orderId, customerId, finalAmount) 

If (payment success) 

Update order status → "PLACED" 

Notify chefs that a new order is placed 

Return orderId 

Else (payment failed) 

Update order status → "REJECTED" 

Show error: "Payment failed. Please try again" 

4.2 PaymentService.processPayment(orderId, customerId, amount) 

Handle the payment for an order by checking and updating the user’s wallet. 

Input: orderId, customerId, amount to pay 

Output: status "SUCCESS" or "FAILED" with a message 

Pseudo-code: 

Load wallet by customerId 

If (no wallet found)  

→ Return FAILED + "Wallet not found" 

If (wallet.balance < amount) 

Call ReputationService to record "ORDER_REJECTED_INSUFFICIENT_FUNDS" 

Return FAILED + "Insufficient wallet balance" 

Deduct amount from wallet.balance 

Save updated wallet 

Create a payment transaction record (orderId, amount, method = "WALLET", status = "SUCCESS") 

Update order paymentStatus → "PAID" 

Return SUCCESS + "Payment completed" 

4.3 DeliveryService.assignAgent(orderId) 

Assign a delivery person to an order after the bidding process, or let the manager handle it if no bids. 

Input: orderId 

Output: assigned deliveryPersonId or an error message 

Pseudo-code: 

Load order by orderId 

If (order not found)  

→ Error: "Order not found" 

Load all bids for this order 

If (no bids)	 

Set order.status → "NO_BIDDERS_MANUAL_ASSIGNMENT_REQUIRED" 

Notify manager: "No bids for this order" 

Error: "No bids. Manager must assign manually" 

Sort bids from lowest bidAmount to highest (if tie, earlier timestamp first) 

Take lowestBid = first bid in sorted list 

Check if there is a manager override for this order 

If (manager override exists) 

chosenDeliveryPerson = override.deliveryPersonId 

assignmentType = "MANAGER_OVERRIDE" 

Else 

chosenDeliveryPerson = lowestBid.deliveryPersonId 

assignmentType = "AUTO_ASSIGN" 

Create a delivery assignment record: (orderId, chosenDeliveryPerson, assignmentType) 

Update order.status → "ASSIGNED_FOR_DELIVERY" 

Notify chosenDeliveryPerson: "You have been assigned to order #orderId" 

Return chosenDeliveryPerson 

4.4 AIEngine.answerQuestion(userId, questionText) 

Answer user questions via chat. First try the local knowledge base. If not found, use external LLM. 

Input: userId (can be guest), questionText 

Output: answerText shown to the user 

Pseudo-code: 

Save the question in chat log (for history and analytics) 

Search local Knowledge Base with questionText 

If (local KB has a good match) 

Get kbAnswer 

Display kbAnswer to user 

Ask user to rate the answer (1–5) 

If (rating not in [1,5])  

→ Error message: "Invalid rating" but answer is still shown 

Save rating in rating table 

If (rating is very low, e.g. 0 or 1) 

Flag this KB article for manager review 

Return kbAnswer 

Else (no local answer found) 

Send questionText to external LLM service 

Get llmAnswer 

Display llmAnswer to user 

Do NOT ask for rating (only log for analytics) 

Save that this answer came from LLM in chat log 

Return llmAnswer 

4.5 AIEngine.recommendMenu(userId, context) 

Recommend dishes to the user based on popularity and user’s history. 

Input: userId (optional), context (time of day, etc.) 

Output: list of recommended dishes 

Pseudo-code: 

Get all dishes that are currently available 

If (userId exists / user is logged in) 

Load past orders of this user 

Extract favorite tags or categories (e.g. spicy, vegan, dessert) 

Else 

favoriteTags = empty 

Get global popularity score for each dish (how many times it was ordered, rating, etc.) 

For each dish in available dishes: 

Start score = popularityScore[dish] 

If (dish.tags overlap with favoriteTags) → score += some bonus (e.g. +10) 

If (dish fits current time of day from context, e.g. breakfast item in morning) → score += timeOfDayBonus 

Sort all dishes by score from highest to lowest 

Take top N dishes (for example N = 5 or 10) as recommendation list 

Return the recommendation list 

 

4.6 ReputationService.recordEvent(userId, eventType, details) 

Record events that affect user reputation (for customers, chefs, and delivery staff) and update scores. 

Input: userId, eventType, details 

Output: none (but it updates reputation score and maybe the user’s status) 

Pseudo-code: 

Insert a new row into reputation log: (userId, eventType, details, timestamp) 

Use ReputationRuleEngine to compute scoreChange for this eventType 

Load current reputationScore for this user 

newScore = currentScore + scoreChange 

Save newScore back to database 

If (newScore >= VIP threshold) 

Update user.status → "VIP" 

If (newScore <= blacklist threshold) 

Update user.status → "BLACKLISTED" 

Notify security or manager: "User moved to blacklist" 

 

(Repeat for PaymentService.processPayment, DeliveryService.assignAgent, AIEngine.recommendMenu, etc.) 



