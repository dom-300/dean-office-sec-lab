from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_permission, require_role
from app.database import get_db
from app.models import Grade, Subject, User
from app.schemas import GradeCreate

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("/students/{student_id}/grades")
def student_grades(
    student_id: int,
    current_user: User = Depends(require_role("teacher", "admin")),
    _: User = Depends(require_permission("read_grades")),
    db: Session = Depends(get_db),
):
    grades = db.query(Grade).filter(Grade.student_id == student_id).all()
    return {
        "student_id": student_id,
        "grades": [
            {
                "id": g.id,
                "subject_id": g.subject_id,
                "grade": g.grade,
                "comment": g.comment,
            }
            for g in grades
        ],
    }


@router.post("/grades", status_code=status.HTTP_201_CREATED)
def add_grade(
    data: GradeCreate,
    current_user: User = Depends(require_role("teacher", "admin")),
    _: User = Depends(require_permission("edit_grades")),
    db: Session = Depends(get_db),
):
    target_student = db.get(User, data.student_id)
    if target_student is None or not any(r.name == "student" for r in target_student.roles):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Студента не знайдено")

    if db.get(Subject, data.subject_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Дисципліну не знайдено")

    grade = Grade(
        student_id=data.student_id,
        subject_id=data.subject_id,
        grade=data.grade,
        comment=data.comment,
        assigned_by=current_user.id,  # Підзвітність: автор фіксується з токена
    )
    db.add(grade)
    db.commit()
    db.refresh(grade)

    return {
        "id": grade.id,
        "student_id": grade.student_id,
        "grade": grade.grade,
        "comment": grade.comment,
        "assigned_by": current_user.username,
    }
