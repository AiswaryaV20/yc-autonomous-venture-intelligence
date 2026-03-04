from db.database import engine
from db.models import Base

# Create all tables in the database
Base.metadata.create_all(bind=engine)

print("All tables created successfully!")