import datetime
import os
import shutil

from sqlalchemy import inspect
from sqlalchemy import text


PUBLIC_MEDIA_RENAMES = {
    "coachProfile/default_male.jpg": "coachProfile/public_coach_mason.jpg",
    "coachProfile/default_female.jpg": "coachProfile/public_coach_olivia.jpg",
    "coachProfile/default_none.jpg": "coachProfile/public_coach_neo.jpg",
    "coachProfile/test.jpg": "coachProfile/public_coach_ryan.jpg",
    "Course/cover/Coach20221217_204532.jpg": "Course/cover/public_course_core_fitting.jpg",
    "Course/cover/coach_alpha_20221217_204850.jpg": "Course/cover/public_course_strength_foundation.jpg",
    "Course/cover/coach_alpha_20221217_205244.jpg": "Course/cover/public_course_cycle_cardio.jpg",
    "Course/cover/coach_beta_20221217_205454.jpg": "Course/cover/public_course_swim_basics.jpg",
    "Course/video/_Compressed_Coach20221217_204532.mp4": "Course/video/public_course_core_fitting.mp4",
    "Course/video/_Compressed_coach_alpha_20221217_204850.mp4": "Course/video/public_course_strength_foundation.mp4",
    "Course/video/coach_alpha_20221217_205244.mp4": "Course/video/public_course_cycle_cardio.mp4",
    "Course/video/_Compressed_coach_beta_20221217_205454.mp4": "Course/video/public_course_swim_basics.mp4",
}


PUBLIC_COACHES = [
    {
        "username": "public_coach_mason",
        "email": "mason.public@gym.local",
        "speciality": "fitting",
        "sex": 1,
        "profile": "../static/coachProfile/public_coach_mason.jpg",
    },
    {
        "username": "public_coach_olivia",
        "email": "olivia.public@gym.local",
        "speciality": "strength",
        "sex": 2,
        "profile": "../static/coachProfile/public_coach_olivia.jpg",
    },
    {
        "username": "public_coach_neo",
        "email": "neo.public@gym.local",
        "speciality": "all",
        "sex": 0,
        "profile": "../static/coachProfile/public_coach_neo.jpg",
    },
    {
        "username": "public_coach_ryan",
        "email": "ryan.public@gym.local",
        "speciality": "swimming",
        "sex": 1,
        "profile": "../static/coachProfile/public_coach_ryan.jpg",
    },
]


PUBLIC_COURSES = [
    {
        "coach": "public_coach_mason",
        "name": "Public Core Fitting",
        "description": "Free public class for full body activation and foundation movements.",
        "cover": "../static/Course/cover/public_course_core_fitting.jpg",
        "video": "../static/Course/video/public_course_core_fitting.mp4",
        "start": datetime.datetime(2026, 1, 10, 19, 0, 0),
        "end": datetime.datetime(2026, 1, 10, 20, 0, 0),
    },
    {
        "coach": "public_coach_olivia",
        "name": "Public Strength Foundation",
        "description": "Free public class focused on safe strength basics and technique.",
        "cover": "../static/Course/cover/public_course_strength_foundation.jpg",
        "video": "../static/Course/video/public_course_strength_foundation.mp4",
        "start": datetime.datetime(2026, 1, 11, 18, 30, 0),
        "end": datetime.datetime(2026, 1, 11, 19, 30, 0),
    },
    {
        "coach": "public_coach_neo",
        "name": "Public Cycle Cardio",
        "description": "Free public cardio ride for after-work stress release and endurance.",
        "cover": "../static/Course/cover/public_course_cycle_cardio.jpg",
        "video": "../static/Course/video/public_course_cycle_cardio.mp4",
        "start": datetime.datetime(2026, 1, 12, 20, 0, 0),
        "end": datetime.datetime(2026, 1, 12, 21, 0, 0),
    },
    {
        "coach": "public_coach_ryan",
        "name": "Public Swim Basics",
        "description": "Free public lesson for beginner swimming posture and breathing.",
        "cover": "../static/Course/cover/public_course_swim_basics.jpg",
        "video": "../static/Course/video/public_course_swim_basics.mp4",
        "start": datetime.datetime(2026, 1, 13, 17, 0, 0),
        "end": datetime.datetime(2026, 1, 13, 18, 0, 0),
    },
]


