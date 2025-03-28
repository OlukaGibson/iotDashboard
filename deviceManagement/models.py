from .extentions import db

class Firmware(db.Model):
    __tablename__ = 'firmware'
    id = db.Column(db.Integer, primary_key=True)
    firmwareVersion = db.Column(db.String(100), unique=True)
    firmware_string = db.Column(db.String(100), nullable=False)
    firmware_string_hex = db.Column(db.String(100), default=None, nullable=True)
    firmware_string_bootloader = db.Column(db.String(100), default=None, nullable=True)
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


    def __init__(self, firmwareVersion,firmware_string, firmware_string_hex, firmware_string_bootloader, description, change1, change2, change3, change4, change5, change6, change7, change8, change9, change10):
        self.firmwareVersion = firmwareVersion
        self.firmware_string = firmware_string
        self.firmware_string_hex = firmware_string_hex
        self.firmware_string_bootloader = firmware_string_bootloader
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
    field1_mark = db.Column(db.Boolean, default=False)
    field2 = db.Column(db.String(100), default=None)
    field2_mark = db.Column(db.Boolean, default=False)
    field3 = db.Column(db.String(100), default=None)
    field3_mark = db.Column(db.Boolean, default=False)
    field4 = db.Column(db.String(100), default=None)
    field4_mark = db.Column(db.Boolean, default=False)
    field5 = db.Column(db.String(100), default=None)
    field5_mark = db.Column(db.Boolean, default=False)
    field6 = db.Column(db.String(100), default=None)
    field6_mark = db.Column(db.Boolean, default=False)
    field7 = db.Column(db.String(100), default=None)
    field7_mark = db.Column(db.Boolean, default=False)
    field8 = db.Column(db.String(100), default=None)
    field8_mark = db.Column(db.Boolean, default=False)
    field9 = db.Column(db.String(100), default=None)
    field9_mark = db.Column(db.Boolean, default=False)
    field10 = db.Column(db.String(100), default=None)
    field10_mark = db.Column(db.Boolean, default=False)
    field11 = db.Column(db.String(100), default=None)
    field11_mark = db.Column(db.Boolean, default=False)
    field12 = db.Column(db.String(100), default=None)
    field12_mark = db.Column(db.Boolean, default=False)
    field13 = db.Column(db.String(100), default=None)
    field13_mark = db.Column(db.Boolean, default=False)
    field14 = db.Column(db.String(100), default=None)
    field14_mark = db.Column(db.Boolean, default=False)
    field15 = db.Column(db.String(100), default=None)
    field15_mark = db.Column(db.Boolean, default=False)
    field16 = db.Column(db.String(100), default=None)
    field16_mark = db.Column(db.Boolean, default=False)
    field17 = db.Column(db.String(100), default=None)
    field17_mark = db.Column(db.Boolean, default=False)
    field18 = db.Column(db.String(100), default=None)
    field18_mark = db.Column(db.Boolean, default=False)
    field19 = db.Column(db.String(100), default=None)
    field19_mark = db.Column(db.Boolean, default=False)
    field20 = db.Column(db.String(100), default=None)
    field20_mark = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, name, description, field1, field1_mark, field2, field2_mark, field3, field3_mark, field4, field4_mark, field5, field5_mark, field6, field6_mark, field7, field7_mark, field8, field8_mark, field9, field9_mark, field10, field10_mark, field11, field11_mark, field12, field12_mark, field13, field13_mark, field14, field14_mark, field15, field15_mark, field16, field16_mark, field17, field17_mark, field18, field18_mark, field19, field19_mark, field20, field20_mark):
        self.name = name
        self.description = description
        self.field1 = field1
        self.field1_mark = field1_mark
        self.field2 = field2
        self.field2_mark = field2_mark
        self.field3 = field3
        self.field3_mark = field3_mark
        self.field4 = field4
        self.field4_mark = field4_mark
        self.field5 = field5
        self.field5_mark = field5_mark
        self.field6 = field6
        self.field6_mark = field6_mark
        self.field7 = field7
        self.field7_mark = field7_mark
        self.field8 = field8
        self.field8_mark = field8_mark
        self.field9 = field9
        self.field9_mark = field9_mark
        self.field10 = field10
        self.field10_mark = field10_mark
        self.field11 = field11
        self.field11_mark = field11_mark
        self.field12 = field12
        self.field12_mark = field12_mark
        self.field13 = field13
        self.field13_mark = field13_mark
        self.field14 = field14
        self.field14_mark = field14_mark
        self.field15 = field15
        self.field15_mark = field15_mark
        self.field16 = field16
        self.field16_mark = field16_mark
        self.field17 = field17
        self.field17_mark = field17_mark
        self.field18 = field18
        self.field18_mark = field18_mark
        self.field19 = field19
        self.field19_mark = field19_mark
        self.field20 = field20
        self.field20_mark = field20_mark

class Devices(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    readkey = db.Column(db.String(100), unique=True)
    deviceID = db.Column(db.Integer, unique=True)
    writekey = db.Column(db.String(100), unique=True)
    imsi = db.Column(db.String(100), default=None)
    imei = db.Column(db.String(100), default=None)
    currentFirmwareVersion = db.Column(db.Integer, db.ForeignKey('firmware.id'), default=None)
    previousFirmwareVersion = db.Column(db.Integer, db.ForeignKey('firmware.id'), default=None)
    targetFirmwareVersion = db.Column(db.Integer, db.ForeignKey('firmware.id'), default=None)
    fileDownloadState = db.Column(db.Boolean, default=False)
    profile = db.Column(db.Integer, db.ForeignKey('profiles.id'), default=None)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, name, readkey, writekey, deviceID,  imsi, imei, profile,currentFirmwareVersion, previousFirmwareVersion, targetFirmwareVersion, fileDownloadState ):
        self.name = name
        self.readkey = readkey
        self.writekey = writekey
        self.deviceID = deviceID
        self.imsi = imsi
        self.imei = imei
        self.profile = profile
        self.currentFirmwareVersion = currentFirmwareVersion
        self.previousFirmwareVersion = previousFirmwareVersion
        self.targetFirmwareVersion = targetFirmwareVersion
        self.fileDownloadState = fileDownloadState

class MetadataValues(db.Model):
    __tablename__ = 'metadatavalues'
    id = db.Column(db.Integer, primary_key=True)
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
    field16 = db.Column(db.String(100), default=None)
    field17 = db.Column(db.String(100), default=None)
    field18 = db.Column(db.String(100), default=None)
    field19 = db.Column(db.String(100), default=None)
    field20 = db.Column(db.String(100), default=None)

    def __init__(self, created_at, deviceID, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, field12, field13, field14, field15, field16, field17, field18, field19, field20):
        self.created_at = created_at
        self.deviceID = deviceID
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
        self.field16 = field16
        self.field17 = field17
        self.field18 = field18
        self.field19 = field19
        self.field20 = field20

class DeviceFiles(db.Model):
    __tablename__ = 'devicefiles'
    id = db.Column(db.Integer, primary_key=True)
    deviceID = db.Column(db.Integer, db.ForeignKey('devices.deviceID'))
    file = db.Column(db.String(100), default=None, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, deviceID, file):
        self.deviceID = deviceID
        self.file = file
