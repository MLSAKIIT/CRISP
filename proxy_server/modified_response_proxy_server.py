import socket
import threading
import logging

# Setup logging for better traceability
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def modify_request(request):
    """Modify the request before forwarding it."""
    logging.debug("Modifying request...")
    # Example modification: Change User-Agent header
    modified_request = request.replace("User-Agent: Mozilla", "User-Agent: BurpClone")
    return modified_request

def modify_response(response):
    """Modify the response before sending it back to the client."""
    logging.debug("Modifying response...")
    # Example: Modify the response content
    if "origin" in response:
        response = response.replace("103.106.200.60", "127.0.0.1")  # Modify IP for testing purposes
    return response

def handle_client_request(client_socket):
    """Handles the client's request, modifying and forwarding it to the destination."""
    try:
        # Receiving the request
        request = b''
        client_socket.setblocking(False)

        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                request += data
                logging.debug(f"Received data: {data.decode('utf-8', errors='ignore')}")
            except BlockingIOError:
                break

        # Modify the request
        modified_request = modify_request(request.decode('utf-8'))
        host, port = extract_host_port_from_request(modified_request)

        # Forwarding the modified request to the destination server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as destination_socket:
            destination_socket.connect((host, port))
            destination_socket.sendall(modified_request.encode('utf-8'))
            logging.debug("Request forwarded to the destination")

            # Receive the response from the destination server
            response = b""
            while True:
                data = destination_socket.recv(1024)
                if not data:
                    break
                response += data
            # Modify the response before sending it back to the client
            modified_response = modify_response(response.decode('utf-8'))
            client_socket.sendall(modified_response.encode('utf-8'))

        logging.debug("Response sent back to the client")

    except Exception as e:
        logging.error(f"Error handling request: {e}")
    finally:
        client_socket.close()

def extract_host_port_from_request(request):
    """Extract the host and port from the HTTP request."""
    host_string_start = request.find('Host: ') + len('Host: ')
    host_string_end = request.find('\r\n', host_string_start)
    host_string = request[host_string_start:host_string_end]
    port = 80
    if ':' in host_string:
        host, port = host_string.split(':')
        port = int(port)
    else:
        host = host_string
    return host, port

def start_proxy_server(port=8080):
    """Start the proxy server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', port))
    server.listen(5)
    logging.info(f"Proxy server running on port {port}")

    try:
        while True:
            client_socket, client_address = server.accept()
            logging.info(f"Accepted connection from {client_address}")
            client_handler = threading.Thread(target=handle_client_request, args=(client_socket,))
            client_handler.start()
    except KeyboardInterrupt:
        logging.info("Shutting down the proxy server...")
    finally:
        server.close()

if __name__ == "__main__":
    start_proxy_server()
