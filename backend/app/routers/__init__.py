from .hcp import router as hcp_router
from .interaction import router as interaction_router

# अगर chat_router फ़ाइल अभी तक नहीं बनी है, तो एरर रोकने के लिए एक डमी राउटर बना देते हैं
try:
    from .chat import router as chat_router
except ImportError:
    from fastapi import APIRouter
    chat_router = APIRouter(prefix="/chat", tags=["Chat"])