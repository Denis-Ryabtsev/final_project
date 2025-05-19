import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_users.password import PasswordHelper

from core.template import templates
from company.schemas.department import DepartmentCreate
from company.service.department import DepartmentService
from calendars.depencies import get_calendar_service
from calendars.service import CalendarService
from meeting.depencies import get_meeting_service
from meeting.schemas import MeetingChange, MeetingCreate
from meeting.service import MeetingService
from news.depencies import get_news_service
from news.schemas import NewsCreate
from news.service import NewsService
from rating.depencies import get_rating_service
from rating.schemas import RatingCreate
from rating.service import RatingService
from tasks.schemas.comment import CommentCreate
from tasks.service.comment import CommentService
from tasks.models.task import Task, TaskStatus
from tasks.depencies import get_comment_service, get_task_service
from tasks.schemas.task import TaskChange, TaskChangeRole, TaskCreate
from tasks.service.task import TaskService
from users.manager import fastapi_users, get_user_manager
from users.models import RoleType, User
from users.config_token import auth_backend
from users.service import UserService
from users.depencies import get_user_service
from users.schemas import UserChange, UserRegistration
from database import get_session
from core_depencies import check_role, get_user
from news.depencies import get_news_service
from company.service.company import CompanyService
from company.depencies import validate_company_presence, get_company_service, get_department_service
from company.schemas.company import CompanyCreate
from meeting.depencies import get_meeting_service


router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index_page(
    request: Request,
    user: User = Depends(fastapi_users.current_user(optional=True)),
    user_service: UserService = Depends(get_user_service),
    news_service: UserService = Depends(get_news_service),
    company_service: CompanyService = Depends(get_company_service),
    meeting_service: MeetingService = Depends(get_meeting_service),
    session: AsyncSession = Depends(get_session)
):
    profile = None
    users = []
    ratings = []
    news = []
    owner_meetings = []
    tasks = {"owner_tasks": [], "assigned_tasks": []}
    avg = None

    if user:
        profile = await user_service.get_user(user)
        if user.company_id:
            users = await company_service.get_company_users(session, user, user.company_id)
            news = await news_service.get_news(session, user.company_id)
            owner_meetings = await meeting_service.get_meeting(user, session, user.company_id)
        ratings = await user_service.get_rating(session, user)
        avg = await user_service.get_avg_rating(session, user)

        tasks["owner_tasks"] = await user_service.get_owner_tasks(user, session)
        tasks["assigned_tasks"] = await user_service.get_my_tasks(user, session)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "profile": profile,
        "users": users,
        "ratings": ratings,
        "avg": avg,
        'news': news,
        "tasks": tasks,
        "owner_meetings": owner_meetings
    })

@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    user_manager=Depends(get_user_manager),
):
    try:
        db_user = await user_manager.get_by_email(username)
        if not db_user:
            raise Exception("User not found")

        helper = PasswordHelper()
        valid, _ = helper.verify_and_update(password, db_user.hashed_password)

        if not valid:
            raise Exception("Invalid password")

        token = await auth_backend.get_strategy().write_token(db_user)

        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(
            key="project",
            value=token,
            httponly=True,
            max_age=3600,
            samesite="lax"
        )
        return response

    except Exception as e:
        print(f"[LOGIN ERROR]: {e}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": None,
            "error": str(e)
        }, status_code=401)

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("project")
    return response

@router.post("/register")
async def register_user(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    company_role: str = Form(...),
    company_code: Optional[str] = Form(None),
    email: str = Form(...),
    password: str = Form(...),
    service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        if company_code == '':
            company_code = None

        data = UserRegistration(
            first_name=first_name,
            last_name=last_name,
            company_role=company_role,
            company_code=company_code,
            email=email,
            password=password
        )

        await service.register_user(session, data)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": None,
            "error": "Успешная регистрация. Войдите в систему."
        })

    except Exception as e:
        print(f"[REGISTER ERROR]: {e}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": None,
            "error": str(e)
        }, status_code=400)


