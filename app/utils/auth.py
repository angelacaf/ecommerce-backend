"""
JWT Authentication Utilities
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt  

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica password"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Hash password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea JWT token
    
    Args:
        data: Dizionario con i dati da inserire nel token (es. {"sub": "7", "email": "...", "role": "..."})
        expires_delta: Durata personalizzata del token (opzionale)
    
    Returns:
        Token JWT firmato come stringa
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica JWT token
    
    Args:
        token: Token JWT da decodificare
    
    Returns:
        Payload del token come dict, oppure None se invalido/scaduto
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    

    """
JWT Authentication Utilities
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt  

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica password"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Hash password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea JWT token
    
    Args:
        data: Dizionario con i dati da inserire nel token (es. {"sub": "7", "email": "...", "role": "..."})
        expires_delta: Durata personalizzata del token (opzionale)
    
    Returns:
        Token JWT firmato come stringa
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica JWT token
    
    Args:
        token: Token JWT da decodificare
    
    Returns:
        Payload del token come dict, oppure None se invalido/scaduto
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None



def verify_token_with_details(token: str) -> Dict[str, Any]:
    """
    Verifica la validità del token JWT e restituisce informazioni dettagliate
    
    Args:
        token: Token JWT da verificare
    
    Returns:
        Dizionario con:
        - valid (bool): True se il token è valido
        - payload (dict): Payload del token se valido
        - error (str): Messaggio di errore se non valido
        - expires_in (int): Secondi rimanenti prima della scadenza
        - expires_at (str): Timestamp ISO della scadenza
    """
    try:
        # Decodifica il token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verifica la scadenza
        exp_timestamp = payload.get('exp')
        if not exp_timestamp:
            return {
                'valid': False,
                'error': 'Token senza data di scadenza',
                'payload': None
            }
        
        current_timestamp = datetime.now(timezone.utc).timestamp()
        
        # Calcola il tempo rimanente
        time_remaining = exp_timestamp - current_timestamp
        
        if time_remaining <= 0:
            return {
                'valid': False,
                'error': 'Token scaduto',
                'payload': None
            }
        
        return {
            'valid': True,
            'payload': payload,
            'expires_in': int(time_remaining),
            'expires_at': datetime.fromtimestamp(exp_timestamp, tz=timezone.utc).isoformat()
        }
        
    except jwt.ExpiredSignatureError:
        return {
            'valid': False,
            'error': 'Token scaduto',
            'payload': None
        }
    except jwt.JWTClaimsError:
        return {
            'valid': False,
            'error': 'Claims del token non validi',
            'payload': None
        }
    except jwt.JWTError as e:
        return {
            'valid': False,
            'error': f'Token non valido: {str(e)}',
            'payload': None
        }
    except Exception as e:
        return {
            'valid': False,
            'error': f'Errore nella verifica del token: {str(e)}',
            'payload': None
        }