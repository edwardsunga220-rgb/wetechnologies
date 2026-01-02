import requests
import json
from django.conf import settings
from wetech.utils.retry import retry_network
from wetech.utils.logger import logger


class AzamPayClient:
    def __init__(self):
        # Get configuration from Django settings
        self.app_name = getattr(settings, 'AZAMPAY_APP_NAME', 'We-Tech').strip()
        self.client_id = getattr(settings, 'AZAMPAY_CLIENT_ID', '').strip()
        self.client_secret = getattr(settings, 'AZAMPAY_CLIENT_SECRET', '').strip()
        self.sandbox = getattr(settings, 'AZAMPAY_SANDBOX', True)
        
        if not self.client_id or not self.client_secret:
            raise ValueError("AzamPay API keys not configured. Please set AZAMPAY_CLIENT_ID and AZAMPAY_CLIENT_SECRET in settings.py")
        
        # Debug: Print credential info (without exposing full secrets)
        print(f"--- AZAMPAY INIT: App={self.app_name}, ClientID={self.client_id[:20]}..., SecretLength={len(self.client_secret)}, Sandbox={self.sandbox} ---")
        
        # Set URLs based on sandbox setting
        if self.sandbox:
            # SANDBOX URLS
            self.auth_url = "https://authenticator-sandbox.azampay.co.tz/App/Login"
            self.checkout_url = "https://sandbox.azampay.co.tz/azampay/mno/checkout"
            print("--- AZAMPAY: Using SANDBOX environment ---")
        else:
            # LIVE URLS
            self.auth_url = "https://authenticator.azampay.co.tz/App/Login"
            self.checkout_url = "https://checkout.azampay.co.tz/azampay/mno/checkout"
            print("--- AZAMPAY: Using LIVE environment ---")
    @retry_network
    def get_token(self):
        """1. Generate Session Token. Returns tuple (token, error_message)"""
        headers = {'Content-Type': 'application/json'}
        
        # Ensure credentials are clean (no extra whitespace/newlines)
        clean_client_secret = self.client_secret.strip().replace('\n', '').replace('\r', '')
        clean_client_id = self.client_id.strip().replace('\n', '').replace('\r', '')
        clean_app_name = self.app_name.strip()
        
        payload = {
            "appName": clean_app_name,
            "clientId": clean_client_id,
            "clientSecret": clean_client_secret
        }
        
        try:
            print(f"--- AZAMPAY: Authenticating to {self.auth_url} ---")
            print(f"--- AZAMPAY: App Name: '{clean_app_name}' ---")
            print(f"--- AZAMPAY: Client ID: '{clean_client_id}' ---")
            print(f"--- AZAMPAY: Client Secret length: {len(clean_client_secret)} characters ---")
            print(f"--- AZAMPAY: Client Secret starts with: {clean_client_secret[:30]}... ---")
            print(f"--- AZAMPAY: Payload: {json.dumps({**payload, 'clientSecret': '***HIDDEN***'}, indent=2)} ---")
            
            # Try with SSL verification first, then without if it fails
            try:
                response = requests.post(self.auth_url, json=payload, headers=headers, timeout=30, verify=True)
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as ssl_error:
                print(f"⚠️ SSL error, retrying without verification: {ssl_error}")
                response = requests.post(self.auth_url, json=payload, headers=headers, timeout=30, verify=False)
            
            print(f"--- AZAMPAY: Auth Response Status: {response.status_code} ---")
            print(f"--- AZAMPAY: Auth Response Text: {response.text[:500]} ---")
            
            # Handle 401 Unauthorized (credentials invalid)
            if response.status_code == 401:
                # Try to get more details from the response
                try:
                    error_data = response.json()
                    api_error = error_data.get('message') or error_data.get('msg') or error_data.get('error') or response.text[:200]
                except:
                    api_error = response.text[:200] if response.text else "Unauthorized"
                
                error_msg = f"Invalid credentials (401 Unauthorized). API says: {api_error}. Please verify your Client ID and Client Secret are correct for the SANDBOX environment."
                print(f"❌ AzamPay Auth Failed - Status 401")
                print(f"❌ AzamPay Response: {response.text[:500]}")
                return None, error_msg
            
            # Try to parse JSON response
            try:
                data = response.json()
                print(f"--- AZAMPAY: Response Data: {data} ---")
            except json.JSONDecodeError:
                # If it's not JSON, use the raw text as error message
                error_text = response.text[:200].strip()
                if not error_text:
                    error_text = f"Empty response (Status {response.status_code})"
                error_msg = f"Invalid response from AzamPay API. Status {response.status_code}: {error_text}"
                print(f"❌ AzamPay Auth Failed - {error_msg}")
                return None, error_msg
            
            if response.status_code == 200:
                if data.get('success'):
                    access_token = data.get('data', {}).get('accessToken')
                    if access_token:
                        print("✅ AzamPay Token Received")
                        return access_token, None
                    else:
                        error_msg = "Response success=True but no accessToken found. Full response: " + str(data)[:200]
                        print(f"❌ AzamPay: {error_msg}")
                        return None, error_msg
                else:
                    error_msg = data.get('message') or data.get('msg') or data.get('error') or 'Unknown error from AzamPay API'
                    if isinstance(error_msg, dict):
                        error_msg = str(error_msg)
                    print(f"❌ AzamPay Auth Failed: {error_msg}")
                    return None, error_msg
            else:
                # Non-200 status codes
                error_msg = data.get('message') or data.get('msg') or data.get('error') or f'HTTP {response.status_code}'
                if isinstance(error_msg, dict):
                    error_msg = str(error_msg)
                if not error_msg or error_msg == f'HTTP {response.status_code}':
                    error_msg = f"Authentication failed with status {response.status_code}. Response: {response.text[:200]}"
                print(f"❌ AzamPay Auth Failed - Status {response.status_code}: {error_msg}")
                return None, error_msg
        except requests.exceptions.Timeout:
            error_msg = "Connection timeout - AzamPay API did not respond within 30 seconds"
            print(f"❌ {error_msg}")
            return None, error_msg
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error - Cannot reach AzamPay API: {str(e)}"
            print(f"❌ {error_msg}")
            return None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"❌ AzamPay Unexpected Error: {error_msg}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None, error_msg

    @retry_network
    def mobile_checkout(self, mobile_number, amount, external_id, provider):
        """2. Trigger USSD Push"""
        result = self.get_token()
        if not isinstance(result, tuple) or len(result) != 2:
            return {'success': False, 'message': 'Authentication failed: Invalid response from authentication'}
        
        token, error_message = result
        if not token:
            # Use the actual error message from the API
            if error_message:
                return {'success': False, 'message': f'Authentication failed: {error_message}'}
            else:
                env_mode = "SANDBOX" if self.sandbox else "LIVE"
                return {'success': False, 'message': f'Authentication failed. Please check: 1) Your credentials match the {env_mode} environment, 2) AZAMPAY_SANDBOX setting is correct, 3) Check terminal/console for detailed error logs.'}

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Provider Mapping (AzamPay expects specific strings)
        provider_map = {
            'Tigo': 'Tigo',
            'Airtel': 'Airtel',
            'Halopesa': 'Halopesa',
            'AzamPesa': 'AzamPesa',
            'Mpesa': 'Mpesa' 
        }
        
        # Ensure correct provider format
        mno = provider_map.get(provider, provider)

        payload = {
            "accountNumber": mobile_number, # The customer phone number
            "amount": str(int(amount)),     # Must be a string of an integer
            "currency": "TZS",
            "externalId": external_id,      # Our Invoice ID
            "provider": mno
        }

        print(f"--- AZAMPAY: Sending Push to {mobile_number} ({mno}) ---")

        try:
            print(f"--- AZAMPAY: Sending checkout request to {self.checkout_url} ---")
            print(f"--- AZAMPAY: Payload: {json.dumps(payload, indent=2)} ---")
            response = requests.post(self.checkout_url, json=payload, headers=headers, timeout=30)
            print(f"--- AZAMPAY CHECKOUT RESPONSE: {response.status_code} ---")
            print(f"--- AZAMPAY CHECKOUT RESPONSE TEXT: {response.text[:500]} ---")
            
            data = response.json()
            
            # AzamPay returns success: true if push was sent
            if data.get('success') == True:
                return {'success': True, 'message': data.get('message', 'Payment request sent successfully')}
            else:
                error_msg = data.get('message') or data.get('msg') or data.get('error') or 'Unknown error from AzamPay'
                if isinstance(error_msg, dict):
                    error_msg = str(error_msg)
                return {'success': False, 'message': error_msg}
                
        except requests.exceptions.Timeout:
            return {'success': False, 'message': 'Request timeout - AzamPay API did not respond within 30 seconds'}
        except requests.exceptions.ConnectionError as e:
            return {'success': False, 'message': f'Connection error - Cannot reach AzamPay API: {str(e)}'}
        except json.JSONDecodeError as e:
            return {'success': False, 'message': f'Invalid response from AzamPay API. Response: {response.text[:200]}'}
        except Exception as e:
            import traceback
            print(f"❌ AzamPay Checkout Unexpected Error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return {'success': False, 'message': f'Unexpected error: {str(e)}'}