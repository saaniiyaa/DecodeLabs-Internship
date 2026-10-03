-- Query 1: Product Performance Analysis
SELECT 
    Product,
    COUNT(OrderID) AS total_orders,
    SUM(Quantity) AS total_quantity_sold,
    ROUND(SUM(TotalPrice), 2) AS total_revenue,
    ROUND(AVG(TotalPrice), 2) AS avg_order_value
FROM orders
GROUP BY Product
ORDER BY total_revenue DESC;

-- Query 2: Valid Payment Methods Analysis (Excluding Cancelled)
SELECT 
    PaymentMethod,
    COUNT(OrderID) AS valid_orders,
    ROUND(SUM(TotalPrice), 2) AS total_revenue,
    ROUND(AVG(UnitPrice), 2) AS avg_unit_price
FROM orders
WHERE OrderStatus != 'Cancelled'
GROUP BY PaymentMethod
ORDER BY total_revenue DESC;

-- Query 3: High-Value Referral Channels (Threshold > 200,000)
SELECT 
    ReferralSource,
    COUNT(OrderID) AS total_orders,
    ROUND(SUM(TotalPrice), 2) AS total_revenue,
    ROUND(AVG(TotalPrice), 2) AS avg_revenue_per_order
FROM orders
GROUP BY ReferralSource
HAVING total_revenue > 200000
ORDER BY total_revenue DESC;