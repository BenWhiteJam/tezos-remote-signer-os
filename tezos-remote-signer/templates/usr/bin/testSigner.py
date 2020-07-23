#!/usr/bin/python3
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import requests
import subprocess
import sys
PORT = 5732
SIGNER_CHECK_ARGS = ["/home/tezos/tezos/tezos-signer", "get", "ledger", "authorized", "path", "for" ]
class LedgerHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query_components = parse_qs(urlparse(self.path).query)
            ledger_url = query_components["ledger_url"]
            ledger_response = subprocess.run(SIGNER_CHECK_ARGS + ledger_url, capture_output=True)
            public_baking_key = query_components["public_baking_key"][0]
            signer_response = requests.get('http://localhost:8443/keys/%s' % public_baking_key)
            if ledger_response.returncode == 0 and signer_response:
                self.send_response(200)
            else:
                self.send_response(500)
            self.send_header("Content-type", "plain")
            self.end_headers()
            try:
                self.wfile.write(ledger_response.stdout)
                self.wfile.write(ledger_response.stderr)
                self.wfile.write(signer_response.content)
            except ConnectionError:
                pass
        except Exception as e:
            self.send_error(501, message=str(e))
if __name__ == '__main__':
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, LedgerHTTPHandler)
    print("Signer status listening at port", PORT)
    httpd.serve_forever()
