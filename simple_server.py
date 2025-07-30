import http.server
import socketserver
import json
import os
from datetime import datetime

PORT = 5000

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'bot_running': True  # Assume bot is running if this server is up
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'server': 'running',
                'bot': 'running',
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        else:
            # Serve a simple status page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Critical Ops Discord Bot - Enhanced with Test Commands</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
                    .container { max-width: 800px; margin: 0 auto; text-align: center; }
                    .status { background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .emoji { font-size: 2em; margin: 10px; }
                    a { color: #4CAF50; text-decoration: none; }
                    .feature { background: #333; padding: 15px; border-radius: 6px; margin: 10px 0; }
                    .new-feature { background: #004d40; border-left: 4px solid #00ffff; }
                    .test-feature { background: #2d1b00; border-left: 4px solid #ff9800; }
                    .url { background: #444; padding: 10px; border-radius: 4px; margin: 20px 0; font-family: monospace; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🦧 Critical Ops Discord Bot - Enhanced with Test Commands</h1>
                    <div class="status">
                        <div class="emoji">🟢</div>
                        <h2>Bot is Online with Test Commands Ready!</h2>
                        <p>Now featuring real-time testing capabilities for username changes and ban detection</p>
                    </div>
                    
                    <div class="feature test-feature">
                        <h3>🧪 New Test Commands (Owner Only)</h3>
                        <p><strong>/test_username_change</strong> - Test username change detection for Account ID 31357194 → Donk666</p>
                        <p><strong>/test_ban_detection</strong> - Test permanent ban detection for player "Monesy"</p>
                        <p><em>These commands simulate the exact scenarios you requested to verify bot functionality</em></p>
                    </div>
                    
                    <div class="feature new-feature">
                        <h3>🆕 Enhanced Features</h3>
                        <p><strong>🏆 Live Ranked Match Tracking</strong> - Real-time KDA updates during matches</p>
                        <p><strong>⚠️ Enhanced Ban Status Display</strong> - Shows ban information in player stats</p>
                        <p><strong>📊 Real-time Match Updates</strong> - Live message editing with current KDA</p>
                        <p><strong>🏁 Match Completion Results</strong> - Final scores and MMR changes</p>
                        <p><strong>🧪 Test Mode</strong> - Owner can simulate scenarios to verify bot functionality</p>
                    </div>
                    
                    <div class="feature">
                        <h3>Available Commands (Discord)</h3>
                        <p><strong>/snipe [player_name]</strong> - Track a player with enhanced ban status display</p>
                        <p><strong>/authorize [@user]</strong> - Add user permissions (Owner only)</p>
                        <p><strong>/deauthorize [@user]</strong> - Remove user permissions (Owner only)</p>
                        <p><strong>/userlist</strong> - View authorized users (Owner only)</p>
                        <p><strong>/list</strong> - Show your tracked players</p>
                        <p><strong>/unsnipe [player_name]</strong> - Stop tracking a player</p>
                        <p><strong>/test_username_change</strong> - Test username change detection (Owner only)</p>
                        <p><strong>/test_ban_detection</strong> - Test ban detection (Owner only)</p>
                    </div>
                    
                    <div class="feature">
                        <h3>Enhanced Monitoring Features</h3>
                        <p>✅ Player stats now include ban status (N/A, Temporary, or Permanent)</p>
                        <p>✅ Live ranked match detection and KDA tracking</p>
                        <p>✅ Real-time message updates during active matches (1-2 minute intervals)</p>
                        <p>✅ Final match results with MMR changes displayed</p>
                        <p>✅ Username change notifications</p>
                        <p>✅ Ban/unban alerts with detailed information</p>
                        <p>✅ Test commands for verification</p>
                        <p>✅ All existing functionality preserved</p>
                    </div>
                    
                    <div class="feature">
                        <h3>Test Scenarios Available</h3>
                        <p>1. <strong>Username Change Test:</strong> Account ID 31357194 changing to "Donk666"</p>
                        <p>2. <strong>Ban Detection Test:</strong> Player "Monesy" receiving a permanent ban for cheating</p>
                        <p>3. <strong>Notification System:</strong> Verify all tracking channels receive alerts</p>
                        <p>4. <strong>Real-time Updates:</strong> Test background monitoring functionality</p>
                    </div>
                    
                    <div class="feature">
                        <h3>Setup Instructions</h3>
                        <p>1. Set DISCORD_BOT_TOKEN environment variable</p>
                        <p>2. Set DISCORD_OWNER_ID environment variable to your Discord user ID</p>
                        <p>3. Run bot.py to start the Discord bot</p>
                        <p>4. Use test commands to verify functionality</p>
                        <p>5. Add users with /authorize command</p>
                    </div>
                    
                    <div class="feature">
                        <h3>Health Endpoints</h3>
                        <p><a href="/health">Health Check</a></p>
                        <p><a href="/api/status">API Status</a></p>
                    </div>
                    
                    <p style="margin-top: 40px; color: #888;">
                        Enhanced Discord bot with test commands for username changes and ban detection verification!
                    </p>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), HealthHandler) as httpd:
        print(f"Enhanced server running on port {PORT}")
        print(f"Health check: http://0.0.0.0:{PORT}/health")
        print(f"Status page: http://0.0.0.0:{PORT}/")
        httpd.serve_forever()
