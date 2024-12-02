# KKDataD

KKDataD is a financial data distribution service built for the KakiQuant community. It serves as a secure bridge between users and our financial database, providing efficient data access with features like compression and usage tracking.

## Features

- SQL direct querying with security measures
- API key authentication and management
- Data usage tracking and quota management
- LZ4 compression for efficient data transfer
- Support for ClickHouse and MySQL databases

## Installation

1. Clone the repository:

```bash
git clone https://github.com/kakiquant/kkdatad.git
cd kkdatad
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Development

```bash
uvicorn kkdatad.app:app --reload
```

### Production

```bash
uvicorn kkdatad.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```bash
docker build -t kkdatad .
docker run -p 8000:8000 kkdatad
```

## API Documentation

### Authentication

All API endpoints require authentication using an API key. Include the API key in the request header:

```
X-API-Key: your_api_key_here
```

### Endpoints

#### User Management

1. Register User

```http
POST /api/v1/register
Content-Type: application/json

{
    "username": "string",
    "password": "string",
    "invite_code": "string" (optional)
}
```

2. Login

```http
POST /api/v1/login
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

3. Get User Info

```http
GET /api/v1/users/info
Authorization: Bearer {access_token}
```

#### API Keys

1. Create API Key

```http
POST /api/v1/users/api-keys
Authorization: Bearer {access_token}
```

2. List API Keys

```http
GET /api/v1/users/api-keys
Authorization: Bearer {access_token}
```

3. Revoke API Key

```http
DELETE /api/v1/users/api-keys/{key_id}
Authorization: Bearer {access_token}
```

#### Data Access

1. Execute SQL Query

```http
POST /api/v1/sql/
X-API-Key: your_api_key_here
Content-Type: application/json

{
    "query": "SELECT * FROM your_table LIMIT 10"
}
```

Response format:

```json
{
    "status": "success",
    "data": "compressed_hex_data"
}
```

Note: The response data is compressed using LZ4 and encoded in hexadecimal format. Use the provided client library to handle decompression.

### Usage Tracking

1. Get API Usage

```http
GET /api/v1/users/api-quota
Authorization: Bearer {access_token}
```

Response:

```json
{
    "totalQuota": 1000,
    "usedQuota": 50
}
```

## Client Library

For Python users, we recommend using our official client library `kkdatac`:

```bash
pip install kkdatac
```

Example usage:

```python
from kkdatac import KKDataClient

client = KKDataClient(api_key="your_api_key")
df = client.query("SELECT * FROM your_table LIMIT 10")
print(df)
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Copyright © 2024 KakiQuant. All rights reserved.

## Support

- Documentation: https://docs.kakiquant.com
- Email: support@kakiquant.com
- Community Forum: https://forum.kakiquant.com
