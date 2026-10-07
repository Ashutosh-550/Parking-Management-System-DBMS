

CREATE DATABASE IF NOT EXISTS parking_management_system;
USE parking_management_system;

CREATE TABLE IF NOT EXISTS admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

INSERT IGNORE INTO admin (username, password) VALUES ('admin2', 'admin123');

CREATE TABLE IF NOT EXISTS parking_slot (
    slot_id VARCHAR(10) PRIMARY KEY,
    floor INT NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL,
    status ENUM('Available', 'Occupied') DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS parking_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(50) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    slot_number VARCHAR(20),
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Parked'
);

INSERT IGNORE INTO parking_slot (slot_id, floor, vehicle_type, status) VALUES 
('S-101', 1, 'Car', 'Available'),
('S-102', 1, 'Bike', 'Available'),
('S-103', 1, 'Car', 'Occupied'),
('S-104', 1, 'Bike', 'Occupied'),
('S-105', 2, 'Truck', 'Available'),
('S-106', 2, 'Car', 'Available'),
('S-107', 2, 'Bike', 'Available'),
('S-108', 2, 'Car', 'Available'),
('S-109', 1, 'Truck', 'Available'),
('S-110', 1, 'Car', 'Available'),
('S-111', 2, 'Bike', 'Available'),
('S-112', 1, 'Car', 'Available'),
('S-113', 1, 'Truck', 'Available'),
('S-114', 2, 'Bike', 'Available'),
('S-115', 2, 'Truck', 'Available');

CREATE TABLE IF NOT EXISTS vehicle (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(20) NOT NULL UNIQUE,
    vehicle_type VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS parking_request (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT,
    slot_id VARCHAR(10),
    entry_datetime DATETIME NOT NULL,
    exit_datetime DATETIME NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(vehicle_id) ON DELETE CASCADE,
    FOREIGN KEY (slot_id) REFERENCES parking_slot(slot_id) ON DELETE CASCADE
);

INSERT IGNORE INTO vehicle (vehicle_id, vehicle_number, vehicle_type) VALUES 
(1, 'DL-01-AB-1234', 'Car'),
(2, 'MH-12-AB-5678', 'Bike'),
(3, 'KA-05-XY-9876', 'Car');

INSERT IGNORE INTO parking_request (request_id, vehicle_id, slot_id, entry_datetime, exit_datetime, status) VALUES 
(1, 1, 'S-101', '2026-09-08 10:00:00', '2026-09-08 14:00:00', 'Approved'),
(2, 2, 'S-102', '2026-09-08 11:30:00', '2026-09-08 17:30:00', 'Pending'),
(3, 3, 'S-105', '2026-09-08 10:30:00', '2026-09-08 15:00:00', 'Rejected');