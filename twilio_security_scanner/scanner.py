import logging
from datetime import datetime, timedelta, timezone
from typing import List
from twilio.rest import Client
from .utils import PublicEntity

logger = logging.getLogger(__name__)


class TwilioSecurityScanner:
    def __init__(self, client: Client):
        self.client = client

    def scan_phone_numbers(self) -> List[str]:
        """Scan for phone numbers with unencrypted HTTP webhooks"""
        numbers_with_http_webhooks = []
        logger.debug("Checking phone number webhooks for unencrypted HTTP...")

        for number in self.client.incoming_phone_numbers.stream():
            if (number.voice_url and number.voice_url.startswith('http:')) or \
               (number.sms_url and number.sms_url.startswith('http:')):
                logger.warning(
                    f"Phone number {number.phone_number} has an unencrypted HTTP voice/SMS URL"
                )
                numbers_with_http_webhooks.append(number.phone_number)

            if (number.voice_fallback_url and number.voice_fallback_url.startswith('http:')) or \
               (number.sms_fallback_url and number.sms_fallback_url.startswith('http:')):
                logger.warning(
                    f"Phone number {number.phone_number} has an unencrypted HTTP fallback URL"
                )
                numbers_with_http_webhooks.append(number.phone_number)

        return numbers_with_http_webhooks

    def scan_messaging_services(self) -> List[str]:
        """Scan for messaging services with unencrypted HTTP webhooks"""
        services_with_http_webhooks = []
        logger.debug("Checking messaging services for unencrypted HTTP...")

        for service in self.client.messaging.v1.services.stream():
            if service.fallback_url and service.fallback_url.startswith('http:'):
                logger.warning(
                    f"Messaging service {service.friendly_name} has an unencrypted HTTP fallback URL"
                )
                services_with_http_webhooks.append(service.friendly_name)

            if service.inbound_request_url and service.inbound_request_url.startswith('http:'):
                logger.warning(
                    f"Messaging service {service.friendly_name} has an unencrypted HTTP inbound request URL"
                )
                services_with_http_webhooks.append(service.friendly_name)

        return services_with_http_webhooks

    def scan_api_keys(self) -> List[str]:
        """Scan for API keys older than 90 days"""
        old_keys = []
        logger.debug("Checking for API keys older than 90 days...")

        for key in self.client.keys.stream():
            now = datetime.utcnow().replace(tzinfo=timezone.utc)
            if now - key.date_created > timedelta(days=90):
                logger.warning(f"API Key {key.friendly_name} is older than 90 days")
                old_keys.append(key.friendly_name)

        return old_keys

    def scan_public_serverless(self) -> List[PublicEntity]:
        """Scan for public serverless functions and assets"""
        public_items = []
        services = self.client.serverless.v1.services.list()

        if not services:
            logger.debug("No serverless services found")
            return []

        for service in services:
            logger.debug(f"Checking Service: {service.friendly_name} (SID: {service.sid})")

            domains = self.client.serverless.v1.services(service.sid).environments.list()
            service_domain = domains[0].domain_name if domains else None

            if not service_domain:
                continue

            # Scan functions
            for function in self.client.serverless.v1.services(service.sid).functions.list():
                versions = self.client.serverless.v1.services(service.sid).functions(
                    function.sid
                ).function_versions.list()

                if versions and versions[0].visibility == 'public':
                    public_items.append(
                        PublicEntity(
                            type="Function",
                            url=f"https://{service_domain}{versions[0].path}",
                            path=versions[0].path,
                            SID=function.sid,
                            service_name=service.friendly_name,
                            service_sid=service.sid
                        )
                    )
                    logger.warning(
                        f"Public function found in service '{service.friendly_name}': {versions[0].path}"
                    )

            # Scan assets
            for asset in self.client.serverless.v1.services(service.sid).assets.list():
                versions = self.client.serverless.v1.services(service.sid).assets(
                    asset.sid
                ).asset_versions.list()

                if versions and versions[0].visibility == 'public':
                    public_items.append(
                        PublicEntity(
                            type="Asset",
                            url=f"https://{service_domain}{versions[0].path}",
                            path=versions[0].path,
                            SID=asset.sid,
                            service_name=service.friendly_name,
                            service_sid=service.sid
                        )
                    )
                    logger.warning(
                        f"Public asset found in service '{service.friendly_name}': {versions[0].path}"
                    )

        return public_items
