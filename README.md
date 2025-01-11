# pinggy-server

## Overview
`pinggy-server` is a FastAPI-based application that manages SSH tunnels using Pinggy. It allows you to create and manage tunnels programmatically. Itr currently only supports http tunnels. 

## Features
- Create SSH tunnels
- Manage tunnel status

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/pinggy-server.git
    cd pinggy-server
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration
1. Set up your environment variables in a `.env` file:
    ```env
    DATABASE_URL=/app/db/pinggy.db
    PINGGY_TOKEN=your_pinggy_token  # optional
    ```

## Usage
1. Run the application:
    ```sh
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```

## API Endpoints
- `POST /api/tunnels`: Create a new tunnel; accepts a JSON payload with the following fields:
    ```json
    {
        "hostname": "tunnel_host",
        "port": "tunnel_port"
    }
    ```
- `GET /api/tunnels/{tunnel_id}`: Get tunnel details
- `DELETE /api/tunnels/{tunnel_id}`: Delete a tunnel

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