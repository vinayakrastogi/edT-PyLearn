import random
import string
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.classroom import ClassroomModule, Enrollment

router = APIRouter(prefix="/api/classrooms", tags=["classrooms"])


# Schemas
class CreateClassroomRequest(BaseModel):
    module_id: str
    title: str
    description: Optional[str] = None
    is_public: bool = True
    is_test: bool = False
    time_limit_minutes: Optional[int] = None
    deadline: Optional[datetime] = None


class EnrollRequest(BaseModel):
    code: str


class ClassroomResponse(BaseModel):
    id: int
    code: str
    module_id: str
    title: str
    description: Optional[str]
    is_public: bool
    is_test: bool
    time_limit_minutes: Optional[int]
    deadline: Optional[datetime]
    created_at: datetime
    enrollment_count: int

    model_config = {"from_attributes": True}


class EnrollmentResponse(BaseModel):
    id: int
    classroom_module_id: int
    classroom_title: str
    classroom_code: str
    module_id: str
    enrolled_at: datetime
    score: Optional[int]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


# Helper function to generate 6-digit alphanumeric code
def generate_classroom_code(db: Session) -> str:
    """Generate unique 6-digit alphanumeric code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        existing = db.query(ClassroomModule).filter(ClassroomModule.code == code).first()
        if not existing:
            return code


# Faculty Endpoints
@router.post("/create", response_model=ClassroomResponse)
async def create_classroom(
    request: CreateClassroomRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a classroom (Faculty only)"""
    if current_user.role != "faculty":
        raise HTTPException(status_code=403, detail="Only faculty can create classrooms")
    
    code = generate_classroom_code(db)
    
    classroom = ClassroomModule(
        code=code,
        module_id=request.module_id,
        title=request.title,
        description=request.description,
        creator_id=current_user.id,
        is_public=request.is_public,
        is_test=request.is_test,
        time_limit_minutes=request.time_limit_minutes,
        deadline=request.deadline
    )
    
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    
    return ClassroomResponse(
        id=classroom.id,
        code=classroom.code,
        module_id=classroom.module_id,
        title=classroom.title,
        description=classroom.description,
        is_public=classroom.is_public,
        is_test=classroom.is_test,
        time_limit_minutes=classroom.time_limit_minutes,
        deadline=classroom.deadline,
        created_at=classroom.created_at,
        enrollment_count=0
    )


@router.get("/my-classrooms")
async def get_my_classrooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all classrooms created by faculty"""
    if current_user.role != "faculty":
        raise HTTPException(status_code=403, detail="Only faculty can access this endpoint")
    
    classrooms = db.query(ClassroomModule).filter(
        ClassroomModule.creator_id == current_user.id
    ).all()
    
    result = []
    for classroom in classrooms:
        enrollment_count = db.query(Enrollment).filter(
            Enrollment.classroom_module_id == classroom.id
        ).count()
        
        result.append(ClassroomResponse(
            id=classroom.id,
            code=classroom.code,
            module_id=classroom.module_id,
            title=classroom.title,
            description=classroom.description,
            is_public=classroom.is_public,
            is_test=classroom.is_test,
            time_limit_minutes=classroom.time_limit_minutes,
            deadline=classroom.deadline,
            created_at=classroom.created_at,
            enrollment_count=enrollment_count
        ))
    
    return result


@router.get("/{classroom_id}/analytics")
async def get_classroom_analytics(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific classroom (Faculty only)"""
    classroom = db.query(ClassroomModule).filter(ClassroomModule.id == classroom_id).first()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    if classroom.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this classroom")
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.classroom_module_id == classroom_id
    ).all()
    
    students = []
    total_score = 0
    completed_count = 0
    
    for enrollment in enrollments:
        student = db.query(User).filter(User.id == enrollment.student_id).first()
        students.append({
            "id": student.id,
            "name": student.full_name,
            "email": student.email,
            "enrolled_at": enrollment.enrolled_at,
            "score": enrollment.score,
            "completed_at": enrollment.completed_at
        })
        
        if enrollment.score is not None:
            total_score += enrollment.score
            completed_count += 1
    
    avg_score = total_score / completed_count if completed_count > 0 else None
    
    return {
        "classroom": ClassroomResponse(
            id=classroom.id,
            code=classroom.code,
            module_id=classroom.module_id,
            title=classroom.title,
            description=classroom.description,
            is_public=classroom.is_public,
            is_test=classroom.is_test,
            time_limit_minutes=classroom.time_limit_minutes,
            deadline=classroom.deadline,
            created_at=classroom.created_at,
            enrollment_count=len(enrollments)
        ),
        "students": students,
        "avg_score": avg_score,
        "completion_rate": (completed_count / len(enrollments) * 100) if enrollments else 0
    }


@router.delete("/{classroom_id}")
async def delete_classroom(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a classroom (Faculty only)"""
    classroom = db.query(ClassroomModule).filter(ClassroomModule.id == classroom_id).first()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    if classroom.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this classroom")
    
    db.delete(classroom)
    db.commit()
    
    return {"status": "success", "message": "Classroom deleted"}


# Student Endpoints
@router.post("/enroll")
async def enroll_in_classroom(
    request: EnrollRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll in a classroom using 6-digit code"""
    classroom = db.query(ClassroomModule).filter(ClassroomModule.code == request.code).first()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Invalid classroom code")
    
    # Check if already enrolled
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.classroom_module_id == classroom.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this classroom")
    
    # Check capacity for private classrooms
    if not classroom.is_public:
        enrollment_count = db.query(Enrollment).filter(
            Enrollment.classroom_module_id == classroom.id
        ).count()
        
        if enrollment_count >= 80:
            raise HTTPException(status_code=400, detail="Classroom is full (max 80 students)")
    
    enrollment = Enrollment(
        student_id=current_user.id,
        classroom_module_id=classroom.id
    )
    
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    return {"status": "success", "message": f"Enrolled in {classroom.title}"}


@router.get("/my-enrollments")
async def get_my_enrollments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all classrooms student is enrolled in"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id
    ).all()
    
    result = []
    for enrollment in enrollments:
        classroom = db.query(ClassroomModule).filter(
            ClassroomModule.id == enrollment.classroom_module_id
        ).first()
        
        result.append(EnrollmentResponse(
            id=enrollment.id,
            classroom_module_id=classroom.id,
            classroom_title=classroom.title,
            classroom_code=classroom.code,
            module_id=classroom.module_id,
            enrolled_at=enrollment.enrolled_at,
            score=enrollment.score,
            completed_at=enrollment.completed_at
        ))
    
    return result


@router.delete("/{classroom_id}/unenroll")
async def unenroll_from_classroom(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unenroll from a classroom"""
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.classroom_module_id == classroom_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Not enrolled in this classroom")
    
    db.delete(enrollment)
    db.commit()
    
    return {"status": "success", "message": "Unenrolled from classroom"}
