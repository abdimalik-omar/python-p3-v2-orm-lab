from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:
    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year  # This will use the setter
        self.summary = summary  # This will use the setter
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Review instances."""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INT,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Review instances."""
        sql = "DROP TABLE IF EXISTS reviews;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of the new row.
        Save the object in local dictionary using table row's PK as dictionary key."""
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid  # Update with the new row's ID
            print(f"Inserted Review: {self.year}, {self.summary}, {self.employee_id} (ID: {self.id})")
        else:
            sql = """
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))

        CONN.commit()
        Review.all[self.id] = self  # Cache the object

    @classmethod
    def create(cls, year, summary, employee_id):
        """Create a new Review instance and save it to the database."""
        review = cls(year, summary, employee_id)
        review.save()  # Re-use the save method to persist it
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Returns a Review instance from the database row."""
        print(f"Attempting to create Review from row: {row}")  # Debugging row values
        if row[0] in cls.all:
            print(f"Found cached Review with ID {row[0]}")
            return cls.all[row[0]]

        # Create a new Review object from the database row
        review = cls(
            id=row[0],         # The ID from the row
            year=row[1],       # The year from the row
            summary=row[2],    # The summary from the row
            employee_id=row[3] # The employee_id from the row
        )
        cls.all[row[0]] = review
        print(f"Created new Review: ID={row[0]}, Year={row[1]}, Summary={row[2]}, Employee ID={row[3]}")
        return review


    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance by ID."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        """Update the current Review instance in the database."""
        if self.id:
            sql = """
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()

    def delete(self):
        """Delete the current Review instance from the database and remove it from the cache."""
        if self.id:
            sql = "DELETE FROM reviews WHERE id = ?"
            CURSOR.execute(sql, (self.id,))
            CONN.commit()
            del Review.all[self.id]  # Remove from cache
            self.id = None  # Reset the instance id

    @classmethod
    def get_all(cls):
        """Return a list of all Review instances."""
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Property methods
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer.")
        if value < 2000:
            raise ValueError("Year must be 2000 or greater.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not value or not value.strip():
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Check if the employee_id exists in the Employee table
        employee = Employee.find_by_id(value)
        if not employee:
            raise ValueError(f"Employee with ID {value} does not exist.")
        self._employee_id = value