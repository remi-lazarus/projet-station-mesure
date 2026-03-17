#!/usr/bin/env python3
"""
Simple Python webserver that listens on 0.0.0.0:8000 and returns a JSON response.
Run with: python3 main.py
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket
import os

HOST = '0.0.0.0'
PORT = 8000

data_file = 'temperature_data.json'

def save_temperature(temperature):
    data = []
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    data.append({'temperature': temperature})
    # Keep only the last 1000 entries
    if len(data) > 1000:
        data = data[-1000:]
    with open(data_file, 'w') as f:
        json.dump(data, f)

class Handler(BaseHTTPRequestHandler):
    def _set_json_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            self._set_json_headers()
            payload = {'status': 'ok', 'message': 'Hello from temperature_lorraine_app'}
            self.wfile.write(json.dumps(payload).encode('utf-8'))
        elif self.path == '/last-temperature':
            temperature = None
            timestamp = None
            if os.path.exists(data_file):
                try:
                    with open(data_file, 'r') as f:
                        data = json.load(f)
                        if data:
                            last_entry = data[-1]
                            temperature = last_entry.get('temperature')
                            # Add timestamp if available, else use current time
                            timestamp = last_entry.get('timestamp') if 'timestamp' in last_entry else None
                except Exception:
                    pass
            self._set_json_headers()
            self.wfile.write(json.dumps({
                'temperature': temperature,
                'timestamp': timestamp
            }).encode('utf-8'))
        elif self.path == '/last-temperatures':
            temperatures = []
            if os.path.exists(data_file):
                try:
                    with open(data_file, 'r') as f:
                        data = json.load(f)
                        temperatures = data[-50:] if len(data) > 0 else []
                except Exception:
                    pass
            self._set_json_headers()
            self.wfile.write(json.dumps({'temperatures': temperatures}).encode('utf-8'))
        elif self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self._set_json_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode('utf-8'))

    def do_POST(self):
        if self.path == '/temperature':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data)
                temperature = payload.get('temperature')
                if temperature is not None:
                    save_temperature(temperature)
                    self._set_json_headers(201)
                    self.wfile.write(json.dumps({'status': 'ok', 'message': 'Temperature stored'}).encode('utf-8'))
                else:
                    self._set_json_headers(400)
                    self.wfile.write(json.dumps({'error': 'Missing temperature'}).encode('utf-8'))
            except Exception as e:
                self._set_json_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid JSON', 'details': str(e)}).encode('utf-8'))
        else:
            self._set_json_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode('utf-8'))

    def log_message(self, format, *args):
        # Override to reduce console noise; remove to enable access logs
        return

if __name__ == '__main__':
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, Handler)
    hostname = socket.gethostname()
    print(f'Serving HTTP on {HOST} port {PORT} (http://{hostname}:{PORT}/) ...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server')
        httpd.server_close()
