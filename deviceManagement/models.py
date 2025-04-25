from .extentions import db
from sqlalchemy import Enum

class Firmware(db.Model):
    __tablename__ = 'firmware'
    id = db.Column(db.Integer, primary_key=True)
    firmwareVersion = db.Column(db.String(100), unique=True)
    firmware_string = db.Column(db.String(100), nullable=False)
    firmware_string_hex = db.Column(db.String(100), default=None, nullable=True)
    firmware_string_bootloader = db.Column(db.String(100), default=None, nullable=True)
    firmware_type = db.Column(Enum('stable', 'beta', 'deprecated', 'legacy', name='firmware_type_enum'), nullable=True, default='beta')
    description = db.Column(db.String(100), default=None, nullable=True)
    # documentation = db.Column(db.String(100), default=None)
    # documentationLink = db.Column(db.String(100), default=None)
    change1 = db.Column(db.String(100), default=None)
    change2 = db.Column(db.String(100), default=None)
    change3 = db.Column(db.String(100), default=None)
    change4 = db.Column(db.String(100), default=None)
    change5 = db.Column(db.String(100), default=None)
    change6 = db.Column(db.String(100), default=None)
    change7 = db.Column(db.String(100), default=None)
    change8 = db.Column(db.String(100), default=None)
    change9 = db.Column(db.String(100), default=None)
    change10 = db.Column(db.String(100), default=None)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())    
    created_at = db.Column(db.DateTime, server_default=db.func.now())


    def __init__(self, firmwareVersion,firmware_string, firmware_string_hex, firmware_string_bootloader, firmware_type, description, change1, change2, change3, change4, change5, change6, change7, change8, change9, change10):
        self.firmwareVersion = firmwareVersion
        self.firmware_string = firmware_string
        self.firmware_string_hex = firmware_string_hex
        self.firmware_string_bootloader = firmware_string_bootloader
        self.firmware_type = firmware_type
        self.description = description
        # self.documentation = documentation
        # self.documentationLink = documentationLink
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

class Profiles(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(100), default=None)
    field1 = db.Column(db.String(100), default=None)
    field2 = db.Column(db.String(100), default=None)
    field3 = db.Column(db.String(100), default=None)
    field4 = db.Column(db.String(100), default=None)
    field5 = db.Column(db.String(100), default=None)
    field6 = db.Column(db.String(100), default=None)
    field7 = db.Column(db.String(100), default=None)
    field8 = db.Column(db.String(100), default=None)
    field9 = db.Column(db.String(100), default=None)
    field10 = db.Column(db.String(100), default=None)
    field11 = db.Column(db.String(100), default=None)
    field12 = db.Column(db.String(100), default=None)
    field13 = db.Column(db.String(100), default=None)
    field14 = db.Column(db.String(100), default=None)
    field15 = db.Column(db.String(100), default=None)
    metadata1 = db.Column(db.String(100), default=None)
    metadata2 = db.Column(db.String(100), default=None)
    metadata3 = db.Column(db.String(100), default=None)
    metadata4 = db.Column(db.String(100), default=None)
    metadata5 = db.Column(db.String(100), default=None)
    metadata6 = db.Column(db.String(100), default=None)
    metadata7 = db.Column(db.String(100), default=None)
    metadata8 = db.Column(db.String(100), default=None)
    metadata9 = db.Column(db.String(100), default=None)
    metadata10 = db.Column(db.String(100), default=None)
    metadata11 = db.Column(db.String(100), default=None)
    metadata12 = db.Column(db.String(100), default=None)
    metadata13 = db.Column(db.String(100), default=None)
    metadata14 = db.Column(db.String(100), default=None)
    metadata15 = db.Column(db.String(100), default=None)
    config1 = db.Column(db.String(100), default=None)
    config2 = db.Column(db.String(100), default=None)
    config3 = db.Column(db.String(100), default=None)
    config4 = db.Column(db.String(100), default=None)
    config5 = db.Column(db.String(100), default=None)
    config6 = db.Column(db.String(100), default=None)
    config7 = db.Column(db.String(100), default=None)
    config8 = db.Column(db.String(100), default=None)
    config9 = db.Column(db.String(100), default=None)
    config10 = db.Column(db.String(100), default=None)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, name, description, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, field12, field13, field14, field15, config1, config2, config3, config4, config5, config6, config7, config8, config9, config10, metadata1, metadata2, metadata3, metadata4, metadata5, metadata6, metadata7, metadata8, metadata9, metadata10, metadata11, metadata12, metadata13, metadata14, metadata15):
        self.name = name
        self.description = description
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

class Devices(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    readkey = db.Column(db.String(100), unique=True)
    deviceID = db.Column(db.Integer, unique=True)
    writekey = db.Column(db.String(100), unique=True)
    networkID = db.Column(db.String(100), default=None)
    currentFirmwareVersion = db.Column(db.Integer, db.ForeignKey('firmware.id'), default=None)
    previousFirmwareVersion = db.Column(db.Integer, db.ForeignKey('firmware.id'), default=None)
    targetFirmwareVersion = db.Column(db.Integer, db.ForeignKey('firmware.id'), default=None)
    fileDownloadState = db.Column(db.Boolean, default=False)
    profile = db.Column(db.Integer, db.ForeignKey('profiles.id'), default=None)
    firmwareDownloadState = db.Column(Enum('updated', 'pending', 'failed', name='firmware_download_state_enum'), nullable=True, default='updated')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, name, readkey, writekey, deviceID,  networkID, profile,currentFirmwareVersion, previousFirmwareVersion, targetFirmwareVersion, fileDownloadState, firmwareDownloadState ):
        self.name = name
        self.readkey = readkey
        self.writekey = writekey
        self.deviceID = deviceID
        self.networkID = networkID
        self.profile = profile
        self.currentFirmwareVersion = currentFirmwareVersion
        self.previousFirmwareVersion = previousFirmwareVersion
        self.targetFirmwareVersion = targetFirmwareVersion
        self.fileDownloadState = fileDownloadState
        self.firmwareDownloadState = firmwareDownloadState

