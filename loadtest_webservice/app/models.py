from app import db, ma

class Test(db.Model):
    __tablename__ = 'loadtest_tests'

    # These fields are subject to change depending
    # on the final test config implementation
    id = db.Column(db.Integer, primary_key=True)
    config = db.Column(db.String())
    start = db.Column(db.TIMESTAMP)
    end = db.Column(db.TIMESTAMP)
    workers = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'config': self.config,
            'start': self.start,
            'end':self.end,
            'workers':self.workers
        }
class TestSchema(ma.ModelSchema):
    class Meta:
        model = Test


class Request(db.Model):
    __tablename__ = 'loadtest_requests'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer)
    time_sent = db.Column(db.TIMESTAMP)
    request_type = db.Column(db.String())
    request_length = db.Column(db.Integer)
    response_type = db.Column(db.String())
    response_length = db.Column(db.Integer)
    duration = db.Column(db.Float)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'test_id': self.test_id,
            'time_sent': self.time_sent,
            'request_type': self.request_type,
            'request_length': self.request_length,
            'response_type': self.response_type,
            'response_length': self.response_length,
            'duration': self.duration
        }

class RequestSchema(ma.ModelSchema):
    class Meta:
        model = Request

class SystemMetric(db.Model):
    __tablename__ = 'loadtest_metrics'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer)
    time = db.Column(db.TIMESTAMP)
    metric_type = db.Column(db.String())
    metric_value = db.Column(db.Float)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'test_id': self.test_id,
            'time': self.time,
            'metric_type': self.metric_type,
            'metric_value': self.metric_value
        }

class SystemMetricSchema(ma.ModelSchema):
    class Meta:
        model = SystemMetric