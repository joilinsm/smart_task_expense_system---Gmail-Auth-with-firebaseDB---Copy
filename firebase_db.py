"""
Firebase Firestore Database Module
Enhanced wrapper for Firebase Firestore integration with SQLAlchemy-like interface
Supports full CRUD operations and query patterns
"""
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud.firestore import Client
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️ Firebase Admin SDK not installed. Install with: pip install firebase-admin")

class FirebaseDB:
    """
    Firebase Firestore Database wrapper
    Provides connection and comprehensive CRUD operations with SQLAlchemy-like interface
    
    Methods:
    - add(collection, data) - Create new document with auto ID
    - set(collection, doc_id, data) - Set document with specific ID
    - get(collection, doc_id) - Get single document
    - query(collection) - Query documents (returns QueryBuilder)
    - delete(collection, doc_id) - Delete document
    - update(collection, doc_id, data) - Update document fields
    - batch_write(operations) - Batch operations
    """
    _instance = None
    _db = None
    
    def __new__(cls):
        """Singleton pattern - only one Firebase connection"""
        if cls._instance is None:
            cls._instance = super(FirebaseDB, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase connection"""
        if not FIREBASE_AVAILABLE:
            raise ImportError("Firebase Admin SDK not installed. Run: pip install firebase-admin")
        
        if self._db is None:
            try:
                # Check if Firebase is already initialized
                firebase_admin.get_app()
            except ValueError:
                # Firebase not initialized, initialize it
                firebase_creds = self._get_firebase_credentials()
                
                if firebase_creds:
                    cred = credentials.Certificate(firebase_creds)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase initialized successfully!")
                else:
                    raise ValueError("Firebase credentials not configured. See .env setup instructions.")
            
            # Get Firestore client
            self._db = firestore.client()
    
    def add(self, collection, data):
        """
        Add document to collection with auto-generated ID
        Returns: (doc_id, doc_data)
        """
        try:
            doc_id = str(uuid.uuid4())
            self._db.collection(collection).document(doc_id).set(data)
            return doc_id, data
        except Exception as e:
            print(f"❌ Error adding to {collection}: {e}")
            raise
    
    def set(self, collection, doc_id, data, merge=False):
        """
        Set document with specific ID
        merge=True: update only specified fields
        merge=False: replace entire document
        """
        try:
            self._db.collection(collection).document(str(doc_id)).set(data, merge=merge)
            return True
        except Exception as e:
            print(f"❌ Error setting {collection}/{doc_id}: {e}")
            raise
    
    def get(self, collection, doc_id):
        """Get single document and return data"""
        try:
            doc = self._db.collection(collection).document(str(doc_id)).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id  # Add document ID to data
                return data
            return None
        except Exception as e:
            print(f"❌ Error getting {collection}/{doc_id}: {e}")
            raise
    
    def get_all(self, collection):
        """Get all documents from a collection"""
        try:
            docs = self._db.collection(collection).stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            return results
        except Exception as e:
            print(f"❌ Error getting all from {collection}: {e}")
            raise
    
    def query(self, collection):
        """
        Query builder for flexible querying
        Usage: db.query('tasks').where('user_id', '==', user_id).where('status', '==', 'Pending').get()
        """
        return QueryBuilder(self._db, collection)
    
    def delete(self, collection, doc_id):
        """Delete document"""
        try:
            self._db.collection(collection).document(str(doc_id)).delete()
            return True
        except Exception as e:
            print(f"❌ Error deleting {collection}/{doc_id}: {e}")
            raise
    
    def update(self, collection, doc_id, data):
        """Update specific fields in a document"""
        try:
            self._db.collection(collection).document(str(doc_id)).update(data)
            return True
        except Exception as e:
            print(f"❌ Error updating {collection}/{doc_id}: {e}")
            raise
    
    def batch_write(self, operations):
        """
        Batch write operations
        operations: list of dicts with 'type' (add/set/update/delete), 'collection', 'doc_id', 'data'
        """
        try:
            batch = self._db.batch()
            for op in operations:
                collection = op['collection']
                doc_id = str(op.get('doc_id', ''))
                
                if op['type'] == 'add':
                    batch.set(self._db.collection(collection).document(), op['data'])
                elif op['type'] == 'set':
                    batch.set(self._db.collection(collection).document(doc_id), op['data'])
                elif op['type'] == 'update':
                    batch.update(self._db.collection(collection).document(doc_id), op['data'])
                elif op['type'] == 'delete':
                    batch.delete(self._db.collection(collection).document(doc_id))
            
            batch.commit()
            return True
        except Exception as e:
            print(f"❌ Error in batch write: {e}")
            raise
    
    def collection_exists(self, collection):
        """Check if collection has any documents"""
        try:
            return len(self._db.collection(collection).limit(1).stream()) > 0
        except:
            return False
    
    @staticmethod
    def _get_firebase_credentials():
        """
        Get Firebase credentials from environment or JSON file
        Returns: Dictionary with Firebase credentials or None
        """
        # Try loading from environment variables
        env_config = {
            'type': os.getenv('FIREBASE_TYPE', 'service_account'),
            'project_id': os.getenv('FIREBASE_PROJECT_ID'),
            'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            'private_key': os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
            'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
            'client_id': os.getenv('FIREBASE_CLIENT_ID'),
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            'client_x509_cert_url': os.getenv('FIREBASE_CLIENT_X509_CERT_URL', '')
        }
        
        # Check if all required fields are present
        if all([env_config['project_id'], env_config['private_key'], env_config['client_email']]):
            return env_config
        
        # Try loading from JSON file
        json_path = os.getenv('FIREBASE_CREDENTIALS_FILE', 'firebase-credentials.json')
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)
        
        return None
    
    @property
    def db(self):
        """Get Firestore database instance"""
        if self._db is None:
            self.__init__()
        return self._db
    
    def collection(self, collection_name):
        """Get a collection reference"""
        return self.db.collection(collection_name)
    
    def close(self):
        """Close Firebase connection"""
        if self._db:
            # Firebase client doesn't need explicit close, but we can reset
            self._db = None


class QueryBuilder:
    """
    Query builder for Firebase Firestore
    Supports chaining where clauses, ordering, and limits
    
    Usage:
        results = db.query('tasks').where('user_id', '==', '123').where('status', '==', 'Pending').order_by('deadline').limit(10).get()
    """
    
    def __init__(self, firestore_client, collection_name):
        """Initialize query builder"""
        self.firestore_client = firestore_client
        self.collection_name = collection_name
        self.query = firestore_client.collection(collection_name)
        self.constraints = []
    
    def where(self, field, operator, value):
        """Add where clause to query"""
        self.query = self.query.where(field, operator, value)
        return self
    
    def order_by(self, field, direction='ASCENDING'):
        """Add ordering to query"""
        self.query = self.query.order_by(field, direction=direction)
        return self
    
    def limit(self, limit_count):
        """Limit number of results"""
        self.query = self.query.limit(limit_count)
        return self
    
    def get(self):
        """Execute query and return results"""
        try:
            docs = self.query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            return results
        except Exception as e:
            print(f"❌ Error in query: {e}")
            return []
    
    def first(self):
        """Get first result"""
        results = self.limit(1).get()
        return results[0] if results else None
    
    def count(self):
        """Get count of results (executes query)"""
        return len(self.get())


# Create global Firebase instance
firebase_db = FirebaseDB()

# Export for use in app
def get_firebase_db():
    """Get Firebase database instance"""
    return firebase_db.db