@router.post("/edit-profile")
async def edit_profile(
    request: Request,
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    company_role: Optional[str] = Form(None),
    company_code: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    user: User = Depends(fastapi_users.current_user()),
    service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        if company_code == "":
            company_code = None

        data = UserChange(
            first_name=first_name or None,
            last_name=last_name or None,
            company_role=company_role or None,
            company_code=company_code,
            email=email or None,
        )

        await service.change_user(session, user, data)

        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        profile = await service.get_user(user)
    
        tasks = {
            "owner_tasks": await service.get_owner_tasks(user, session),
            "assigned_tasks": await service.get_my_tasks(user, session)
        }
        ratings = await service.get_rating(session, user)
        avg = await service.get_avg_rating(session, user)
        users = []
        if user.company_id:
            users = await get_company_service().get_company_users(session, user, user.company_id)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "tasks": tasks,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "error": str(e)
        }, status_code=400)

@router.post("/delete-profile")
async def delete_profile(
    request: Request,
    user: User = Depends(fastapi_users.current_user()),
    service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        await service.delete_user(session, user)
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie("project")
        return response

    except Exception as e:
        profile = await service.get_user(user)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "error": str(e)
        }, status_code=400)
    
@router.post("/change-role")
async def change_role_post(
    request: Request,
    user_id: int = Form(...),
    role: str = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        if user.company_role != RoleType.admin:
            raise HTTPException(status_code=403, detail="Недостаточно прав")

        await user_service.change_role(session, user, user_id, RoleType(role))
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        error = e.detail if isinstance(e, HTTPException) else str(e)

        profile = await user_service.get_user(user)
        users = await company_service.get_company_users(session, user, user.company_id)
        tasks = {
        "owner_tasks": await user_service.get_owner_tasks(user, session),
        "assigned_tasks": await user_service.get_my_tasks(user, session)
    }

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "tasks": tasks,
            "error": error
        }, status_code=400)
    
@router.post("/remove-department")
async def remove_department_post(
    request: Request,
    user_id: int = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        if user.company_role != RoleType.admin:
            raise HTTPException(status_code=403, detail="Недостаточно прав")

        await user_service.delete_department(session, user, user_id)
        users = await company_service.get_company_users(session, user, user.company_id)
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        print(f"[REMOVE DEPT ERROR]: {e}")
        profile = await user_service.get_user(user)
        users = await company_service.get_company_users(session, user, user.company_id)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "error": e.detail if isinstance(e, HTTPException) else str(e)
        }, status_code=400)
    

@router.post("/create-company")
async def create_company_post(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    company_code: str = Form(...),
    admin_code: str = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        if user.company_id:
            raise HTTPException(status_code=400, detail="Вы уже состоите в компании")
        if user.company_role != RoleType.admin:
            raise HTTPException(status_code=403, detail="Недостаточно прав")

        data = CompanyCreate(
            name=name,
            description=description,
            company_code=company_code,
            admin_code=admin_code
        )

        company = await company_service.create_company(session, data, user)

        user.company_id = company.id
        user.company_role = RoleType.admin
        await session.commit()
        await session.refresh(user)

        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        profile = await user_service.get_user(user)
        users = []
        ratings = await user_service.get_rating(session, user)
        avg = await user_service.get_avg_rating(session, user)
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session)
        }

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "tasks": tasks,
            "error": e.detail if isinstance(e, HTTPException) else str(e)
        }, status_code=400)
    
