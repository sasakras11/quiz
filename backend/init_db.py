from database import Base, engine
from models.models import User, QuizResult, CompanyData, VideoIdea, Script, ScriptResult

def init_db():
    """
    Initialize the database by creating all tables.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 