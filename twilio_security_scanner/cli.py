import argparse
import logging
import os
from twilio.rest import Client
from .config import load_config
from .scanner import TwilioSecurityScanner
from .utils import write_items_to_csv

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Twilio Security Scanner')
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output CSV filename for public entities'
    )
    args = parser.parse_args()

    try:
        # Load and validate configuration
        credentials = load_config()
        
        # Initialize client based on authentication method
        if len(credentials) == 2 and credentials[0].startswith('SK'):  # API Key
            api_key_sid, api_key_secret = credentials
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            if not account_sid:
                raise ValueError("TWILIO_ACCOUNT_SID is required even when using API Key authentication")
            client = Client(api_key_sid, api_key_secret, account_sid)
        else:  # Auth Token
            account_sid, auth_token = credentials
            client = Client(account_sid, auth_token)
            
        scanner = TwilioSecurityScanner(client)

        # Run security checks
        public_items = scanner.scan_public_serverless()
        insecure_numbers = scanner.scan_phone_numbers()
        insecure_messaging = scanner.scan_messaging_services()
        old_api_keys = scanner.scan_api_keys()

        # Write results to CSV if requested
        if args.output and public_items:
            with open(args.output, 'w', newline='') as fp:
                write_items_to_csv(public_items, fp)
                logger.info(f"Results written to {args.output}")

        # Log summary
        logger.info("\nScan Summary:")
        logger.info(f"- Public Serverless Items: {len(public_items)}")
        logger.info(f"- Insecure Phone Numbers: {len(insecure_numbers)}")
        logger.info(f"- Insecure Messaging Services: {len(insecure_messaging)}")
        logger.info(f"- Old API Keys: {len(old_api_keys)}")

    except Exception as e:
        logger.error(f"Error during scan: {str(e)}")
        raise


if __name__ == "__main__":
    main()
