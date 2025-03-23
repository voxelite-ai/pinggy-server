# pinggy-server

## Overview
`pinggy-server` is a FastAPI-based application designed to manage SSH tunnels using Pinggy. It provides a programmatic interface to create and manage tunnels efficiently.

## Features
- Create and configure SSH tunnels
- Monitor and manage tunnel status
- Easy setup and deployment with Docker

## Installation
You can run `pinggy-server` via Docker using `make up`. Alternatively, follow these steps for a manual setup:

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/pinggy-server.git
    cd pinggy-server
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

| Environment Variable | Description                         | Example Value                  |
|----------------------|-------------------------------------|--------------------------------|
| `DATABASE_URL`       | URL for the database                | `/app/db/pinggy.db`            |
| `PINGGY_TOKEN`       | Optional Pinggy token               | `your_pinggy_token`            |

1. Set up your environment variables in a `.env` file:
    ```env
    DATABASE_URL=/app/db/pinggy.db
    PINGGY_TOKEN=your_pinggy_token  # Optional
    ```

## Usage
1. Run the application:
    ```sh
    uvicorn app.main\:app --host 0.0.0.0 --port 8000
    ```

## API Endpoints

- `POST /api/tunnels`: Create a new tunnel. Accepts a JSON payload with the following fields:
    ```json
    {
        "hostname": "tunnel_host",
        "port": "tunnel_port"
    }
    ```
    **Mock Response:**
    ```json
    {
        "id": 1,
        "status": "RUNNING",
        "hostname": "localhost",
        "port": 3000,
        "http_url": "http://xxxx.pinggy.link",
        "https_url": "https://xxxx.pinggy.link"
    }
    ```

- `GET /api/tunnels/{tunnel_id}`: Retrieve details of a specific tunnel.
    **Mock Response:**
    ```json
    {
        "id": 1,
        "status": "RUNNING",
        "hostname": "localhost",
        "port": 3000,
        "http_url": "http://xxxx.pinggy.link",
        "https_url": "https://xxxx.pinggy.link"
    }
    ```

- `DELETE /api/tunnels/{tunnel_id}`: Delete a specific tunnel.
    **Mock Response:**
    ```json
    {
        "message": "Tunnel with ID 1 has been deleted."
    }
    ```

## Development
1. Run tests:
    ```sh
    pytest
    ```

2. Lint the code:
    ```sh
    flake8
    ```

## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License
This project is licensed under the MIT License.