@router.post("/add-user")
async def add_user_post(
    request: Request,
    user_id: int = Form(...),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(fastapi_users.current_user(optional=True)),
):
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Вы не авторизованы")

        if current_user.company_role != RoleType.admin:
            raise HTTPException(status_code=403, detail="Только админ может использовать функционал оргструктуры")

        if not current_user.company_id:
            raise HTTPException(status_code=400, detail="Вы не состоите в компании")

        await company_service.add_user(session, current_user.company_id, user_id)

        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        print(f"[ADD USER ERROR]: {e}")
        error = e.detail if isinstance(e, HTTPException) else str(e)

        profile = await user_service.get_user(current_user) if current_user else None
        users = await company_service.get_company_users(session, current_user, current_user.company_id) if current_user else []
        ratings = await user_service.get_rating(session, current_user) if current_user else []
        avg = await user_service.get_avg_rating(session, current_user) if current_user else None

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": current_user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "error": error
        }, status_code=400)
    
@router.post("/remove-user-from-company")
async def remove_user_from_company(
    request: Request,
    user_id: int = Form(...),
    user: User = Depends(check_role),
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
):
    try:
        if not user.company_id:
            raise HTTPException(status_code=400, detail="Вы не состоите в компании")

        await company_service.delete_user(session, user.company_id, user_id)

        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        error = e.detail if isinstance(e, HTTPException) else str(e)
        print(f"[REMOVE COMPANY USER ERROR]: {error}")

        profile = await user_service.get_user(user)
        users = await company_service.get_company_users(session, user, user.company_id)
        ratings = await user_service.get_rating(session, user)
        avg = await user_service.get_avg_rating(session, user)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "error": error
        }, status_code=400)
    
@router.post("/delete-company")
async def delete_company_post(
    request: Request,
    company_id: int = Form(...),
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
):
    
    try:
        if user.company_role != RoleType.admin:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        await company_service.delete_company(session, company_id)
        user.company_id = None
        user.company_role = RoleType.employee
        await session.commit()
        await session.refresh(user)
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        error = e.detail if isinstance(e, HTTPException) else str(e)

        profile = await user_service.get_user(user)
        users = []
        ratings = await user_service.get_rating(session, user)
        avg = await user_service.get_avg_rating(session, user)
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session)
        }

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "tasks": tasks,
            "error": error
        }, status_code=400)

@router.post("/create-department")
async def create_department_post(
    request: Request,
    name: str = Form(...),
    head_user_id: int = Form(...),
    current_user: User = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_session),
    department_service: DepartmentService = Depends(get_department_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service)
):
    try:
        user = validate_company_presence(current_user)
        data = DepartmentCreate(name=name, head_user_id=head_user_id)
        await department_service.create_department(session, user, user.company_id, data)
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        error = e.detail if isinstance(e, HTTPException) else str(e)
        profile = await user_service.get_user(current_user)
        users = await company_service.get_company_users(session, current_user, current_user.company_id)
        ratings = await user_service.get_rating(session, current_user)
        avg = await user_service.get_avg_rating(session, current_user)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": current_user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "error": error
        }, status_code=400)
    
@router.post("/change-department-head")
async def change_department_head_post(
    request: Request,
    department_id: int = Form(...),
    user_id: int = Form(...),
    current_user: User = Depends(fastapi_users.current_user()),
    department_service: DepartmentService = Depends(get_department_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        user = validate_company_presence(current_user)
        await department_service.change_head_user(session, user, user.company_id, department_id, user_id)
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        error = e.detail if isinstance(e, HTTPException) else str(e)
        profile = await user_service.get_user(current_user)
        users = await company_service.get_company_users(session, current_user, current_user.company_id)
        ratings = await user_service.get_rating(session, current_user)
        avg = await user_service.get_avg_rating(session, current_user)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": current_user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "error": error
        }, status_code=400)
    
@router.post("/delete-department")
async def delete_department_post(
    request: Request,
    department_id: int = Form(...),
    current_user: User = Depends(fastapi_users.current_user()),
    department_service: DepartmentService = Depends(get_department_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        user = validate_company_presence(current_user)

        await department_service.delete_department(session, user, user.company_id, department_id)
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        error = e.detail if isinstance(e, HTTPException) else str(e)

        profile = user_service.get_user(current_user)
        users = await company_service.get_company_users(session, current_user, current_user.company_id)
        ratings = await user_service.get_rating(session, current_user)
        avg = await user_service.get_avg_rating(session, current_user)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": current_user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "error": error
        }, status_code=400)
    
