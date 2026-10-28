from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ClassroomModule(Base):
    __tablename__ = "classroom_modules"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, index=True, nullable=False)  # 6-digit alphanumeric
    module_id = Column(String, nullable=False)  # Reference to content module ID
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)  # True = unlimited, False = max 80
    is_test = Column(Boolean, default=False, nullable=False)
    time_limit_minutes = Column(Integer, nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    creator = relationship("User", back_populates="created_modules")
    enrollments = relationship("Enrollment", back_populates="classroom_module", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    classroom_module_id = Column(Integer, ForeignKey("classroom_modules.id"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    score = Column(Integer, nullable=True)  # Overall score/grade (percentage)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    student = relationship("User", back_populates="enrollments")
    classroom_module = relationship("ClassroomModule", back_populates="enrollments")
