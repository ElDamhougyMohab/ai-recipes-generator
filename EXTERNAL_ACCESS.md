# External Access Setup Guide

## 🌐 How to Allow External Users to Access Your App

### Option 1: Local Network Access (Same WiFi/Network)

#### Step 1: Find Your IP Address
```cmd
ipconfig
```
Look for "IPv4 Address" (usually starts with 192.168.x.x or 10.x.x.x)

#### Step 2: Configure Windows Firewall
1. Open **Windows Security** → **Firewall & network protection**
2. Click **Allow an app through firewall**
3. Click **Change settings** → **Allow another app**
4. Browse and add:
   - `python.exe` (from your virtual environment)
   - `node.exe` (from C:\Program Files\nodejs\)
5. **OR** create firewall rules for ports 3000 and 8000:
   ```cmd
   netsh advfirewall firewall add rule name="React Dev Server" dir=in action=allow protocol=TCP localport=3000
   netsh advfirewall firewall add rule name="FastAPI Server" dir=in action=allow protocol=TCP localport=8000
   ```

#### Step 3: Start the Servers for External Access
- Run `start_external.bat` or `start_external.ps1`
- Share your IP address with users

#### Step 4: External Users Access URLs
- **Frontend**: `http://YOUR_IP:3000`
- **Backend API**: `http://YOUR_IP:8000`
- **API Documentation**: `http://YOUR_IP:8000/docs`

---

### Option 2: Internet Access (Port Forwarding)

#### Step 1: Configure Router Port Forwarding
1. Access your router's admin panel (usually http://192.168.1.1 or http://192.168.0.1)
2. Find **Port Forwarding** or **Virtual Server** settings
3. Forward these ports to your computer's IP:
   - External Port 3000 → Internal Port 3000 (React)
   - External Port 8000 → Internal Port 8000 (FastAPI)

#### Step 2: Find Your Public IP
```cmd
curl ipinfo.io/ip
```
Or visit: https://whatismyipaddress.com/

#### Step 3: Share Public URLs
- **Frontend**: `http://YOUR_PUBLIC_IP:3000`
- **Backend**: `http://YOUR_PUBLIC_IP:8000`

---

### Option 3: Cloud Deployment (Recommended for Production)

#### Using Railway (Easy)
1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Deploy backend and frontend separately

#### Using Vercel + Railway
- **Frontend**: Deploy to Vercel
- **Backend**: Deploy to Railway
- Update environment variables accordingly

#### Using AWS/Azure/GCP
- Deploy using container services
- Use Docker Compose for easy deployment

---

### Option 4: Tunneling Services (Quick Testing)

#### Using ngrok (Free for testing)
1. Download ngrok: https://ngrok.com/
2. Start your servers locally
3. Create tunnels:
   ```cmd
   ngrok http 3000  # For frontend
   ngrok http 8000  # For backend
   ```
4. Share the ngrok URLs

#### Using Cloudflare Tunnel
1. Install cloudflared
2. Create tunnels for both services
3. Share the Cloudflare URLs

---

## 🔧 Configuration Files Created

- `start_external.bat` - Windows batch script for external access
- `start_external.ps1` - PowerShell script for external access
- `frontend/.env.local` - Local development config
- `frontend/.env.production` - Production config

## 🛡️ Security Considerations

1. **Firewall**: Only open necessary ports
2. **Environment Variables**: Keep API keys secure
3. **HTTPS**: Use SSL certificates for production
4. **Authentication**: Add user authentication for sensitive data
5. **Rate Limiting**: Implement API rate limiting

## 📱 Testing External Access

1. Start servers with external access scripts
2. Test on another device on the same network
3. Try accessing: `http://YOUR_IP:3000`
4. Verify API works: `http://YOUR_IP:8000/docs`

## 🚨 Troubleshooting

- **Can't connect**: Check firewall settings
- **API errors**: Verify backend is running on 0.0.0.0
- **CORS issues**: Check CORS settings in backend
- **Mobile issues**: Ensure mobile device is on same network
