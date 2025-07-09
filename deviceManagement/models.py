from datetime import datetime
from typing import Optional, Dict, Any
import random
import string

class FirestoreModel:
    """Base class for Firestore document models"""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """Convert model to dictionary for Firestore"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                # Convert datetime objects to timestamp
                if isinstance(value, datetime):
                    result[key] = value
                else:
                    result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model instance from Firestore document data"""
        return cls(**data)

class Firmware(FirestoreModel):
    collection_name = 'firmware'
    
    def __init__(self, firmwareVersion=None, firmware_string=None, firmware_string_hex=None, 
                 firmware_string_bootloader=None, firmware_type='beta', description=None, 
                 change1=None, change2=None, change3=None, change4=None, change5=None, 
                 change6=None, change7=None, change8=None, change9=None, change10=None, 
                 created_at=None, updated_at=None, **kwargs):
        self.firmwareVersion = firmwareVersion
        self.firmware_string = firmware_string
        self.firmware_string_hex = firmware_string_hex
        self.firmware_string_bootloader = firmware_string_bootloader
        self.firmware_type = firmware_type  # 'stable', 'beta', 'deprecated', 'legacy'
        self.description = description
        self.change1 = change1
        self.change2 = change2
        self.change3 = change3
        self.change4 = change4
        self.change5 = change5
        self.change6 = change6
        self.change7 = change7
        self.change8 = change8
        self.change9 = change9
        self.change10 = change10
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        
        # Set any additional fields from kwargs
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

class Profiles(FirestoreModel):
    collection_name = 'profiles'
    
    def __init__(self, name=None, description=None, 
                 field1=None, field2=None, field3=None, field4=None, field5=None,
                 field6=None, field7=None, field8=None, field9=None, field10=None,
                 field11=None, field12=None, field13=None, field14=None, field15=None,
                 metadata1=None, metadata2=None, metadata3=None, metadata4=None, metadata5=None,
                 metadata6=None, metadata7=None, metadata8=None, metadata9=None, metadata10=None,
                 metadata11=None, metadata12=None, metadata13=None, metadata14=None, metadata15=None,
                 config1=None, config2=None, config3=None, config4=None, config5=None,
                 config6=None, config7=None, config8=None, config9=None, config10=None,
                 created_at=None, **kwargs):
        self.name = name
        self.description = description
        
        # Field attributes
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3
        self.field4 = field4
        self.field5 = field5
        self.field6 = field6
        self.field7 = field7
        self.field8 = field8
        self.field9 = field9
        self.field10 = field10
        self.field11 = field11
        self.field12 = field12
        self.field13 = field13
        self.field14 = field14
        self.field15 = field15
        
        # Metadata attributes
        self.metadata1 = metadata1
        self.metadata2 = metadata2
        self.metadata3 = metadata3
        self.metadata4 = metadata4
        self.metadata5 = metadata5
        self.metadata6 = metadata6
        self.metadata7 = metadata7
        self.metadata8 = metadata8
        self.metadata9 = metadata9
        self.metadata10 = metadata10
        self.metadata11 = metadata11
        self.metadata12 = metadata12
        self.metadata13 = metadata13
        self.metadata14 = metadata14
        self.metadata15 = metadata15
        
        # Config attributes
        self.config1 = config1
        self.config2 = config2
        self.config3 = config3
        self.config4 = config4
        self.config5 = config5
        self.config6 = config6
        self.config7 = config7
        self.config8 = config8
        self.config9 = config9
        self.config10 = config10
        
        self.created_at = created_at or datetime.now()
        
        # Set any additional fields from kwargs
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

