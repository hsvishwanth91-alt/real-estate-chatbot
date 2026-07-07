-- =====================================================
-- AI Real Estate Chatbot - Database Setup Script
-- =====================================================
-- Run this file in MySQL to create the database,
-- tables, and load sample property data.
--
-- Usage (from MySQL command line):
--   mysql -u root -p < database.sql
-- =====================================================

DROP DATABASE IF EXISTS real_estate_db;
CREATE DATABASE real_estate_db;
USE real_estate_db;

-- ---------------------------------------------------
-- Table: properties
-- Stores all property listings
-- ---------------------------------------------------
CREATE TABLE properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    property_type VARCHAR(50) NOT NULL,      -- Apartment, Villa, Plot, Independent House
    location VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    price DECIMAL(12, 2) NOT NULL,           -- price in INR
    bedrooms INT DEFAULT 0,
    bathrooms INT DEFAULT 0,
    area_sqft INT DEFAULT 0,
    description TEXT,
    image_url VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Available',  -- Available, Sold
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------
-- Table: bookings
-- Stores site visit booking requests
-- ---------------------------------------------------
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    visit_date DATE NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE SET NULL
);

-- ---------------------------------------------------
-- Table: chat_logs (optional - stores chatbot Q&A history)
-- ---------------------------------------------------
CREATE TABLE chat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_message TEXT,
    bot_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------
-- Sample Property Data
-- ---------------------------------------------------
INSERT INTO properties
(title, property_type, location, city, price, bedrooms, bathrooms, area_sqft, description, image_url, status)
VALUES
('Sunrise 3BHK Apartment', 'Apartment', 'Whitefield', 'Bangalore', 7500000, 3, 2, 1450,
 'A modern 3BHK apartment with clubhouse, gym, and swimming pool access. Close to IT parks and schools.',
 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2', 'Available'),

('Green Valley Villa', 'Villa', 'Sarjapur Road', 'Bangalore', 15000000, 4, 4, 3200,
 'Spacious 4BHK independent villa with private garden and parking for 2 cars. Gated community with 24/7 security.',
 'https://images.unsplash.com/photo-1568605114967-8130f3a36994', 'Available'),

('Cozy 2BHK Flat', 'Apartment', 'Andheri West', 'Mumbai', 9500000, 2, 2, 1050,
 'Well-ventilated 2BHK flat near the railway station, ideal for small families and working professionals.',
 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688', 'Available'),

('Skyline Penthouse', 'Apartment', 'Bandra', 'Mumbai', 32000000, 4, 3, 2800,
 'Luxury penthouse with sea view, private terrace, and premium interiors in the heart of the city.',
 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750', 'Available'),

('Budget 1BHK Studio', 'Apartment', 'Hinjewadi', 'Pune', 3200000, 1, 1, 550,
 'Affordable studio apartment close to IT hubs, perfect for bachelors and young professionals.',
 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267', 'Available'),

('Riverside Independent House', 'Independent House', 'Kothrud', 'Pune', 11000000, 3, 3, 1800,
 'Independent house with a small backyard, located in a peaceful residential neighborhood.',
 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c', 'Available'),

('Emerald Farmland Plot', 'Plot', 'Devanahalli', 'Bangalore', 4500000, 0, 0, 2400,
 'Residential plot near the airport, approved layout with clear title and ready for construction.',
 'https://images.unsplash.com/photo-1500382017468-9049fed747ef', 'Available'),

('Lakeview 3BHK Apartment', 'Apartment', 'Powai', 'Mumbai', 18500000, 3, 3, 1600,
 'Premium apartment overlooking Powai lake with modern amenities and a dedicated kids play area.',
 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914', 'Available'),

('Elegant 2BHK Apartment', 'Apartment', 'Anna Nagar', 'Chennai', 6800000, 2, 2, 1100,
 'Centrally located 2BHK apartment close to schools, hospitals, and shopping malls.',
 'https://images.unsplash.com/photo-1493809842364-78817add7ffb', 'Available'),

('Palm Grove Villa', 'Villa', 'ECR', 'Chennai', 21000000, 5, 5, 4000,
 'Beachside luxury villa with private pool, landscaped garden, and 5 spacious bedrooms.',
 'https://images.unsplash.com/photo-1613977257363-707ba9348227', 'Available'),

('Metro Heights 2BHK', 'Apartment', 'Dwarka', 'Delhi', 8200000, 2, 2, 1200,
 'Well-connected apartment near the metro station, ideal for families and professionals.',
 'https://images.unsplash.com/photo-1524758631624-e2822e304c36', 'Available'),

('Royal Enclave Villa', 'Villa', 'Vasant Kunj', 'Delhi', 27500000, 4, 4, 3500,
 'Premium villa in an upscale neighborhood with modern architecture and landscaped lawns.',
 'https://images.unsplash.com/photo-1613490493576-7fde63acd811', 'Available');
