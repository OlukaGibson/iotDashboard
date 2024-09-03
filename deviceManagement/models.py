from .extentions import db

class Firmware(db.Model):
    __tablename__ = 'firmware'
    id = db.Column(db.Integer, primary_key=True)
    firmwareVersion = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, firmwareVersion, description):
        self.firmwareVersion = firmwareVersion
        self.description = description

class Devices(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    readkey = db.Column(db.String(100), unique=True)
    deviceID = db.Column(db.Integer, unique=True)
    writekey = db.Column(db.String(100), unique=True)
    currentFirmwareVersion = db.Column(db.Integer, db.ForeignKey('firmware.id'), default=None)
    previousFirmwareVersion = db.Column(db.Integer, db.ForeignKey('firmware.id'), default=None)
    file_download_state = db.Column(db.String(100), default=None)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
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

    def __init__(self, name, readkey, writekey, deviceID, currentFirmwareVersion, updateFirmwareVersion, file_download_state ,field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, field12, field13, field14, field15, field16, field17, field18, field19, field20):
        self.name = name
        self.readkey = readkey
        self.writekey = writekey
        self.deviceID = deviceID
        self.currentFirmwareVersion = currentFirmwareVersion
        self.updateFirmwareVersion = updateFirmwareVersion
        self.file_download_state = file_download_state
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

class MetadataValues(db.Model):
    __tablename__ = 'metadatavalues'
    id = db.Column(db.Integer, primary_key=True)
    deviceID = db.Column(db.Integer, db.ForeignKey('devices.deviceID'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
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

    def __init__(self, deviceID, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, field12, field13, field14, field15, field16, field17, field18, field19, field20):
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
