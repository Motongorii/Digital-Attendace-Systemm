# QR CODE SCANNING FIX - SITE NOT FOUND ERROR

## Problem
When scanning the QR code with a mobile device, you get "Site not found" error.

## Root Cause
The QR code contains `http://127.0.0.1:8000/attend/{session_id}/`
But 127.0.0.1 only works on the SAME computer, not on other devices.

## Solution: Use Your Computer's IP Address

### Step 1: Find Your Computer's IP Address
Open PowerShell and run:
```powershell
ipconfig
```

Look for "IPv4 Address" under your network adapter (usually something like `192.168.x.x` or `10.x.x.x`)

Example output:
```
Ethernet adapter Ethernet:
   IPv4 Address. . . . . . . . . . : 192.168.1.100
   Subnet Mask . . . . . . . . . . : 255.255.255.0
```

### Step 2: Stop the Current Server
Press `CTRL+BREAK` in the terminal running Django server

### Step 3: Restart Server with Your IP Address
Replace `192.168.1.100` with YOUR actual IP:

```powershell
cd "c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main"
.\venv\Scripts\python.exe manage.py runserver 192.168.1.100:8000
```

Or to make it accessible on all network interfaces:
```powershell
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

### Step 4: Create New Attendance Session
1. Go to http://192.168.1.100:8000/ (or YOUR IP)
2. Login as admin (admin / Admin@123456)
3. Create a new unit and attendance session
4. The QR code will now contain your IP address

### Step 5: Scan QR Code from Mobile
1. On your mobile device, make sure it's on the SAME WiFi network as your computer
2. Scan the QR code
3. You should now see:
   - Session information (Unit, Lecturer, Date, Time, Venue)
   - Student Name input field
   - Admission Number input field
   - Mark Attendance button/checkbox
   - Submit button

### Step 6: Fill Form and Submit
1. Enter student name
2. Enter admission number
3. Check the checkbox to confirm
4. Click Submit
5. You should see a success message and attendance is saved to Firebase

## Quick Reference

| Device | URL |
|--------|-----|
| Same Computer | http://127.0.0.1:8000/ |
| Mobile on Same WiFi | http://192.168.1.100:8000/ (use YOUR IP) |
| Admin Panel | http://192.168.1.100:8000/admin/ |
| Login | http://192.168.1.100:8000/login/ |
| Dashboard | http://192.168.1.100:8000/dashboard/ |

## Test the Route Manually (before scanning QR)
If you don't have a QR scanner, you can test manually by visiting:
```
http://192.168.1.100:8000/attend/{any-session-uuid}/
```

You should see the student attendance form.

## If Still Not Working

1. Check firewall - port 8000 might be blocked
2. Ensure mobile is on same network (not guest WiFi)
3. Check router - it might have isolated networks
4. Try using computer's hostname instead of IP:
   ```
   http://computer-name.local:8000/
   ```

