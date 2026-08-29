import os

from googleapiclient.discovery import build

from src.google_auth import get_google_credentials
from src.integrations_models import (
    AvailabilitySlot,
    CalendarEventRequest,
    CalendarEventResponse,
)


def get_calendar_service():
    return build(
        "calendar",
        "v3",
        credentials=get_google_credentials(),
    )


def get_busy_slots(
    start: str,
    end: str,
    calendar_id: str | None = None,
) -> list[AvailabilitySlot]:
    calendar_id = calendar_id or os.getenv(
        "GOOGLE_CALENDAR_ID",
        "primary",
    )

    response = (
        get_calendar_service()
        .freebusy()
        .query(
            body={
                "timeMin": start,
                "timeMax": end,
                "items": [{"id": calendar_id}],
            }
        )
        .execute()
    )

    busy = (
        response.get("calendars", {})
        .get(calendar_id, {})
        .get("busy", [])
    )

    return [
        AvailabilitySlot(
            start=item["start"],
            end=item["end"],
        )
        for item in busy
    ]


def create_calendar_event(
    request: CalendarEventRequest,
) -> CalendarEventResponse:
    event = (
        get_calendar_service()
        .events()
        .insert(
            calendarId=request.calendar_id,
            body={
                "summary": request.task_title,
                "description": request.description,
                "start": {
                    "dateTime": request.start,
                    "timeZone": request.timezone,
                },
                "end": {
                    "dateTime": request.end,
                    "timeZone": request.timezone,
                },
            },
        )
        .execute()
    )

    return CalendarEventResponse(
        event_id=event["id"],
        html_link=event.get("htmlLink"),
        summary=event.get("summary", request.task_title),
        start=event["start"].get("dateTime", request.start),
        end=event["end"].get("dateTime", request.end),
    )
