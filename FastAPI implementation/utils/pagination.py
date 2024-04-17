from fastapi_pagination import Page
from fastapi import Query

CustomPage = Page.with_custom_options(
    size=Query(20, ge=1, le=100)
)
