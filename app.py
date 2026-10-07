from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
import math
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get('MYSQL_PASSWORD'),
        database="parking_management_system"
    )

# 1. Main Dashboard
@app.route('/')
@app.route('/login.html')
def home():
    return render_template('login.html')

# 2. Park Vehicle Form Route
@app.route('/user-enter.html', methods=['GET', 'POST'])
def park_vehicle():
    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']
        vehicle_type = request.form['vehicle_type']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO vehicle (vehicle_number, vehicle_type) VALUES (%s, %s)", (vehicle_number, vehicle_type))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect('/parking-request.html')
    return render_template('user-enter.html')

# 3. Parking Status & Slot Selection Route
@app.route('/parking-request.html', methods=['GET', 'POST'])
def parking_status():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        if 'entry_date' in request.form:
            entry_datetime = f"{request.form['entry_date']} {request.form['entry_time']}:00"
            exit_datetime = f"{request.form['exit_date']} {request.form['exit_time']}:00"
            slot_id = request.form['parking_space']
            
            cursor.execute("SELECT vehicle_id FROM vehicle ORDER BY vehicle_id DESC LIMIT 1")
            vehicle = cursor.fetchone()
            
            if vehicle:
                vehicle_id = vehicle['vehicle_id']
                cursor.execute("""
                    INSERT INTO parking_request (vehicle_id, slot_id, entry_datetime, exit_datetime, status) 
                    VALUES (%s, %s, %s, %s, 'Pending')
                """, (vehicle_id, slot_id, entry_datetime, exit_datetime))
                conn.commit()
                
            cursor.close()
            conn.close()
            return redirect('/ticket-status.html')
            
        else:
            vehicle_number = request.form.get('vehicle_number')
            vehicle_type = request.form.get('vehicle_type')
            
            if vehicle_number and vehicle_type:
                cursor.execute("""
                    INSERT INTO vehicle (vehicle_number, vehicle_type) 
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE vehicle_type = VALUES(vehicle_type)
                """, (vehicle_number, vehicle_type))
                conn.commit()

    cursor.execute("SELECT * FROM parking_slot WHERE status = 'Available'")
    available_slots = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('parking-request.html', available_slots=available_slots)


