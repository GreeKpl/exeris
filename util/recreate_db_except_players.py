from exeris.app import app, db

if __name__ == "__main__":
    with app.app_context():
        tables_to_remove = [table.name for table in db.metadata.tables.values() if table.name != "players"]
        print("DROPPING TABLES: ", tables_to_remove)
        db.session.execute("DROP TABLE {}".format(", ".join(tables_to_remove)))
        db.session.commit()
        db.create_all()
