from app import db

class Test(db.Model):
    __tablename__ = 'dev_tests'

    id = db.Column(db.Integer, primary_key=True)
    config = db.Column(db.String())
    start = db.Column(db.String())
    end = db.Column(db.String())
    workers = db.Column(db.Integer())

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