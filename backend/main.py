import os
import json
import httpx
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.hash import pbkdf2_sha256
import jwt
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Periodic Table Facts Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api")
security = HTTPBearer()

SECRET_KEY = os.environ.get("SESSION_SECRET", "fallback-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

with open(os.path.join(os.path.dirname(__file__), "elements.json"), "r") as f:
    ELEMENTS = json.load(f)

ELEMENTS_BY_SYMBOL = {el["symbol"].lower(): el for el in ELEMENTS}
ELEMENTS_BY_NAME = {el["name"].lower(): el for el in ELEMENTS}


class UserSignup(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AskQuestion(BaseModel):
    question: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/")
async def root():
    return {"message": "Periodic Table Facts Bot API"}


@router.post("/signup", response_model=TokenResponse)
async def signup(user: UserSignup):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    password_hash = pbkdf2_sha256.hash(user.password)
    cur.execute(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
        (user.email, password_hash)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, email, password_hash FROM users WHERE email = %s", (user.email,))
    db_user = cur.fetchone()
    cur.close()
    conn.close()
    
    if not db_user or not pbkdf2_sha256.verify(user.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user["email"]}, expires_delta=access_token_expires
    )
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(email: str = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, email FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(id=user["id"], email=user["email"])


@router.get("/elements")
async def get_all_elements():
    return ELEMENTS


@router.get("/elements/{identifier}")
async def get_element(identifier: str):
    identifier_lower = identifier.lower()
    
    if identifier_lower in ELEMENTS_BY_SYMBOL:
        return ELEMENTS_BY_SYMBOL[identifier_lower]
    
    if identifier_lower in ELEMENTS_BY_NAME:
        return ELEMENTS_BY_NAME[identifier_lower]
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Element '{identifier}' not found"
    )


@router.post("/ask")
async def ask_question(question: AskQuestion, email: str = Depends(verify_token)):
    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenRouter API key not configured"
        )
    
    element_context = ""
    question_lower = question.question.lower()
    
    for symbol, element in ELEMENTS_BY_SYMBOL.items():
        if symbol in question_lower or element["name"].lower() in question_lower:
            element_context += f"\nElement Data for {element['name']} ({element['symbol']}):\n"
            element_context += f"- Atomic Number: {element['atomic_number']}\n"
            element_context += f"- Atomic Weight: {element['atomic_weight']}\n"
            element_context += f"- Group: {element['group']}\n"
            element_context += f"- Period: {element['period']}\n"
            element_context += f"- State at STP: {element['state']}\n"
            element_context += f"- Electron Configuration: {element['electron_configuration']}\n"
            element_context += f"- Density: {element['density']} g/cm³\n"
            break
    
    system_prompt = """You are a helpful chemistry assistant specializing in the periodic table of elements. 
You provide accurate, educational, and engaging information about chemical elements.
Keep your responses clear, factual, and appropriate for students and chemistry enthusiasts.
If element data is provided, use it to give accurate information."""
    
    if element_context:
        system_prompt += f"\n\nHere is the relevant element data:{element_context}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://periodic-facts-bot.replit.app",
                    "X-Title": "Periodic Table Facts Bot"
                },
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question.question}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"OpenRouter API error: {response.text}"
                )
            
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            
            return {"answer": answer, "element_context": element_context if element_context else None}
            
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to AI service timed out"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )


app.include_router(router)

# Serve static frontend files
frontend_dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

# Debug: Check if path exists
if not os.path.exists(frontend_dist_path):
    print(f"⚠️ Frontend dist path not found at: {frontend_dist_path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Backend directory: {os.path.dirname(__file__)}")
    
    # Try alternative path
    alt_path = "/opt/render/project/src/frontend/dist"
    if os.path.exists(alt_path):
        print(f"✓ Found dist at alternative path: {alt_path}")
        frontend_dist_path = alt_path
    else:
        print(f"⚠️ Alternative path also not found: {alt_path}")
        # List what's actually there
        try:
            parent = os.path.dirname(frontend_dist_path)
            print(f"Contents of {parent}: {os.listdir(parent) if os.path.exists(parent) else 'Not found'}")
        except:
            pass

if os.path.exists(frontend_dist_path) and os.path.exists(os.path.join(frontend_dist_path, "index.html")):
    print(f"✓ Mounting static files from: {frontend_dist_path}")
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="static")
else:
    # Fallback for development
    print(f"⚠️ Frontend not ready. Creating fallback endpoint.")
    @app.get("/{full_path:path}")
    async def fallback(full_path: str):
        return FileResponse("../frontend/dist/index.html") if os.path.exists("../frontend/dist/index.html") else {"message": "Frontend not built. Please check build process."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
