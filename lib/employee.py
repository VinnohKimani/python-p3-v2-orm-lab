from __init__ import CURSOR, CONN
from department import Department


class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Department ID: {self.department_id}>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str) and len(value):
            self._name = value
        else:
            raise ValueError("Name must be a non-empty string")

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if isinstance(value, str) and len(value):
            self._job_title = value
        else:
            raise ValueError("job_title must be a non-empty string")

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        if isinstance(value, int) and Department.find_by_id(value):
            self._department_id = value
        else:
            raise ValueError(
                "department_id must reference a department in the database"
            )

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CONN.commit()

    def save(self):
        CURSOR.execute(
            "INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)",
            (self.name, self.job_title, self.department_id),
        )
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        CURSOR.execute(
            "UPDATE employees SET name = ?, job_title = ?, department_id = ? WHERE id = ?",
            (self.name, self.job_title, self.department_id, self.id),
        )
        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM employees WHERE id = ?", (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    @classmethod
    def instance_from_db(cls, row):
        instance = cls.all.get(row[0])
        if instance:
            instance.name = row[1]
            instance.job_title = row[2]
            instance.department_id = row[3]
        else:
            instance = cls(row[1], row[2], row[3])
            instance.id = row[0]
            cls.all[instance.id] = instance
        return instance

    @classmethod
    def get_all(cls):
        return [
            cls.instance_from_db(row)
            for row in CURSOR.execute("SELECT * FROM employees").fetchall()
        ]

    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute("SELECT * FROM employees WHERE id = ?", (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        row = CURSOR.execute(
            "SELECT * FROM employees WHERE name IS ?", (name,)
        ).fetchone()
        return cls.instance_from_db(row) if row else None

    def reviews(self):
        from review import Review

        rows = CURSOR.execute(
            "SELECT * FROM reviews WHERE employee_id = ?", (self.id,)
        ).fetchall()
        return [Review.instance_from_db(row) for row in rows]
