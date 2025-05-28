from calendars.service import CalendarService


#   возврат сервиса календаря
def get_calendar_service() -> CalendarService:
    return CalendarService()