class ReplicaRouter:
    """
    A router to control database operations for read/write splitting.

    - All write operations (INSERT, UPDATE, DELETE) go to the 'default' database (writer)
    - All read operations (SELECT) go to the 'replica' database (reader)
    - Migrations always use the 'default' database
    """

    def db_for_read(self, model, **hints):
        """
        Send read operations to the replica database.
        """
        return "replica"

    def db_for_write(self, model, **hints):
        """
        Send write operations to the default (writer) database.
        """
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the same database.
        Since both databases are replicas of each other, always allow.
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure migrations only run on the default (writer) database.
        """
        return db == "default"
