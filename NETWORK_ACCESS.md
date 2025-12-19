# Network Access Setup - IR-bot Playbook Management System

The servers are now configured to be accessible from other machines on your network.

## Starting the Servers

### Backend (Python/FastAPI)

**Windows:**
```bash
cd backend
start_server.bat
```

**Linux/Mac:**
```bash
cd backend
./start_server.sh
```

**Or manually:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be accessible at:
- Local: `http://localhost:8000`
- Network: `http://YOUR_IP:8000`

### Frontend (React/Vite)

```bash
cd frontend
npm run dev
```

The frontend will be accessible at:
- Local: `http://localhost:3000`
- Network: `http://YOUR_IP:3000`

Vite will display your network addresses when it starts:

```
  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.1.100:3000/
```

## Finding Your IP Address

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" under your active network adapter.

**Linux/Mac:**
```bash
ifconfig
# or
ip addr show
```

## Firewall Configuration

If others can't access the servers, you may need to allow the ports through your firewall:

**Windows Firewall:**
```bash
# Allow port 8000 (Backend)
netsh advfirewall firewall add rule name="IR-bot Backend" dir=in action=allow protocol=TCP localport=8000

# Allow port 3000 (Frontend)
netsh advfirewall firewall add rule name="IR-bot Frontend" dir=in action=allow protocol=TCP localport=3000
```

**Linux (ufw):**
```bash
sudo ufw allow 8000/tcp
sudo ufw allow 3000/tcp
```

## Accessing from Other Machines

Once both servers are running, other machines on your network can access:

**Frontend UI:**
```
http://YOUR_IP:3000
```

Replace `YOUR_IP` with your machine's IP address (e.g., `http://192.168.1.100:3000`)

## Important Security Notes

⚠️ **This is a prototype configuration - NOT production ready:**

1. **No Authentication** - Anyone with network access can view/modify incidents
2. **No Encryption** - All traffic is unencrypted (HTTP)
3. **No Authorization** - No access controls or user management
4. **In-Memory Storage** - All data lost when server restarts
5. **No Input Validation** - Limited security checks on data

**Recommendations:**
- Only use on trusted networks (not public WiFi)
- Consider this demo/prototype only
- For production, implement proper authentication and HTTPS

## Testing Network Access

From another machine on your network:

1. **Check Backend:**
   ```bash
   curl http://YOUR_IP:8000/api/playbooks
   ```

2. **Open Frontend:**
   Open browser to `http://YOUR_IP:3000`

## Troubleshooting

**"Cannot access from other machines":**
- Check firewall settings
- Verify both machines are on same network
- Try pinging your machine: `ping YOUR_IP`
- Check if server is running: `netstat -an | findstr 8000`

**"API calls failing":**
- The frontend proxy is configured for localhost backend
- If backend is on different machine, update `frontend/vite.config.ts` proxy target

**"Connection refused":**
- Ensure servers are running with `--host 0.0.0.0`
- Check antivirus isn't blocking connections
