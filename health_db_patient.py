from pymodm import MongoModel, fields, EmbeddedMongoModel


class CPAP_Result(EmbeddedMongoModel):
    """ Database Record for CPAP_result

    This class inherits from EmbeddedMongoModel class of pymodm and encodes the
    the results data for the Patient MongoModel Class

    The "mrn" field is an integer and set-up as the primary key.  The "name"
    fields is CharFields (strings) to contain its contents. The "roomNumm"
    field is IntegerField to contain its content. The "breathingRate" field is
    a FloatField to contain its respective content. The "timestanp" field is a
    CharField to hold its content. The "apneaCount" field is an IntegerField to
    whold its content. Finally, "flowImg" is set up as a ImageField to hold its
    content.
    """

    timeStamp = fields.DateTimeField()
    breathingRate = fields.FloatField()
    apneaCount = fields.IntegerField()
    flowImg = fields.CharField()


class Patient(MongoModel):
    """ Database record for a patient

    This class inherits from the MongoModel class of pymodm and contains the
    data for a single patient and allows this data to be saved and retrieved
    from a MongoDB database.

    The "mrn" field is an integer and set-up as the primary key.  The "name"
    fields is CharFields (strings) to contain its contents. The "roomNumm"
    field is IntegerField to contain its content. The "pressure"
    field is FloatField to contain its content. Finally, "results" is set up
    as a EmbeddedDocumentListField to hold a list of the CPAP_Result objects
    """

    mrn = fields.IntegerField(primary_key=True)
    roomNum = fields.IntegerField()
    name = fields.CharField(blank=True)
    pressure = fields.IntegerField(blank=True)
    results = fields.EmbeddedDocumentListField(CPAP_Result)
    registered_timeStamp = fields.DateTimeField()
