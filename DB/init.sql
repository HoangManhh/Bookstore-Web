CREATE DATABASE IF NOT EXISTS `bookstore_db`
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Sử dụng CSDL vừa tạo
USE `bookstore_db`;
-- ------------------------------------------------------------------
-- Bảng 1: Users (Người dùng)
-- ------------------------------------------------------------------
CREATE TABLE Users (
    id CHAR(36) PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,   
    address TEXT,
    phone_number VARCHAR(20),
    role ENUM('customer', 'admin') NOT NULL DEFAULT 'customer',
    status ENUM('active', 'banned') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------
-- Bảng 2: Authors (Tác giả)
-- ------------------------------------------------------------------
CREATE TABLE Authors (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    year_of_birth DATE,              
    year_of_death DATE,
    hometown VARCHAR(255),            
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------
-- Bảng 3: Publishers (Nhà xuất bản)
-- ------------------------------------------------------------------
CREATE TABLE Publishers (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT, -- Địa chỉ nhà xuất bản
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------
-- Bảng 4: Categories (Danh mục)
-- ------------------------------------------------------------------
CREATE TABLE Categories (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- ------------------------------------------------------------------
-- Bảng 5: Products (Sản phẩm - Sách)
-- ------------------------------------------------------------------
CREATE TABLE Products (
    id CHAR(36) PRIMARY KEY,
    category_id CHAR(36),            
    author_id CHAR(36),               
    publisher_id CHAR(36),           
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0, 
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Tạo liên kết khóa ngoại
    FOREIGN KEY (category_id) REFERENCES Categories(id) 
        ON DELETE SET NULL,
    FOREIGN KEY (author_id) REFERENCES Authors(id)
        ON DELETE SET NULL, -- Nếu xóa tác giả, sách vẫn còn (chỉ mất liên kết)
    FOREIGN KEY (publisher_id) REFERENCES Publishers(id)
        ON DELETE SET NULL  -- Nếu xóa NXB, sách vẫn còn
);

-- ------------------------------------------------------------------
-- Bảng 6: Orders (Đơn hàng)
-- ------------------------------------------------------------------
CREATE TABLE Orders (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    shipping_address TEXT NOT NULL,
    shipping_phone VARCHAR(20),
    payment_method VARCHAR(50) NOT NULL,

    FOREIGN KEY (user_id) REFERENCES Users(id) 
        ON DELETE RESTRICT
);

-- ------------------------------------------------------------------
-- Bảng 7: OrderItems (Chi tiết Đơn hàng)
-- ------------------------------------------------------------------
CREATE TABLE OrderItems (
    id CHAR(36) PRIMARY KEY,
    order_id CHAR(36) NOT NULL,
    product_id CHAR(36),
    quantity INT NOT NULL,
    price_at_purchase DECIMAL(10, 2) NOT NULL, 

    FOREIGN KEY (order_id) REFERENCES Orders(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products(id) 
        ON DELETE SET NULL
);

-- ------------------------------------------------------------------
-- Bảng 8: Comments (Bình luận)
-- ------------------------------------------------------------------
CREATE TABLE Comments (
    id CHAR(36) PRIMARY KEY,
    product_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES Products(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) 
        ON DELETE CASCADE
);