def _copy_if_needed(root_path, source_rel, target_rel):
    source_path = os.path.join(root_path, "static", *source_rel.split("/"))
    target_path = os.path.join(root_path, "static", *target_rel.split("/"))

    if not os.path.exists(source_path):
        return
    if os.path.exists(target_path):
        return

    target_dir = os.path.dirname(target_path)
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy2(source_path, target_path)


def _ensure_public_media_assets(flask_app):
    for source_rel, target_rel in PUBLIC_MEDIA_RENAMES.items():
        _copy_if_needed(flask_app.root_path, source_rel, target_rel)


def _tables_ready(db):
    inspector = inspect(db.engine)
    return inspector.has_table("coach") and inspector.has_table("course")


def _ensure_public_marker_columns(db):
    inspector = inspect(db.engine)

    coach_columns = {column["name"] for column in inspector.get_columns("coach")}
    if "is_public_seed" not in coach_columns:
        db.session.execute(text("ALTER TABLE coach ADD COLUMN is_public_seed INTEGER DEFAULT 0"))
        db.session.commit()

    course_columns = {column["name"] for column in inspector.get_columns("course")}
    if "is_public_seed" not in course_columns:
        db.session.execute(text("ALTER TABLE course ADD COLUMN is_public_seed INTEGER DEFAULT 0"))
        db.session.commit()


def _upsert_public_coaches(db, bcrypt):
    from app.model import Coach

    changed = False
    for item in PUBLIC_COACHES:
        coach = Coach.query.filter_by(username=item["username"]).first()
        if coach is None:
            coach = Coach()
            coach.username = item["username"]
            coach.password = bcrypt.generate_password_hash("public123").decode("utf-8")
            db.session.add(coach)
            changed = True

        if coach.Email != item["email"]:
            coach.Email = item["email"]
            changed = True
        if coach.speciality != item["speciality"]:
            coach.speciality = item["speciality"]
            changed = True
        if coach.sex != item["sex"]:
            coach.sex = item["sex"]
            changed = True
        if coach.cprofile != item["profile"]:
            coach.cprofile = item["profile"]
            changed = True
        if coach.is_public_seed != 1:
            coach.is_public_seed = 1
            changed = True

    if changed:
        db.session.commit()


def _upsert_public_courses(db):
    from app.model import Coach, Course

    coach_map = {
        coach.username: coach.cid
        for coach in Coach.query.filter(
            Coach.username.in_([item["username"] for item in PUBLIC_COACHES])
        ).all()
    }

    changed = False
    for item in PUBLIC_COURSES:
        coach_id = coach_map.get(item["coach"])
        if not coach_id:
            continue

        course = Course.query.filter_by(cid=coach_id, name=item["name"]).first()
        if course is None:
            course = Course()
            course.cid = coach_id
            course.name = item["name"]
            db.session.add(course)
            changed = True

        if course.description != item["description"]:
            course.description = item["description"]
            changed = True
        if course.courseProfile != item["cover"]:
            course.courseProfile = item["cover"]
            changed = True
        if course.video != item["video"]:
            course.video = item["video"]
            changed = True
        if course.start != item["start"]:
            course.start = item["start"]
            changed = True
        if course.end != item["end"]:
            course.end = item["end"]
            changed = True
        if course.is_public_seed != 1:
            course.is_public_seed = 1
            changed = True

    if changed:
        db.session.commit()


def bootstrap_public_catalog(flask_app, db, bcrypt):
    if flask_app.config.get("TESTING"):
        return

    try:
        if not _tables_ready(db):
            return
        _ensure_public_marker_columns(db)
        _ensure_public_media_assets(flask_app)
        _upsert_public_coaches(db, bcrypt)
        _upsert_public_courses(db)
    except Exception as exc:
        flask_app.logger.warning("Public catalog bootstrap skipped: %s", exc)