# 5. Admin Login Route
@app.route('/admin-enter.html', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if admin:
            return redirect('/admin-dashboard.html')
        else:
            return "Invalid Credentials! <a href='/admin-enter.html'>Try Again</a>"
            
    return render_template('admin-enter.html')

# 6. Admin Dashboard Route
@app.route('/admin-dashboard.html', methods=['GET', 'POST'])
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT pr.request_id, v.vehicle_number, v.vehicle_type, pr.entry_datetime, pr.exit_datetime, pr.slot_id 
        FROM parking_request pr 
        JOIN vehicle v ON pr.vehicle_id = v.vehicle_id 
        WHERE pr.status = 'Pending'
    """)
    pending_requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('admin-dashboard.html', pending_requests=pending_requests)

# Route to handle Approve / Reject actions
@app.route('/update-request/<int:request_id>/<action>')
def update_request(request_id, action):
    new_status = 'Approved' if action == 'approve' else 'Rejected'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE parking_request SET status = %s WHERE request_id = %s", (new_status, request_id))
    
    if new_status == 'Approved':
        cursor.execute("UPDATE parking_slot SET status = 'Occupied' WHERE slot_id = (SELECT slot_id FROM parking_request WHERE request_id = %s)", (request_id,))
        
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect('/admin-dashboard.html')

@app.route('/ticket-status.html', methods=['GET'])
def ticket_status_view():
    search_vehicle = request.args.get('search_vehicle')
    requests_list = []
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if search_vehicle:
        cursor.execute("""
            SELECT pr.request_id, v.vehicle_number, pr.slot_id, pr.status
            FROM parking_request pr
            JOIN vehicle v ON pr.vehicle_id = v.vehicle_id
            WHERE v.vehicle_number = %s
        """, (search_vehicle,))
        requests_list = cursor.fetchall()
        
    cursor.close()
    conn.close()
    
    return render_template('ticket-status.html', requests_list=requests_list)

# Route to render the scanning page
@app.route('/admin/scan', methods=['GET'])
def admin_scan_page():
    return render_template('admin_scan.html')

# Route to handle form submission from the scanner
@app.route('/admin/scan-entry', methods=['POST'])
def admin_scan_entry():
    vehicle_number = request.form.get('vehicle_number')
    vehicle_type = request.form.get('vehicle_type')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Insert or update vehicle in database
    cursor.execute("""
        INSERT INTO vehicle (vehicle_number, vehicle_type) 
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE vehicle_type = VALUES(vehicle_type)
    """, (vehicle_number, vehicle_type))
    conn.commit()
    
    # Get vehicle ID
    cursor.execute("SELECT vehicle_id FROM vehicle WHERE vehicle_number = %s", (vehicle_number,))
    vehicle = cursor.fetchone()
    vehicle_id = vehicle['vehicle_id'] if vehicle else None
    
    # Auto-assign an available slot (matching vehicle type first, then any available)
    cursor.execute("SELECT slot_id FROM parking_slot WHERE status = 'Available' AND vehicle_type = %s LIMIT 1", (vehicle_type,))
    slot = cursor.fetchone()
    if not slot:
        cursor.execute("SELECT slot_id FROM parking_slot WHERE status = 'Available' LIMIT 1")
        slot = cursor.fetchone()
    
    slot_number = slot['slot_id'] if slot else "Unassigned"
    
    entry_now = datetime.now()
    entry_time_str = entry_now.strftime("%Y-%m-%d %H:%M:%S")
    ticket_id = None
    
    if slot and vehicle_id:
        cursor.execute("UPDATE parking_slot SET status = 'Occupied' WHERE slot_id = %s", (slot_number,))
        try:
            cursor.execute("""
                INSERT INTO parking_request (vehicle_id, slot_id, entry_datetime, status) 
                VALUES (%s, %s, %s, 'Approved')
            """, (vehicle_id, slot_number, entry_time_str))
        except mysql.connector.Error as err:
            if "exit_datetime" in str(err):
                cursor.execute("""
                    INSERT INTO parking_request (vehicle_id, slot_id, entry_datetime, exit_datetime, status) 
                    VALUES (%s, %s, %s, %s, 'Approved')
                """, (vehicle_id, slot_number, entry_time_str, entry_time_str))
            else:
                raise err
        conn.commit()
        ticket_id = cursor.lastrowid
        
    cursor.close()
    conn.close()

    return render_template('parking_slip.html', 
                           ticket_id=ticket_id,
                           vehicle_number=vehicle_number, 
                           vehicle_type=vehicle_type, 
                           slot_number=slot_number,
                           entry_time=entry_time_str)

# 7. Vehicle Exit & Fee Calculation Routes
@app.route('/admin/exit', methods=['GET', 'POST'])
@app.route('/admin_exit.html', methods=['GET', 'POST'])
def admin_exit():
    parking = None
    fee = 0
    duration = 0
    
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        
        if search_query:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Find active approved parking session by vehicle number or slot ID
            cursor.execute("""
                SELECT pr.request_id, pr.slot_id, pr.entry_datetime,
                       v.vehicle_number, v.vehicle_type
                FROM parking_request pr
                JOIN vehicle v ON pr.vehicle_id = v.vehicle_id
                WHERE pr.status = 'Approved'
                  AND (LOWER(TRIM(v.vehicle_number)) = LOWER(%s) OR LOWER(TRIM(pr.slot_id)) = LOWER(%s))
                ORDER BY pr.request_id DESC
                LIMIT 1
            """, (search_query, search_query))
            
            parking = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if parking:
                entry_dt = parking.get('entry_datetime')
                # Parse entry_datetime if string
                if isinstance(entry_dt, str):
                    try:
                        entry_dt = datetime.strptime(entry_dt, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            entry_dt = datetime.strptime(entry_dt[:19], "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            entry_dt = datetime.now()
                elif not isinstance(entry_dt, datetime):
                    entry_dt = datetime.now()
                
                # Calculate parked duration
                now = datetime.now()
                total_seconds = max((now - entry_dt).total_seconds(), 0)
                duration_hours = max(1.0, round(total_seconds / 3600.0, 1))
                duration = int(duration_hours) if duration_hours.is_integer() else duration_hours
                
                # Hourly rates by vehicle type (in Rs.)
                vehicle_type = str(parking.get('vehicle_type', '')).strip().lower()
                rate_chart = {
                    'bike': 20,
                    'car': 40,
                    'truck': 80
                }
                rate = rate_chart.get(vehicle_type, 40)
                
                # Calculate total fee (minimum 1 hour billing)
                billed_hours = max(1, math.ceil(total_seconds / 3600.0))
                fee = billed_hours * rate
                
    return render_template('admin_exit.html', parking=parking, duration=duration, fee=fee)


# 8. Process Exit & Free Parking Slot
@app.route('/admin/process-exit/<int:request_id>', methods=['POST'])
def admin_process_exit(request_id):
    exit_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Fetch current parking record to identify slot
    cursor.execute("SELECT slot_id FROM parking_request WHERE request_id = %s", (request_id,))
    record = cursor.fetchone()
    
    if record:
        slot_id = record['slot_id']
        
        # 2. Update parking_request status to Completed and record exit timestamp
        cursor.execute("""
            UPDATE parking_request 
            SET status = 'Completed', exit_datetime = %s 
            WHERE request_id = %s
        """, (exit_now, request_id))
        
        # 3. Free the parking slot in parking_slot table
        if slot_id:
            cursor.execute("UPDATE parking_slot SET status = 'Available' WHERE slot_id = %s", (slot_id,))
        
        conn.commit()
        
    cursor.close()
    conn.close()
    
    return redirect('/admin-dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)