class DeviceData(db.Model):
    __tablename__ = 'devicedata'
    id = db.Column(db.Integer, primary_key=True)
    entryID = db.Column(db.Integer)
    deviceID = db.Column(db.Integer, db.ForeignKey('devices.deviceID'))
    created_at = db.Column(db.DateTime)  # Removed server_default
    field1 = db.Column(db.String(100), default=None)
    field2 = db.Column(db.String(100), default=None)
    field3 = db.Column(db.String(100), default=None)
    field4 = db.Column(db.String(100), default=None)
    field5 = db.Column(db.String(100), default=None)
    field6 = db.Column(db.String(100), default=None)
    field7 = db.Column(db.String(100), default=None)
    field8 = db.Column(db.String(100), default=None)
    field9 = db.Column(db.String(100), default=None)
    field10 = db.Column(db.String(100), default=None)
    field11 = db.Column(db.String(100), default=None)
    field12 = db.Column(db.String(100), default=None)
    field13 = db.Column(db.String(100), default=None)
    field14 = db.Column(db.String(100), default=None)
    field15 = db.Column(db.String(100), default=None)

    __table_args__ = (db.UniqueConstraint('deviceID', 'entryID', name='unique_device_entry'),)

    @classmethod
    def get_next_entry_id(cls, device_id):
        """Get the next available entry ID for a specific device."""
        max_entry = db.session.query(db.func.max(cls.entryID)).filter(cls.deviceID == device_id).scalar()
        return 1 if max_entry is None else max_entry + 1

    def __init__(self, created_at, deviceID, entryID, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, field12, field13, field14, field15):
        self.created_at = created_at
        self.deviceID = deviceID
        self.entryID = entryID
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

class MetadataValues(db.Model):
    __tablename__ = 'metadatavalues'
    id = db.Column(db.Integer, primary_key=True)
    deviceID = db.Column(db.Integer, db.ForeignKey('devices.deviceID'))
    created_at = db.Column(db.DateTime)
    metadata1 = db.Column(db.String(100), default=None)
    metadata2 = db.Column(db.String(100), default=None)
    metadata3 = db.Column(db.String(100), default=None)
    metadata4 = db.Column(db.String(100), default=None)
    metadata5 = db.Column(db.String(100), default=None)
    metadata6 = db.Column(db.String(100), default=None)
    metadata7 = db.Column(db.String(100), default=None)
    metadata8 = db.Column(db.String(100), default=None)
    metadata9 = db.Column(db.String(100), default=None)
    metadata10 = db.Column(db.String(100), default=None)
    metadata11 = db.Column(db.String(100), default=None)
    metadata12 = db.Column(db.String(100), default=None)
    metadata13 = db.Column(db.String(100), default=None)
    metadata14 = db.Column(db.String(100), default=None)
    metadata15 = db.Column(db.String(100), default=None)

    def __init__(self, created_at, deviceID, metadata1, metadata2, metadata3, metadata4, metadata5, metadata6, metadata7, metadata8, metadata9, metadata10, metadata11, metadata12, metadata13, metadata14, metadata15):
        self.created_at = created_at
        self.deviceID = deviceID
        self.metadata1 = metadata1
        self.metadata2 = metadata2
        self.metadata3 = metadata3
        self.metadata4 = metadata4
        self.metadata5 = metadata5
        self.metadata6 = metadata6
        self.metadata7 = metadata7
        self.metadata8 = metadata8
        self.metadata9 =  metadata9
        self.metadata10 = metadata10
        self.metadata11 = metadata11
        self.metadata12 = metadata12
        self.metadata13 = metadata13
        self.metadata14 = metadata14
        self.metadata15 = metadata15

class ConfigValues(db.Model):
    __tablename__ = 'configvalues'
    id = db.Column(db.Integer, primary_key=True)
    deviceID = db.Column(db.Integer, db.ForeignKey('devices.deviceID'))
    created_at = db.Column(db.DateTime)  
    config1 = db.Column(db.String(100), default=None)
    config2 = db.Column(db.String(100), default=None)
    config3 = db.Column(db.String(100), default=None)
    config4 = db.Column(db.String(100), default=None)
    config5 = db.Column(db.String(100), default=None)
    config6 = db.Column(db.String(100), default=None)
    config7 = db.Column(db.String(100), default=None)
    config8 = db.Column(db.String(100), default=None)
    config9 = db.Column(db.String(100), default=None)
    config10 = db.Column(db.String(100), default=None)

    def __init__(self, created_at, deviceID, config1, config2, config3, config4, config5, config6, config7, config8, config9, config10):
        self.created_at = created_at
        self.deviceID = deviceID
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

class DeviceFiles(db.Model):
    __tablename__ = 'devicefiles'
    id = db.Column(db.Integer, primary_key=True)
    deviceID = db.Column(db.Integer, db.ForeignKey('devices.deviceID'))
    file = db.Column(db.String(100), default=None, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, deviceID, file):
        self.deviceID = deviceID
        self.file = file
