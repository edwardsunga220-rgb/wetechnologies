import requests
import json
import urllib3
from django.conf import settings
from wetech.utils.retry import retry_network
from wetech.utils.logger import logger

# Suppress the warning that appears when we disable SSL verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Pesapal:
    def __init__(self):
        # 1. LIVE URL (from settings or default)
        self.base_url = getattr(settings, 'PESAPAL_BASE_URL', 'https://pay.pesapal.com/v3')
        
        # 2. Get keys from Django settings (single source of truth)
        self.key = getattr(settings, 'PESAPAL_CONSUMER_KEY', '').strip()  # Remove any whitespace
        self.secret = getattr(settings, 'PESAPAL_CONSUMER_SECRET', '').strip()  # Remove any whitespace
        
        if not self.key or not self.secret:
            raise ValueError("Pesapal API keys not configured. Please set PESAPAL_CONSUMER_KEY and PESAPAL_CONSUMER_SECRET in settings.py")

    @retry_network
    def get_access_token(self):
        """Authenticate and get Token. Returns tuple (token, error_message)"""
        url = f"{self.base_url}/api/Auth/RequestToken"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "consumer_key": self.key,
            "consumer_secret": self.secret
        }
        
        # Debug: Log key info (without exposing full secrets)
        key_preview = self.key[:10] + "..." if len(self.key) > 10 else self.key
        secret_preview = self.secret[:10] + "..." if len(self.secret) > 10 else self.secret
        print(f"--- [1] Attempting Auth: {url} ---")
        print(f"--- [DEBUG] Key length: {len(self.key)}, Secret length: {len(self.secret)} ---")
        print(f"--- [DEBUG] Key preview: {key_preview}, Secret preview: {secret_preview} ---")
        
        try:
            # Try with SSL verification first (ngrok uses proper SSL)
            # If that fails, try without verification as fallback
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=30, verify=True)
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as ssl_error:
                print(f"⚠️ SSL error, retrying without verification: {ssl_error}")
                response = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)
            
            print(f"--- [2] Server Replied: {response.status_code} ---")
            print(f"--- [DEBUG] Response text: {response.text} ---")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Safety check: ensure data is a dict
                    if data is None:
                        error_msg = f"Empty response from Pesapal API. Response body: {response.text[:200]}"
                        print(f"❌ Error: {error_msg}")
                        return None, error_msg
                    
                    if not isinstance(data, dict):
                        error_msg = f"Unexpected response format from Pesapal API. Response body: {response.text[:200]}"
                        print(f"❌ Error: {error_msg}")
                        return None, error_msg
                    
                    # Check for token FIRST (success case) - prioritize token over error
                    token = data.get('token')
                    if token:
                        print("✅ Token Received")
                        return token, None
                    
                    # Only check for errors if there's no token
                    if 'error' in data:
                        error_info = data.get('error', {})
                        # Safety check: ensure error_info is a dict
                        if not isinstance(error_info, dict):
                            error_info = {}
                        
                        error_code = error_info.get('code', 'unknown_error') if isinstance(error_info, dict) else 'unknown_error'
                        error_message = error_info.get('message', '') if isinstance(error_info, dict) else ''
                        
                        # Also check the raw response for additional error details
                        print(f"❌ DEBUG: Full error response: {data}")
                        print(f"❌ DEBUG: Error info: {error_info}")
                        print(f"❌ DEBUG: Error code: {error_code}, Error message: {error_message}")
                        
                        # Handle specific error codes
                        if 'invalid_consumer_key_or_secret' in str(error_code).lower():
                            error_msg = "Invalid Pesapal API credentials. Please check your Consumer Key and Consumer Secret in settings."
                        elif error_code == 'unknown_error' and error_message:
                            # If we don't have a specific code but have a message, use the message
                            error_msg = f"Pesapal API Error: {error_message}"
                        elif error_code == 'unknown_error':
                            # If we really don't know, show the full response
                            error_msg = f"Pesapal API Error. Full response: {str(data)[:300]}"
                        else:
                            error_msg = f"Pesapal API Error: {error_code}"
                            if error_message:
                                error_msg += f" - {error_message}"
                        
                        print(f"❌ Error: {error_msg}")
                        return None, error_msg
                    
                    # If we get here, there's no token and no error field - unexpected response
                    error_msg = f"Response 200 but no token found. Response body: {response.text[:200]}"
                    print(f"❌ Error: {error_msg}")
                    return None, error_msg
                        
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON response: {response.text[:200]}"
                    print(f"❌ Error: {error_msg}")
                    return None, error_msg
                except Exception as e:
                    error_msg = f"Error parsing response: {str(e)}. Response body: {response.text[:200]}"
                    print(f"❌ Error: {error_msg}")
                    return None, error_msg
            else:
                try:
                    # Try to parse error from non-200 responses
                    error_data = response.json()
                    if error_data and isinstance(error_data, dict) and 'error' in error_data:
                        error_info = error_data.get('error', {})
                        if isinstance(error_info, dict):
                            error_code = error_info.get('code', 'unknown_error')
                            error_message = error_info.get('message', '')
                            error_msg = f"Auth Failed (Status {response.status_code}): {error_code}"
                            if error_message:
                                error_msg += f" - {error_message}"
                        else:
                            error_msg = f"Auth Failed (Status {response.status_code}). Response: {response.text[:200]}"
                    else:
                        error_msg = f"Auth Failed (Status {response.status_code}). Response: {response.text[:200]}"
                except json.JSONDecodeError:
                    error_msg = f"Auth Failed (Status {response.status_code}). Response: {response.text[:200]}"
                except Exception as e:
                    error_msg = f"Auth Failed (Status {response.status_code}). Error: {str(e)}. Response: {response.text[:200]}"
                
                print(f"❌ {error_msg}")
                return None, error_msg

        except requests.exceptions.Timeout:
            error_msg = "Connection timeout - Pesapal API did not respond within 30 seconds"
            print(f"❌ {error_msg}")
            return None, error_msg
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error - Cannot reach Pesapal API: {str(e)}"
            print(f"❌ {error_msg}")
            return None, error_msg
        except Exception as e:
            # Catch any unexpected errors and return safely
            error_msg = f"Unexpected error: {str(e)}"
            print(f"❌ CRITICAL ERROR: {error_msg}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return None, error_msg

    def register_ipn_url(self, token, ipn_url):
        """Register Notification URL"""
        url = f"{self.base_url}/api/URLSetup/RegisterIPN"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": ipn_url,
            "ipn_notification_type": "GET"
        }
        
        print(f"--- [3] Registering IPN: {ipn_url} ---")
        
        try:
            try:
                response = requests.post(url, json=payload, headers=headers, verify=True, timeout=30)
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                response = requests.post(url, json=payload, headers=headers, verify=False, timeout=30)
            
            print(f"--- [4] IPN Status: {response.status_code} ---")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result and isinstance(result, dict):
                        return result.get('ipn_id')
                except json.JSONDecodeError:
                    print(f"⚠️ IPN Registration: Invalid JSON response")
            print(f"⚠️ IPN Registration failed: {response.status_code} - {response.text[:200]}")
            return None
        except Exception as e:
            print(f"❌ IPN Error: {e}")
            return None

    @retry_network
    def submit_order(self, token, order_data):
        """Submit the Order"""
        url = f"{self.base_url}/api/Transactions/SubmitOrderRequest"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print("--- [5] Submitting Order Data ---")
        
        try:
            try:
                response = requests.post(url, json=order_data, headers=headers, verify=True, timeout=30)
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                response = requests.post(url, json=order_data, headers=headers, verify=False, timeout=30)
            
            print(f"--- [6] Order Status: {response.status_code} ---")
            
            try:
                result = response.json()
                # Ensure we always return a dict
                if result is None:
                    return {'error': {'message': 'Empty response from Pesapal API'}}
                return result
            except json.JSONDecodeError:
                return {'error': {'message': f'Invalid JSON response: {response.text[:200]}'}}
        except requests.exceptions.Timeout:
            return {'error': {'message': 'Request timeout - Pesapal API did not respond within 30 seconds'}}
        except requests.exceptions.ConnectionError as e:
            return {'error': {'message': f'Connection error: {str(e)}'}}
        except Exception as e:
            print(f"❌ Order Submit Error: {e}")
            return {'error': {'message': str(e)}}

    @retry_network
    def get_transaction_status(self, token, order_tracking_id):
        url = f"{self.base_url}/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        try:
            try:
                response = requests.get(url, headers=headers, verify=True, timeout=30)
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                response = requests.get(url, headers=headers, verify=False, timeout=30)
            
            try:
                result = response.json()
                return result if result is not None else {}
            except json.JSONDecodeError:
                return {}
        except Exception as e:
            print(f"❌ Transaction Status Error: {e}")
            return {}