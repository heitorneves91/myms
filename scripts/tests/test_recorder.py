import csv
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error

spec = importlib.util.spec_from_file_location('recorder', Path(__file__).parents[1] / 'record_temperatures.py')
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)

class RecorderTest(unittest.TestCase):
    def test_status_without_login_and_missing_values(self):
        authorization_headers = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                authorization_headers.append(self.headers.get('Authorization'))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'device_id': 'test', 'recording': {}, 'air_c': None, 'wall_c': 24, 'heater': False}).encode())
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f'http://127.0.0.1:{server.server_port}'
            row = recorder.row_for(recorder.fetch_status(url))
            self.assertIsNone(row['air_c'])
            self.assertEqual(row['wall_c'], 24)
            self.assertFalse(row['heater_command'])
            self.assertEqual(recorder.row_for(error='Disconnected')['connection_error'], 'Disconnected')
            with tempfile.TemporaryDirectory() as temp:
                output = Path(temp) / 'measurements.csv'
                command = [sys.executable, str(Path(recorder.__file__)), url,
                           '--interval', '1', '--duration', '2', '--output', str(output)]
                completed = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                with output.open() as file:
                    rows = list(csv.DictReader(file))
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]['device_id'], 'test')
                self.assertEqual(rows[0]['air_c'], '')
                self.assertEqual(rows[0]['wall_c'], '24')
                original = output.read_bytes()
                repeated = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
                self.assertNotEqual(repeated.returncode, 0)
                self.assertEqual(output.read_bytes(), original)
            self.assertTrue(authorization_headers)
            self.assertTrue(all(header is None for header in authorization_headers))
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
