from .quiz import quiz_router
from .topics import topics_router
from .errors import router as errors_router
from .keywords import router as keywords_router

def register_all(dp):
    dp.include_router(quiz_router)
    dp.include_router(topics_router)
    dp.include_router(keywords_router)
    dp.include_router(errors_router)
