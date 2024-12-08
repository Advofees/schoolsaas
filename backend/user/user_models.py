import datetime
import pyotp
from sqlalchemy import String, DateTime, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from dateutil.relativedelta import relativedelta
from backend.database.base import Base
import typing
from sqlalchemy.dialects.postgresql import JSONB
import enum
from backend.user.permissions.permissions_schemas import PERMISSIONS


from backend.school.school_model import School
from backend.file.file_model import File, Profile
from backend.calendar_events.calendar_events_model import CalendarEvent
from backend.student.student_model import Student
from backend.school.school_model import School, SchoolParent
from backend.teacher.teacher_model import Teacher


class RoleType(enum.Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    SECRETARY = "secretary"
    BURSAR = "bursar"
    CLASS_TEACHER = "class_teacher"


class UserPermission(Base):
    __tablename__ = "user_permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    permission_description: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Add back-reference to users for direct permissions
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_permission_associations",
        back_populates="permissions",
        viewonly=True,
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="role_permission_associations",
        back_populates="user_permissions",
        viewonly=True,
    )

    @property
    def permissions(self):
        return PERMISSIONS.model_validate(self.permission_description)

    def __init__(self, permission_description: dict):
        super().__init__()

        self.permission_description = PERMISSIONS.model_validate(
            permission_description
        ).model_dump(exclude_defaults=True, exclude_unset=True)


class UserPermissionAssociation(Base):
    __tablename__ = "user_permission_associations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.id"), primary_key=True
    )
    user_permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("user_permissions.id"), primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    def __init__(self, user_id: uuid.UUID, user_permission_id: uuid.UUID):
        super().__init__()
        self.user_id = user_id
        self.user_permission_id = user_permission_id


class RolePermissionAssociation(Base):
    __tablename__ = "role_permission_associations"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("roles.id"), primary_key=True
    )
    user_permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("user_permissions.id"), primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    def __init__(self, role_id: uuid.UUID, user_permission_id: uuid.UUID):
        super().__init__()
        self.role_id = role_id
        self.user_permission_id = user_permission_id


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    expire_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    # ---
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.id"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def __init__(self, user_id: uuid.UUID):
        super().__init__()

        self.user_id = user_id
        self.expire_at = datetime.datetime.utcnow() + relativedelta(months=6)


class UserRoleAssociation(Base):
    __tablename__ = "user_role_associations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.id"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("roles.id"), primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    def __init__(self, user_id: uuid.UUID, role_id: uuid.UUID):
        super().__init__()
        self.user_id = user_id
        self.role_id = role_id


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[typing.Optional[str]] = mapped_column(String)

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_role_associations",
        back_populates="roles",
        viewonly=True,
    )

    user_permissions: Mapped[list["UserPermission"]] = relationship(
        "UserPermission",
        secondary="role_permission_associations",
        back_populates="roles",
        viewonly=True,
    )

    def __init__(
        self, name: str, type: RoleType, description: typing.Optional[str] = None
    ):
        super().__init__()
        self.name = name
        self.description = description
        self.type = type.value


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    secret_key: Mapped[str] = mapped_column()
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Direct permissions relationship
    permissions: Mapped[list["UserPermission"]] = relationship(
        "UserPermission",
        secondary="user_permission_associations",
        back_populates="users",
        viewonly=True,
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_role_associations",
        back_populates="users",
        viewonly=True,
    )

    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user"
    )
    files: Mapped[list["File"]] = relationship("File", back_populates="user")
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(
        "CalendarEvent", back_populates="creator"
    )
    school_user: Mapped["School"] = relationship(
        School, back_populates="user", uselist=False
    )
    student_user: Mapped["Student"] = relationship(
        Student, back_populates="user", uselist=False
    )
    school_parent_user: Mapped["SchoolParent"] = relationship(
        SchoolParent, back_populates="user", uselist=False
    )
    teacher_user: Mapped["Teacher"] = relationship(
        Teacher, back_populates="user", uselist=False
    )
    profile: Mapped["Profile"] = relationship(
        "Profile", back_populates="user", uselist=False
    )

    @property
    def name(self):
        if self.school_user:
            return self.school_user.name
        elif self.teacher_user:
            return self.teacher_user.first_name
        elif self.student_user:
            return self.student_user.first_name

    @property
    def school_id(self):
        if self.school_user:
            return self.school_user.id
        elif self.teacher_user:
            return self.teacher_user.school.id
        elif self.student_user:
            if not self.student_user.school_students_associations:
                raise ValueError(
                    f"Student {self.student_user.id} is not associated with any school"
                )

            active_association = next(
                (
                    assoc
                    for assoc in self.student_user.school_students_associations
                    if assoc.is_active
                ),
                None,
            )
            if not active_association:
                raise ValueError(
                    f"Student {self.student_user.id} has no active school set"
                )
            return active_association.school_id

        elif self.school_parent_user:
            if not self.school_parent_user.school_parent_associations:
                raise ValueError(
                    f"Parent {self.school_parent_user.id} is not associated with any school"
                )

            active_association = next(
                (
                    assoc
                    for assoc in self.school_parent_user.school_parent_associations
                    if assoc.is_active
                ),
                None,
            )
            if not active_association:
                raise ValueError(
                    f"Parent {self.school_parent_user.id} has no active school set"
                )
            return active_association.school_id

        return None

    def __init__(
        self,
        email: str,
        username: str,
        password_hash: str,
    ):
        super().__init__()
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.secret_key = pyotp.random_base32()

    def has_role_type(self, role_type: RoleType) -> bool:
        return any(role.type == role_type.value for role in self.roles)

    @property
    def all_permissions(self) -> set[UserPermission]:
        all_permissions = set(self.permissions)
        return all_permissions
