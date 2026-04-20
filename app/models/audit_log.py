from app.extensions import db
from datetime import datetime


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'))
    action      = db.Column(db.String(50))       # create / update / delete / login / logout
    entity_type = db.Column(db.String(50))        # product / order / user ...
    entity_id   = db.Column(db.Integer)
    description = db.Column(db.Text)
    ip_address  = db.Column(db.String(45))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditLog {self.action} {self.entity_type}>'


def log_action(user_id, action, entity_type=None, entity_id=None, description=None, ip=None):
    """Helper để ghi log nhanh"""
    from app.extensions import db
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip,
    )
    db.session.add(entry)
    # Không commit ở đây — để người gọi tự commit
