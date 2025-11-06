

import hashlib
import time
import secrets
from django.core.cache import cache, caches
from django.contrib.auth.models import AnonymousUser

class HTMXTokenManager:
    """
    Manages one-time use tokens for HTMX requests with pre-verification registry
    """
    
    @staticmethod
    def generate_token(request, action_type='general', expires_in=300):
        """
        Generate a one-time token and PRE-REGISTER it for instant validation
        
        Args:
            request: Django request object
            action_type: Type of action (upload, form, search, etc.)
            expires_in: Seconds until expiration (default 5 minutes)
        
        Returns:
            str: One-time token (PRE-VERIFIED in server registry)
        """
        if isinstance(request.user, AnonymousUser):
            user_id = 'anonymous'
        else:
            user_id = str(request.user.id)
            
        session_key = request.session.session_key or 'no-session'
        timestamp = str(int(time.time()))
        
        # Create unique token data
        token_data = f"{user_id}:{session_key}:{action_type}:{timestamp}:{secrets.token_hex(16)}"
        
        # Generate token hash
        token = hashlib.sha256(token_data.encode()).hexdigest()[:32]
        
        # PRE-REGISTER token in server registry for instant validation
        cache_key = f"htmx_token:{token}"
        registry_key = f"htmx_registry:{user_id}:{session_key}"  # User-specific registry
        
        cache_data = {
            'user_id': user_id,
            'session_key': session_key,
            'action_type': action_type,
            'created_at': timestamp,
            'used': False,
            'pre_verified': True,  # Server knows this token exists
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'token': token,  # Store token reference
            # WebSocket connection binding support
            'wss_connection_id': request.META.get('WSS_CONNECTION_ID'),
            'bound_to_connection': bool(request.META.get('WSS_CONNECTION_ID')),
            'distribution_method': 'wss' if request.META.get('WSS_CONNECTION_ID') else 'http'
        }
        
        # Store individual token data
        cache.set(cache_key, cache_data, expires_in)
        
        # Add to user's token registry for instant lookup
        user_tokens = cache.get(registry_key, [])
        user_tokens.append({
            'token': token,
            'action_type': action_type,
            'expires_at': int(time.time()) + expires_in,
            'pre_verified': True,
            'wss_bound': bool(request.META.get('WSS_CONNECTION_ID')),
            'connection_id': request.META.get('WSS_CONNECTION_ID')
        })
        
        # Keep only non-expired tokens in registry
        current_time = int(time.time())
        user_tokens = [t for t in user_tokens if t['expires_at'] > current_time]
        
        cache.set(registry_key, user_tokens, expires_in)
        
        return token
    
    @staticmethod
    def is_token_pre_verified(request, token, action_type='general'):
        """
        INSTANT pre-verification check - server already knows if token exists
        This runs BEFORE any heavy processing to verify legitimacy
        
        Args:
            request: Django request object
            token: Token to pre-verify
            action_type: Expected action type
            
        Returns:
            bool: True if token exists in server registry (pre-verified)
        """
        if isinstance(request.user, AnonymousUser):
            user_id = 'anonymous'
        else:
            user_id = str(request.user.id)
            
        session_key = request.session.session_key or 'no-session'
        registry_key = f"htmx_registry:{user_id}:{session_key}"
        
        # Check user's token registry first (fastest lookup)
        user_tokens = cache.get(registry_key, [])
        current_time = int(time.time())
        
        for token_entry in user_tokens:
            if (token_entry['token'] == token and 
                token_entry['action_type'] == action_type and
                token_entry.get('pre_verified', False) and
                token_entry['expires_at'] > current_time):
                return True
                
        return False
    
    @staticmethod
    def validate_and_consume_token(request, token, action_type='general'):
        """
        Full validation and consumption (after pre-verification passes)
        
        Args:
            request: Django request object  
            token: Token to validate
            action_type: Expected action type
            
        Returns:
            bool: True if token is valid and consumed
        """
        # First do instant pre-verification check
        if not HTMXTokenManager.is_token_pre_verified(request, token, action_type):
            return False
            
        cache_key = f"htmx_token:{token}"
        token_data = cache.get(cache_key)
        
        if not token_data:
            return False
            
        # Check if already used
        if token_data.get('used', True):
            return False
            
        # Validate user context (full validation)
        current_user_id = str(request.user.id) if not isinstance(request.user, AnonymousUser) else 'anonymous'
        current_session = request.session.session_key or 'no-session'
        current_ip = request.META.get('REMOTE_ADDR')
        
        if (token_data['user_id'] != current_user_id or 
            token_data['session_key'] != current_session or
            token_data['action_type'] != action_type or
            token_data.get('ip_address') != current_ip):
            return False
            
        # Mark as used (makes it obsolete)
        token_data['used'] = True
        token_data['used_at'] = str(int(time.time()))
        cache.set(cache_key, token_data, 60)  # Keep for 1 minute for logging
        
        # Remove from user registry (consumed)
        registry_key = f"htmx_registry:{current_user_id}:{current_session}"
        user_tokens = cache.get(registry_key, [])
        user_tokens = [t for t in user_tokens if t['token'] != token]
        cache.set(registry_key, user_tokens, 300)
        
        return True
    
    @staticmethod
    def generate_dom_salt(request, salt_sources=None):
        """
        Generate salt that client can derive from DOM elements
        Both server and client can compute this independently
        """
        if salt_sources is None:
            salt_sources = [
                'session_key',
                'user_agent_hash', 
                'timestamp_interval',
                'csrf_token_hash',
                'dom_fingerprint'
            ]
        
        salt_components = []
        
        for source in salt_sources:
            if source == 'session_key':
                # Client can get this from sessionStorage or meta tag
                session_key = request.session.session_key or 'no-session'
                salt_components.append(session_key[:8])  # First 8 chars
                
            elif source == 'user_agent_hash':
                # Client can hash their own navigator.userAgent
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                ua_hash = hashlib.md5(user_agent.encode()).hexdigest()[:6]
                salt_components.append(ua_hash)
                
            elif source == 'timestamp_interval':
                # Both sides can compute current 5-minute interval
                interval = int(time.time()) // 300  # 5-minute intervals
                salt_components.append(str(interval))
                
            elif source == 'csrf_token_hash':
                # Client can get CSRF token from DOM
                csrf_token = request.META.get('CSRF_COOKIE', '')
                if csrf_token:
                    csrf_hash = hashlib.md5(csrf_token.encode()).hexdigest()[:6]
                    salt_components.append(csrf_hash)
                    
            elif source == 'dom_fingerprint':
                # Client can compute from DOM structure
                # Server precomputes and embeds hint
                dom_hint = f"body-{len(request.path)}-{request.method}"
                salt_components.append(hashlib.md5(dom_hint.encode()).hexdigest()[:4])
        
        # Combine all components into final salt
        combined = ':'.join(salt_components)
        final_salt = hashlib.sha256(combined.encode()).hexdigest()[:16]
        
        return final_salt, salt_components
    
    @staticmethod
    def generate_client_retoken(request, original_token, action_type='general'):
        """
        Generate a client-side retoken using derived salt
        Client can regenerate this same token using DOM-derived salt
        """
        # Generate salt that client can also derive
        salt, salt_components = HTMXTokenManager.generate_dom_salt(request)
        
        # Create retoken data
        if isinstance(request.user, AnonymousUser):
            user_id = 'anonymous'
        else:
            user_id = str(request.user.id)
            
        # Retoken combines original token + salt + action
        retoken_data = f"{original_token}:{salt}:{action_type}:{user_id}"
        retoken = hashlib.sha256(retoken_data.encode()).hexdigest()[:24]
        
        # Store retoken mapping
        cache_key = f"htmx_retoken:{retoken}"
        cache.set(cache_key, {
            'original_token': original_token,
            'salt': salt,
            'salt_components': salt_components,
            'action_type': action_type,
            'user_id': user_id,
            'created_at': int(time.time()),
            'client_derivable': True
        }, 900)  # 15 minutes
        
        return retoken, salt_components
    
    @staticmethod
    def validate_client_retoken(request, retoken, action_type='general'):
        """
        Validate a client-generated retoken
        """
        cache_key = f"htmx_retoken:{retoken}"
        retoken_data = cache.get(cache_key)
        
        if not retoken_data:
            return False
            
        # Verify salt can still be derived the same way
        current_salt, _ = HTMXTokenManager.generate_dom_salt(request)
        
        if current_salt != retoken_data['salt']:
            return False  # Salt changed (expired interval, etc.)
            
        # Verify original token is still valid
        original_token = retoken_data['original_token']
        if not HTMXTokenManager.is_token_pre_verified(request, original_token, action_type):
            return False
            
        return True

    @staticmethod
    def get_token_for_context(request, action_type='general'):
        """
        Generate token specifically for template context
        """
        return HTMXTokenManager.generate_token(request, action_type)
    
    @staticmethod
    def cleanup_expired_tokens(request):
        """
        Clean up expired tokens from user registry
        """
        if isinstance(request.user, AnonymousUser):
            user_id = 'anonymous'
        else:
            user_id = str(request.user.id)
            
        session_key = request.session.session_key or 'no-session'
        registry_key = f"htmx_registry:{user_id}:{session_key}"
        
        user_tokens = cache.get(registry_key, [])
        current_time = int(time.time())
        
        # Remove expired tokens
        active_tokens = [t for t in user_tokens if t['expires_at'] > current_time]
        
        if len(active_tokens) != len(user_tokens):
            cache.set(registry_key, active_tokens, 300)
            
        return len(user_tokens) - len(active_tokens)  # Return number cleaned

    @staticmethod
    def benchmark_token_performance(request, iterations=1000):
        """
        Benchmark server-side token operations
        """
        import time
        results = {
            'token_generation': [],
            'pre_verification': [],
            'full_validation': [],
            'salt_derivation': []
        }
        
        print(f"🚀 Benchmarking server-side token operations ({iterations} iterations)...")
        
        # Benchmark token generation
        for i in range(iterations):
            start = time.perf_counter()
            token = HTMXTokenManager.generate_token(request, 'benchmark')
            end = time.perf_counter()
            results['token_generation'].append((end - start) * 1000)  # Convert to ms
        
        # Benchmark salt derivation
        for i in range(iterations):
            start = time.perf_counter()
            HTMXTokenManager.generate_dom_salt(request)
            end = time.perf_counter()
            results['salt_derivation'].append((end - start) * 1000)
        
        # Generate test tokens for validation benchmarks
        test_tokens = [HTMXTokenManager.generate_token(request, 'benchmark') for _ in range(100)]
        
        # Benchmark pre-verification
        for i in range(iterations):
            token = test_tokens[i % len(test_tokens)]
            start = time.perf_counter()
            HTMXTokenManager.is_token_pre_verified(request, token, 'benchmark')
            end = time.perf_counter()
            results['pre_verification'].append((end - start) * 1000)
        
        # Calculate statistics
        stats = {}
        for operation, times in results.items():
            if times:
                sorted_times = sorted(times)
                stats[operation] = {
                    'min': f"{min(times):.3f}ms",
                    'max': f"{max(times):.3f}ms", 
                    'avg': f"{sum(times)/len(times):.3f}ms",
                    'median': f"{sorted_times[len(sorted_times)//2]:.3f}ms",
                    'p95': f"{sorted_times[int(len(sorted_times)*0.95)]:.3f}ms",
                    'throughput': f"{1000/(sum(times)/len(times)):.0f} ops/sec"
                }
        
        return stats

    @staticmethod
    def obfuscate_token_to_latin(token):
        """
        Convert token to Latin-looking text for obfuscation
        """
        latin_syllables = [
            'ac', 'ad', 'al', 'am', 'an', 'ar', 'as', 'at', 'ba', 'be',
            'bi', 'bo', 'bu', 'ca', 'ce', 'ci', 'co', 'cu', 'da', 'de',
            'di', 'do', 'du', 'ef', 'el', 'em', 'en', 'er', 'es', 'et',
            'ex', 'fa', 'fe', 'fi', 'fo', 'fu', 'ga', 'ge', 'gi', 'go',
            'gu', 'ha', 'he', 'hi', 'ho', 'hu', 'ia', 'ic', 'id', 'ig',
            'il', 'im', 'in', 'ip', 'ir', 'is', 'it', 'la', 'le', 'li',
            'lo', 'lu', 'ma', 'me', 'mi', 'mo', 'mu', 'na', 'ne', 'ni',
            'no', 'nu', 'ob', 'od', 'of', 'og', 'ol', 'om', 'on', 'op',
            'or', 'os', 'ot', 'pa', 'pe', 'pi', 'po', 'pu', 'qu', 're',
            'ri', 'ro', 'ru', 'sa', 'se', 'si', 'so', 'su', 'ta', 'te',
            'ti', 'to', 'tu', 'ub', 'ud', 'uf', 'ug', 'ul', 'um', 'un',
            'up', 'ur', 'us', 'ut', 've', 'vi', 'vo', 'vu'
        ]
        
        latin_suffixes = ['um', 'us', 'is', 'es', 'ae', 'a', 'o', 'i']
        
        # Convert token hex to Latin syllables
        result = ''
        word_count = 0
        
        for i in range(0, len(token), 2):
            if i + 1 < len(token):
                hex_pair = token[i:i+2]
                try:
                    index = int(hex_pair, 16) % len(latin_syllables)
                    result += latin_syllables[index]
                    
                    # Add suffix every 2-4 syllables to create "words"
                    if (i // 2 + 1) % (2 + (int(hex_pair, 16) % 3)) == 0:
                        suffix_index = int(hex_pair, 16) % len(latin_suffixes)
                        result += latin_suffixes[suffix_index]
                        
                        word_count += 1
                        # Space between words (except last)
                        if word_count < 6 and i < len(token) - 4:
                            result += ' '
                except ValueError:
                    continue
        
        # Ensure proper Latin capitalization
        words = result.split(' ')
        capitalized_words = [word.capitalize() for word in words if word]
        
        return ' '.join(capitalized_words)
    
    @staticmethod
    def deobfuscate_latin_to_token(latin_text):
        """
        Convert Latin text back to original token
        """
        latin_syllables = [
            'ac', 'ad', 'al', 'am', 'an', 'ar', 'as', 'at', 'ba', 'be',
            'bi', 'bo', 'bu', 'ca', 'ce', 'ci', 'co', 'cu', 'da', 'de',
            'di', 'do', 'du', 'ef', 'el', 'em', 'en', 'er', 'es', 'et',
            'ex', 'fa', 'fe', 'fi', 'fo', 'fu', 'ga', 'ge', 'gi', 'go',
            'gu', 'ha', 'he', 'hi', 'ho', 'hu', 'ia', 'ic', 'id', 'ig',
            'il', 'im', 'in', 'ip', 'ir', 'is', 'it', 'la', 'le', 'li',
            'lo', 'lu', 'ma', 'me', 'mi', 'mo', 'mu', 'na', 'ne', 'ni',
            'no', 'nu', 'ob', 'od', 'of', 'og', 'ol', 'om', 'on', 'op',
            'or', 'os', 'ot', 'pa', 'pe', 'pi', 'po', 'pu', 'qu', 're',
            'ri', 'ro', 'ru', 'sa', 'se', 'si', 'so', 'su', 'ta', 'te',
            'ti', 'to', 'tu', 'ub', 'ud', 'uf', 'ug', 'ul', 'um', 'un',
            'up', 'ur', 'us', 'ut', 've', 'vi', 'vo', 'vu'
        ]
        
        latin_suffixes = ['um', 'us', 'is', 'es', 'ae', 'a', 'o', 'i']
        
        # Clean and normalize text
        clean_text = latin_text.replace(' ', '').lower()
        
        # Remove known suffixes
        for suffix in latin_suffixes:
            clean_text = clean_text.replace(suffix, '')
        
        # Convert syllables back to hex
        token = ''
        for i in range(0, len(clean_text), 2):
            if i + 1 < len(clean_text):
                syllable = clean_text[i:i+2]
                if syllable in latin_syllables:
                    index = latin_syllables.index(syllable)
                    hex_val = format(index, '02x')
                    token += hex_val
        
        return token
    
    @staticmethod
    def generate_obfuscated_retoken(request, original_token, action_type='general'):
        """
        Generate Latin-obfuscated retoken
        """
        # Generate normal retoken
        retoken, _ = HTMXTokenManager.generate_client_retoken(
            request, original_token, action_type
        )
        
        # Obfuscate to Latin
        latin_obfuscated = HTMXTokenManager.obfuscate_token_to_latin(retoken)
        
        # Store mapping for deobfuscation
        cache_key = f"htmx_latin:{latin_obfuscated.replace(' ', '_')}"
        cache.set(cache_key, {
            'original_retoken': retoken,
            'action_type': action_type,
            'created_at': int(time.time()),
            'obfuscated': True
        }, 900)  # 15 minutes
        
        return latin_obfuscated, retoken
    
    @staticmethod
    def validate_latin_retoken(request, latin_token, action_type='general'):
        """
        Validate Latin-obfuscated retoken
        """
        # Try direct mapping first (fastest)
        cache_key = f"htmx_latin:{latin_token.replace(' ', '_')}"
        latin_data = cache.get(cache_key)
        
        if latin_data:
            original_retoken = latin_data['original_retoken']
            return HTMXTokenManager.validate_client_retoken(request, original_retoken, action_type)
        
        # Fallback: deobfuscate and validate
        try:
            deobfuscated_token = HTMXTokenManager.deobfuscate_latin_to_token(latin_token)
            return HTMXTokenManager.validate_client_retoken(request, deobfuscated_token, action_type)
        except:
            return False


# Decorator for views that require pre-verified tokens
def require_pre_verified_token(action_type='general'):
    """
    Decorator to ensure view has pre-verified token before processing
    Usage: @require_pre_verified_token('form')
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            # Get token from headers
            token = request.META.get('HTTP_X_ONE_TIME_TOKEN')
            
            if not token:
                from django.http import JsonResponse
                return JsonResponse({'error': 'Missing token'}, status=400)
            
            # INSTANT pre-verification check (before any processing)
            if not HTMXTokenManager.is_token_pre_verified(request, token, action_type):
                from django.http import JsonResponse
                return JsonResponse({'error': 'Invalid or expired token'}, status=403)
            
            # Token is pre-verified, proceed with view
            return view_func(request, *args, **kwargs)
            
        return wrapped_view
    return decorator



def require_valid_token(action_type='general'):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            token = request.META.get('HTTP_X_ONE_TIME_TOKEN')
            if not token:
                from django.http import JsonResponse
                return JsonResponse({'error': 'Missing token'}, status=400)

            if not HTMXTokenManager.validate_and_consume_token(request, token, action_type):
                from django.http import JsonResponse
                return JsonResponse({'error': 'Invalid token or already used'}, status=403)

            # ✅ Correct placement: call the actual view now
            return view_func(request, *args, **kwargs)

        return wrapped_view   # not `wrapper`
    return decorator



# WebSocket-enhanced token operations
class WSTokenManager:
    """
    Enhanced token manager with WebSocket connection binding support
    """
    
    @staticmethod
    def validate_connection_bound_token(token, connection_id):
        """
        Validate token is bound to specific WebSocket connection
        
        Args:
            token: Token to validate
            connection_id: WebSocket connection ID
            
        Returns:
            bool: True if token is valid and bound to connection
        """
        # Get token data from cache
        cache_key = f"htmx_token:{token}"
        token_data = cache.get(cache_key)
        
        if not token_data:
            return False
        
        # Check if token is bound to this connection
        if not token_data.get('bound_to_connection'):
            return False
        
        if token_data.get('wss_connection_id') != connection_id:
            return False
        
        # Check if token has been used
        if token_data.get('used'):
            return False
        
        return True
    
    
    @staticmethod
    def get_connection_tokens(connection_id):
        redis_cache = caches['default']
        pattern = f"hyperx:htmx_token:*"
        matching = []
        for key in redis_cache.iter_keys(pattern):  # works for Redis backend
            data = redis_cache.get(key)
            if data and data.get('wss_connection_id') == connection_id:
                matching.append(data)
        return matching


    
    @staticmethod
    def push_token_to_connection(connection_id, token, action_type='general'):
        """
        Push token to specific WebSocket connection
        
        Args:
            connection_id: WebSocket connection ID
            token: Token to push
            action_type: Type of action token is for
            
        Returns:
            bool: True if push was successful
        """
        # Store token push request in cache for WebSocket consumer to pickup
        push_key = f"wss_token_push:{connection_id}"
        push_data = {
            'token': token,
            'action_type': action_type,
            'pushed_at': int(time.time()),
            'status': 'pending'
        }
        
        # Store for 30 seconds - WebSocket consumer should pick it up quickly
        cache.set(push_key, push_data, 30)
        
        return True
    
    @staticmethod
    def create_security_mesh_token(session_key, user_id='anonymous'):
        """
        Create special security mesh authentication token
        
        Args:
            session_key: Django session key
            user_id: User ID (optional)
            
        Returns:
            str: Security mesh token
        """
        timestamp = str(int(time.time()))
        mesh_data = f"security_mesh:{user_id}:{session_key}:{timestamp}:{secrets.token_hex(16)}"
        mesh_token = hashlib.sha256(mesh_data.encode()).hexdigest()[:32]
        
        # Store mesh token
        cache.set(
            f"security_mesh_token:{mesh_token}",
            {
                'user_id': user_id,
                'session_key': session_key,
                'created_at': timestamp,
                'token_type': 'security_mesh',
                'expires_at': int(time.time()) + 3600  # 1 hour
            },
            3600
        )
        
        return mesh_token
    
