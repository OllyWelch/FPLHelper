from app import create_app, db, cli
from app.models import User, Post, Thread, UserTransfer, Notification, PostLike

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Thread': Thread, 'PostLike': PostLike, 'UserTransfer': UserTransfer,
            'Notification': Notification}
