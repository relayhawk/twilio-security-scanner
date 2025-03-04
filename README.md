Read the full blog post [here.](https://www.relayhawk.com/blog/twilio-security)

# Twilio Security Scanner

A security scanning tool for Twilio accounts that helps detect misconfigurations and security risks, including:
- Public serverless functions and assets
- Unencrypted HTTP webhooks in phone numbers and messaging services
- API keys older than 90 days

This tool is useful for DevOps, Security Engineers, and compliance teams looking to audit their Twilio configurations for security best practices.

## Prerequisites

- **Option 1: Docker** (recommended for ease of use)
- **Option 2: Python 3.12** (for running locally)
- Twilio account credentials (Account SID and Auth Token)

## Setup

1. Clone the repository
```sh
git clone https://github.com/relayhawk/twilio-security-scanner.git
cd twilio-security-scanner
```


2. Setup authentication

The scanner supports two authentication methods:

### Option 1: API Key (Recommended)
Create an API Key in the Twilio Console with these permissions:
1. Navigate to Console → Account → Account Management → API keys & tokens
2. Click "Create API Key"
3. Select "Main" for the API Key type. 
   * Note: Ideally you would not need this key to be so powerful, but Twilio does not allow us to create a more restrictive key for the permissions we need. We tried the standard key, but we received 401 errors when scanning API keys for old keys. Using a main key is better than using an Auth Token since a service specific api key can easily be revoked and the Auth Token may be used by other systems.

Then add to your `.env` file:
```sh
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_API_KEY_SID=your_api_key_sid
TWILIO_API_KEY_SECRET=your_api_key_secret
```

Note: The API Key needs read permissions for all resources being scanned. If you get a 401 error, verify the API Key has sufficient permissions in the Twilio Console.

### Option 2: Auth Token
Use your account's auth token (less secure for production use) and add this to your `.env` file:
```sh
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
```

We recommend using API Keys because:
1. They can be revoked individually
2. They have more granular permissions
3. They can be rotated without affecting other systems
4. They provide better audit trails

## Usage

### Using Docker Compose
```sh
docker compose up
```

### Using Python directly
```sh
pip install -r requirements.txt
python -m twilio_security_scanner.cli
```

## Output

The scanner checks for several security concerns:

### Serverless Functions and Assets
- Lists all public functions and assets
- Outputs URLs and paths for each public endpoint
- Saves findings to CSV if specified with `-o` flag

### Webhook Security
- Identifies phone numbers using unencrypted HTTP webhooks
- Checks messaging services for unencrypted HTTP URLs
- Reports both primary and fallback URLs using HTTP

### API Key Age
- Identifies API keys older than 90 days
- Reports key names for rotation

### Trusted Apps
- Lists all trusted connect applications
- Shows count of connected applications

## CSV Output

When using the `-o` flag, the scanner will save public serverless findings to a CSV file with:
- Type (Function/Asset)
- URL
- Path
- SID
- Service Name - The friendly name of the Twilio service containing this function/asset
- Service SID - The unique identifier of the service

## Remediation Steps

### Public Functions and Assets
If the scanner finds public functions or assets, you can:
1. Locate the function/asset in the Twilio Console using the provided service name
2. Navigate to: Console → Functions and Assets → Services → [Service Name]
3. Review the function/asset visibility settings
4. Change visibility from "Public" to "Protected" if the endpoint should not be publicly accessible
5. Consider implementing authentication for endpoints that need controlled access

Note: Making a function/asset protected will require valid Twilio credentials to access it.

**Note about Deployment State:**
Functions and assets can exist in two states:
- **Saved but not deployed**: Even if marked as "public", they are not accessible until deployed
- **Deployed**: Will be publicly accessible if marked as "public"


### Unencrypted HTTP Webhooks
For webhooks using HTTP instead of HTTPS:
1. Update all webhook URLs to use HTTPS
2. Ensure your webhook endpoints support HTTPS
3. Update both primary and fallback URLs

### Old API Keys
For API keys older than 90 days:
1. Create new replacement API keys
2. Update applications to use the new keys
3. Revoke the old keys after confirming all systems are working

## Contributing

We welcome contributions from the community! If you'd like to contribute:

* Read the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
* Report bugs or suggest features by opening an [issue](https://github.com/relayhawk/twilio-security-scanner/issues).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
