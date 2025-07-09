from .extentions import db
from .models import *
from typing import List, Optional, Dict, Any
from datetime import datetime

class FirestoreSession:
    """Helper class to mimic SQLAlchemy session operations for Firestore"""
    
    def add(self, model_instance):
        """Add a document to Firestore"""
        collection_ref = db.collection(model_instance.collection_name)
        doc_ref = collection_ref.add(model_instance.to_dict())
        return doc_ref
    
    def commit(self):
        """Firestore auto-commits, so this is a no-op"""
        pass
    
    def rollback(self):
        """Firestore doesn't support transactions in this context"""
        pass
    
    def query(self, model_class):
        """Return a query helper for the model"""
        return FirestoreQuery(model_class)

class FirestoreQuery:
    """Helper class to mimic SQLAlchemy query operations"""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.collection_ref = db.collection(model_class.collection_name)
        self._filters = []
        self._order_by = None
        self._limit_val = None
    
    def filter_by(self, **kwargs):
        """Add equality filters"""
        for key, value in kwargs.items():
            self._filters.append((key, '==', value))
        return self
    
    def filter(self, *conditions):
        """Add custom filter conditions"""
        # This would need more complex implementation for various operators
        return self
    
    def order_by(self, field, direction='ASCENDING'):
        """Add ordering"""
        self._order_by = (field, direction)
        return self
    
    def limit(self, count):
        """Limit results"""
        self._limit_val = count
        return self
    
    def first(self):
        """Get first result"""
        query = self.collection_ref
        
        # Apply filters
        for field, operator, value in self._filters:
            query = query.where(field, operator, value)
        
        # Apply ordering
        if self._order_by:
            field, direction = self._order_by
            query = query.order_by(field, direction=direction)
        
        # Get first document
        docs = query.limit(1).get()
        if docs:
            return self.model_class.from_dict(docs[0].to_dict())
        return None
    
    def all(self):
        """Get all results"""
        query = self.collection_ref
        
        # Apply filters
        for field, operator, value in self._filters:
            query = query.where(field, operator, value)
        
        # Apply ordering
        if self._order_by:
            field, direction = self._order_by
            query = query.order_by(field, direction=direction)
        
        # Apply limit
        if self._limit_val:
            query = query.limit(self._limit_val)
        
        docs = query.get()
        return [self.model_class.from_dict(doc.to_dict()) for doc in docs]
    
    def count(self):
        """Count documents"""
        query = self.collection_ref
        
        # Apply filters
        for field, operator, value in self._filters:
            query = query.where(field, operator, value)
        
        return len(query.get())

# Create a global session instance
session = FirestoreSession()