@router.post("/create-task")
async def create_task_post(
    request: Request,
    target_id: int = Form(...),
    start_date: datetime.date = Form(...),
    end_date: datetime.date = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    current_user: User = Depends(fastapi_users.current_user()),
    task_service: TaskService = Depends(get_task_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        user = validate_company_presence(current_user)
        data = TaskCreate(
            target_id=target_id,
            start_date=start_date,
            end_date=end_date,
            title=title,
            description=description
        )

        result = await task_service.create_task(user, session, data)
        await task_service.add_task_calendar(session, result)

        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        error = e.detail if isinstance(e, HTTPException) else str(e)

        profile = user_service.get_user(current_user)
        users = await company_service.get_company_users(session, current_user, current_user.company_id)
        ratings = await user_service.get_rating(session, current_user)
        avg = await user_service.get_avg_rating(session, current_user)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": current_user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "error": error
        }, status_code=400)
    
@router.post("/delete-task")
async def delete_task_post(
    request: Request,
    task_id: int = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    task_service: TaskService = Depends(get_task_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        await task_service.delete_task(user, task_id, session)
        
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session)
        }

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": await user_service.get_user(user),
            "tasks": tasks,
            "error": None
        }, status_code=200)

    except Exception as e:
        print(f"[DELETE TASK ERROR]: {e}")
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session)
        }
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": await user_service.get_user(user),
            "tasks": tasks,
            "error": str(e)
        }, status_code=400)
    
@router.get("/edit-task-form")
async def edit_task_form(
    request: Request,
    task_id: int,
    user: User = Depends(fastapi_users.current_user()),
    task_service: TaskService = Depends(get_task_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session)
):
    task = await session.get(Task, task_id)

    tasks = {
        "owner_tasks": await user_service.get_owner_tasks(user, session),
        "assigned_tasks": await user_service.get_my_tasks(user, session)
    }

    profile = await user_service.get_user(user)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "profile": profile,
        "tasks": tasks,
        "edit_task": task
    })

@router.post("/edit-task/{task_id}")
async def edit_task_post(
    request: Request,
    task_id: int,
    title: str = Form(...),
    description: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    status: str = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    task_service: TaskService = Depends(get_task_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        data = TaskChange(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        await task_service.change_task(user, session, data, task_id)

        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        print(f"[EDIT TASK ERROR]: {e}")

        task = await session.get(Task, task_id)
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session)
        }

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": await user_service.get_user(user),
            "tasks": tasks,
            "edit_task": task,
            "error": str(e)
        }, status_code=400)

@router.post("/change-task-status")
async def change_task_status_post(
    request: Request,
    task_id: int = Form(...),
    status: str = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_session),
    service: TaskService = Depends(get_task_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
):
    try:
        status_enum = TaskStatus(status)
        await service.change_task_role(user, session, task_id, TaskChangeRole(status=status_enum))

        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        profile = await user_service.get_user(user)
        users = await company_service.get_company_users(session, user, user.company_id)
        ratings = await user_service.get_rating(session, user)
        avg = await user_service.get_avg_rating(session, user)
        tasks = {
            "assigned_tasks": await user_service.get_my_tasks(user, session),
            "owner_tasks": await user_service.get_owner_tasks(user, session),
        }

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "tasks": tasks,
            "error": e.detail if isinstance(e, HTTPException) else str(e),
        }, status_code=400)
    
@router.post("/add-comment")
async def add_comment_post(
    request: Request,
    task_id: int = Form(...),
    description: str = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    comment_service: CommentService = Depends(get_comment_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        data = CommentCreate(description=description)
        await comment_service.create_comment(user, session, task_id, data)

        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        profile = await user_service.get_user(user)
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session),
        }

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "tasks": tasks,
            "error": e.detail if isinstance(e, HTTPException) else str(e)
        }, status_code=400)
    
