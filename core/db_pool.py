import os
import logging
import threading
from contextlib import contextmanager
from pathlib import Path
import psycopg2
from psycopg2.pool import SimpleConnectionPool, PoolError
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from the project root .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

DATABASE_URL = os.getenv('DATABASE_URL')

# Pool configurations
MIN_CONN = 1
MAX_CONN = 10

# Global connection pool and lock for thread safety (since SimpleConnectionPool is not thread-safe)
_pool = None
_pool_lock = threading.Lock()

def init_pool():
    """Initializes the SimpleConnectionPool globally."""
    global _pool
    if _pool is not None:
        return _pool

    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable is missing. Connection pool cannot be initialized.")
        return None

    try:
        # SimpleConnectionPool is not thread-safe. We use _pool_lock to serialize
        # access to its initialization and all subsequent getconn/putconn calls.
        with _pool_lock:
            if _pool is None:
                _pool = SimpleConnectionPool(minconn=MIN_CONN, maxconn=MAX_CONN, dsn=DATABASE_URL)
                logger.info(f"psycopg2 SimpleConnectionPool initialized successfully (min={MIN_CONN}, max={MAX_CONN}).")
        return _pool
    except Exception as e:
        logger.exception(f"Failed to initialize psycopg2 connection pool: {e}")
        return None

def get_db():
    """
    Retrieves a PostgreSQL connection from the pool and runs a quick sanity check (SELECT 1).
    If the pool fails, is not initialized, or is exhausted, falls back to a direct, ad-hoc psycopg2 connection.
    
    Returns:
        tuple: (connection, is_fallback)
        where `connection` is the psycopg2 connection object, and `is_fallback` is a boolean
        indicating whether this is a direct fallback connection (True) or a pooled connection (False).
    """
    global _pool
    if _pool is None:
        init_pool()

    conn = None
    is_fallback = False

    # 1. Attempt to retrieve and check a connection from the pool
    if _pool is not None:
        try:
            with _pool_lock:
                conn = _pool.getconn()
            
            # Sanity check: Run a fast lightweight query to verify the connection is active
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
            
            logger.debug("Successfully fetched healthy connection from pool.")
            return conn, False
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as conn_err:
            logger.warning(f"Connection from pool failed sanity check: {conn_err}. Releasing and falling back.")
            if conn:
                try:
                    with _pool_lock:
                        _pool.putconn(conn, close=True)
                except Exception:
                    pass
            conn = None
        except PoolError as pool_err:
            logger.warning(f"Connection pool exhausted or not ready: {pool_err}. Falling back to direct connection.")
            conn = None
        except Exception as err:
            logger.warning(f"Unexpected error when getting connection from pool: {err}. Falling back.")
            conn = None

    # 2. Fallback to direct ad-hoc connection
    if conn is None:
        if not DATABASE_URL:
            raise ValueError(
                "DATABASE_URL is not set, and the connection pool is not available. "
                "Please configure DATABASE_URL in your .env file."
            )
        try:
            logger.info("Establishing direct, ad-hoc psycopg2 connection (fallback)...")
            conn = psycopg2.connect(DATABASE_URL)
            is_fallback = True
        except Exception as fallback_err:
            logger.critical(f"Direct ad-hoc database connection fallback failed: {fallback_err}")
            raise fallback_err

    return conn, is_fallback

def return_db(conn, is_fallback=False):
    """
    Safely returns a database connection to the pool, or closes it if it was a fallback connection.
    
    Args:
        conn: The psycopg2 connection object to return or close.
        is_fallback (bool): Explicitly indicates whether this connection was a direct fallback connection.
                            If not passed, it will try to return to the pool, and if the pool rejects it
                            (meaning it's not a pooled connection), it will close it directly.
    """
    global _pool
    if conn is None:
        return

    if is_fallback:
        try:
            conn.close()
            logger.info("Closed direct fallback connection successfully.")
        except Exception as e:
            logger.error(f"Error while closing fallback connection: {e}")
        return

    # Try returning it to the pool
    if _pool is not None:
        try:
            with _pool_lock:
                _pool.putconn(conn)
            logger.debug("Returned connection to the pool successfully.")
            return
        except PoolError:
            # PoolError indicates connection is not from this pool. Let's close it directly.
            logger.debug("Connection not recognized by the pool. Closing directly.")
        except Exception as e:
            logger.error(f"Error while returning connection to pool: {e}")

    # Default fallback: Close connection directly
    try:
        conn.close()
        logger.info("Closed unrecognized database connection directly.")
    except Exception as e:
        logger.error(f"Error while closing unrecognized connection: {e}")

@contextmanager
def db_session():
    """
    A context manager that yields a database connection.
    Guarantees that the connection is safely returned to the pool or closed.
    
    Usage:
        with db_session() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT ...")
                results = cursor.fetchall()
    """
    conn, is_fallback = get_db()
    try:
        yield conn
    finally:
        return_db(conn, is_fallback)