class Devices(FirestoreModel):
    collection_name = 'devices'
    
    def __init__(self, name=None, readkey=None, writekey=None, deviceID=None, networkID=None,
                 currentFirmwareVersion=None, previousFirmwareVersion=None, targetFirmwareVersion=None,
                 fileDownloadState=False, profile=None, firmwareDownloadState='updated',
                 created_at=None, updated_at=None, **kwargs):
        self.name = name
        self.readkey = readkey or self._generate_key()
        self.writekey = writekey or self._generate_key()
        self.deviceID = deviceID
        self.networkID = networkID
        # In Firestore, these will store document IDs or references instead of foreign keys
        self.currentFirmwareVersion = currentFirmwareVersion
        self.previousFirmwareVersion = previousFirmwareVersion
        self.targetFirmwareVersion = targetFirmwareVersion
        self.fileDownloadState = fileDownloadState
        self.profile = profile
        self.firmwareDownloadState = firmwareDownloadState  # 'updated', 'pending', 'failed'
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        
        # Set any additional fields from kwargs
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def _generate_key():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

class DeviceData(FirestoreModel):
    collection_name = 'devicedata'
    
    def __init__(self, entryID=None, deviceID=None, created_at=None,
                 field1=None, field2=None, field3=None, field4=None, field5=None,
                 field6=None, field7=None, field8=None, field9=None, field10=None,
                 field11=None, field12=None, field13=None, field14=None, field15=None,
                 **kwargs):
        self.entryID = entryID
        self.deviceID = deviceID
        self.created_at = created_at or datetime.now()
        
        # Field attributes
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3
        self.field4 = field4
        self.field5 = field5
        self.field6 = field6
        self.field7 = field7
        self.field8 = field8
        self.field9 = field9
        self.field10 = field10
        self.field11 = field11
        self.field12 = field12
        self.field13 = field13
        self.field14 = field14
        self.field15 = field15
        
        # Set any additional fields from kwargs
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def get_next_entry_id(deviceID):
        """Get the next available entry ID for a specific device."""
        from .extentions import db
        # Query Firestore to get the highest entryID for this device
        docs = db.collection('devicedata').where('deviceID', '==', deviceID).order_by('entryID', direction='DESCENDING').limit(1).get()
        if docs:
            return docs[0].to_dict().get('entryID', 0) + 1
        return 1

class MetadataValues(FirestoreModel):
    collection_name = 'metadatavalues'
    
    def __init__(self, deviceID=None, created_at=None,
                 metadata1=None, metadata2=None, metadata3=None, metadata4=None, metadata5=None,
                 metadata6=None, metadata7=None, metadata8=None, metadata9=None, metadata10=None,
                 metadata11=None, metadata12=None, metadata13=None, metadata14=None, metadata15=None,
                 **kwargs):
        self.deviceID = deviceID
        self.created_at = created_at or datetime.now()
        
        # Metadata attributes
        self.metadata1 = metadata1
        self.metadata2 = metadata2
        self.metadata3 = metadata3
        self.metadata4 = metadata4
        self.metadata5 = metadata5
        self.metadata6 = metadata6
        self.metadata7 = metadata7
        self.metadata8 = metadata8
        self.metadata9 = metadata9
        self.metadata10 = metadata10
        self.metadata11 = metadata11
        self.metadata12 = metadata12
        self.metadata13 = metadata13
        self.metadata14 = metadata14
        self.metadata15 = metadata15
        
        # Set any additional fields from kwargs
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

class ConfigValues(FirestoreModel):
    collection_name = 'configvalues'
    
    def __init__(self, deviceID=None, created_at=None,
                 config1=None, config2=None, config3=None, config4=None, config5=None,
                 config6=None, config7=None, config8=None, config9=None, config10=None,
                 **kwargs):
        self.deviceID = deviceID
        self.created_at = created_at or datetime.now()
        
        # Config attributes
        self.config1 = config1
        self.config2 = config2
        self.config3 = config3
        self.config4 = config4
        self.config5 = config5
        self.config6 = config6
        self.config7 = config7
        self.config8 = config8
        self.config9 = config9
        self.config10 = config10
        
        # Set any additional fields from kwargs
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

class DeviceFiles(FirestoreModel):
    collection_name = 'devicefiles'
    
    def __init__(self, deviceID=None, file=None, created_at=None, **kwargs):
        self.deviceID = deviceID
        self.file = file
        self.created_at = created_at or datetime.now()
        
        # Set any additional fields from kwargs
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)