@router.post("/delete-comment")
async def delete_comment_post(
    request: Request,
    comment_id: int = Form(...),
    task_id: int = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    comment_service: CommentService = Depends(get_comment_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        await comment_service.delete_comment(user, session, task_id, comment_id)

        profile = await user_service.get_user(user)
        users = await company_service.get_company_users(session, user, user.company_id)
        ratings = await user_service.get_rating(session, user)
        avg = await user_service.get_avg_rating(session, user)
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session)
        }

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "tasks": tasks
        })

    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "error": str(e)
        }, status_code=400)

@router.post("/rate-task")
async def rate_task_post(
    request: Request,
    task_id: int = Form(...),
    score_date: int = Form(...),
    score_quality: int = Form(...),
    score_complete: int = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    rating_service: RatingService = Depends(get_rating_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
    session: AsyncSession = Depends(get_session)
):
    try:
        data = RatingCreate(
            score_date=score_date,
            score_quality=score_quality,
            score_complete=score_complete
        )

        await rating_service.create_rating(user, session, task_id, data)

        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        profile = await user_service.get_user(user)
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session)
        }
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "tasks": tasks,
            "error": e.detail if isinstance(e, HTTPException) else str(e)
        }, status_code=400)

@router.post("/create-news")
async def create_news_post(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_session),
    news_service: NewsService = Depends(get_news_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service)
):
    try:
        data = NewsCreate(title=title, description=description)
        await news_service.create_news(session, user, user.company_id, data)
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        error = e.detail if isinstance(e, HTTPException) else str(e)
        profile = await user_service.get_user(user)
        users = await company_service.get_company_users(session, user, user.company_id)
        news = await news_service.get_news_by_company(session, user.company_id)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "news": news,
            "news_error": error
        }, status_code=400)

@router.post("/delete-news")
async def delete_news_post(
    request: Request,
    news_id: int = Form(...),
    company_id: int = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_session),
    service: NewsService = Depends(get_news_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service)
):
    try:
        await service.delete_news(session, user, company_id, news_id)
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        error = e.detail if isinstance(e, HTTPException) else str(e)
        profile = await user_service.get_user(user)
        users = await company_service.get_company_users(session, user, user.company_id)
        ratings = await user_service.get_rating(session, user)
        avg = await user_service.get_avg_rating(session, user)
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session)
        }
        news = await service.get_news(session, user.company_id)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "tasks": tasks,
            "news": news,
            "error": error
        }, status_code=400)

@router.post("/create-meeting")
async def create_meeting_post(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    meeting_date: datetime.date = Form(...),
    meeting_time: datetime.time = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_session),
    meeting_service: MeetingService = Depends(get_meeting_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service)
):
    try:
        meeting_data = MeetingCreate(
            title=title,
            description=description,
            meeting_date=meeting_date,
            meeting_time=meeting_time
        )
        await meeting_service.create_meeting(user, session, meeting_data)
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        error = e.detail if isinstance(e, HTTPException) else str(e)
        profile = await user_service.get_user(user)
        users = await company_service.get_company_users(session, user, user.company_id)
        ratings = await user_service.get_rating(session, user)
        avg = await user_service.get_avg_rating(session, user)
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session)
        }

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "tasks": tasks,
            "meeting_error": error
        }, status_code=400)
    
@router.post("/delete-meeting")
async def delete_meeting_post(
    request: Request,
    meeting_id: int = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_session),
    meeting_service: MeetingService = Depends(get_meeting_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service)
):
    try:
        await meeting_service.delete_meeting(user, session, meeting_id)

        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        error = e.detail if isinstance(e, HTTPException) else str(e)

        profile = await user_service.get_user(user)
        users = await company_service.get_company_users(session, user, user.company_id)
        ratings = await user_service.get_rating(session, user)
        avg = await user_service.get_avg_rating(session, user)
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session)
        }
        news = await company_service.get_news(session, user.company_id)
        owner_meetings = await meeting_service.get_meeting(user, session, user.company_id)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "tasks": tasks,
            "news": news,
            "owner_meetings": owner_meetings,
            "error": error
        }, status_code=400)

