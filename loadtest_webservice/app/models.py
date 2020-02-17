from app import db

class Test(db.Model):
    __tablename__ = 'dev_tests'

    id = db.Column(db.Integer, primary_key=True)
    config = db.Column(db.TIMESTAMP) # STRING
    start = db.Column(db.TIMESTAMP) # good
    end = db.Column(db.String()) # TIMESTAMP
    # Will come back to later
    # workers = db.Column(db.Integer()) 

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

class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer())
    time_sent = db.Column(db.TIMESTAMP)
    request_type = db.Column(db.String())
    request_length = db.Column(db.Integer())
    response_type = db.Column(db.String())
    response_length = db.Column(db.Integer())
    duration = db.Column(db.TIMESTAMP)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'time_sent': self.time_sent,
            'request_type': self.request_type,
            'request_length': self.request_length,
            'response_type': self.response_type,
            'response_length': self.response_length,
            'duration': self.duration
        }

class SystemMetric(db.Model):
    __tablename__ = 'system_metrics'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer())
    time = db.Column(db.TIMESTAMP)
    metric_type = db.Column(db.String())
    metric_value = db.Column(db.BigInteger)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'time': self.time,
            'metric type': self.metric_type,
            'metric value': self.metric_value
        }