@router.post("/change-meeting")
async def change_meeting_post(
    request: Request,
    meeting_id: int = Form(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    meeting_date_str: str = Form(""),
    meeting_time_str: str = Form(""),
    user: User = Depends(fastapi_users.current_user()),
    meeting_service: MeetingService = Depends(get_meeting_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        parsed_date = datetime.date.fromisoformat(meeting_date_str) if meeting_date_str else None
        parsed_time = datetime.time.fromisoformat(meeting_time_str) if meeting_time_str else None

        data = MeetingChange(
            title=title,
            description=description,
            meeting_date=parsed_date,
            meeting_time=parsed_time
        )

        await meeting_service.change_meeting(user, session, meeting_id, data)
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        print(f"[CHANGE MEETING ERROR]: {e}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": str(e),
            "user": user,
        }, status_code=400)

@router.post("/add-meeting-user")
async def add_meeting_user_post(
    request: Request,
    meeting_id: int = Form(...),
    user_id: int = Form(...),
    user: User = Depends(fastapi_users.current_user()),
    meeting_service: MeetingService = Depends(get_meeting_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session),
    company_service: CompanyService = Depends(get_company_service)
):
    try:
        await meeting_service.add_user_meeting(user, session, meeting_id, user_id)
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        profile = await user_service.get_user(user)
        users = await company_service.get_company_users(session, user, user.company_id)
        meetings = await meeting_service.get_meeting(user, session, user.company_id)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "owner_meetings": meetings,
            "error": e.detail if isinstance(e, HTTPException) else str(e),
        }, status_code=400)
    
@router.get("/calendar", response_class=HTMLResponse)
async def view_calendar_day(
    request: Request,
    day: int,
    user: User = Depends(fastapi_users.current_user()),
    calendar_service: CalendarService = Depends(get_calendar_service),
    user_service: UserService = Depends(get_user_service),
    company_service: CompanyService = Depends(get_company_service),
    session: AsyncSession = Depends(get_session),
):
    profile = await user_service.get_user(user)
    users = await company_service.get_company_users(session, user, user.company_id)
    ratings = await user_service.get_rating(session, user)
    avg = await user_service.get_avg_rating(session, user)
    tasks = {
        "owner_tasks": await user_service.get_owner_tasks(user, session),
        "assigned_tasks": await user_service.get_my_tasks(user, session)
    }

    try:
        events = await calendar_service.get_day_schedule(user, session, day)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "tasks": tasks,
            "calendar_day": events,
            "selected_day": day
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "users": users,
            "ratings": ratings,
            "avg": avg,
            "tasks": tasks,
            "calendar_day": [],
            "selected_day": day,
            "calendar_error": str(e)
        }, status_code=400)

@router.get("/calendar-month", response_class=HTMLResponse)
async def view_month_schedule(
    request: Request,
    year: int,
    month: int,
    user: User = Depends(fastapi_users.current_user()),
    calendar_service: CalendarService = Depends(get_calendar_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        profile = await user_service.get_user(user)
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session),
        }
        print(f'\n\n\n\n\n\n{year, month}\n\n\n\n')
        events = await calendar_service.get_month_schedule(session, user, year, month)
        print(f'\n\n\n\n\n\n{events}\n\n\n\n')

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "tasks": tasks,
            "calendar_month": events,
            "selected_month": month,
            "selected_year": year
        })
    except Exception as e:
        profile = await user_service.get_user(user)
        tasks = {
            "owner_tasks": await user_service.get_owner_tasks(user, session),
            "assigned_tasks": await user_service.get_my_tasks(user, session),
        }
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "tasks": tasks,
            "calendar_month": [],
            "selected_month": month,
            "selected_year": year,
            "calendar_month_error": str(e)
        }, status_code=400)