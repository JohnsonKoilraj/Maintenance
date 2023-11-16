from typing import Any, Dict, List, Optional, TypeVar, Generic

from pydantic import AnyHttpUrl, BaseSettings, validator
from fastapi import Query
from fastapi_pagination.default import Page as BasePage, Params as BaseParams
import pytz
from urllib.parse import quote  

T = TypeVar("T")


class Params(BaseParams):
    size: int = Query(500, gt=0, le=1000, description="Page size")


class Page(BasePage[T], Generic[T]):
    __params_type__ = Params


# base_domain = "https://erp.themaestro.in"
# base_url = "https://erp.themaestro.in"
base_dir = "/excel_upload"
base_domain_url = ""
base_url_segment = ""
# erp_base_url_segment="/erp"
base_upload_folder = "/var/www/html"
data_base = "mysql+pymysql://root:W3solutions@localhost/Service_Maintenance"


api_doc_path = "/docs"
break_id = 658 # Local
# break_id = 526 # Local


class Settings(BaseSettings):
    API_V1_STR: str = base_url_segment
    # API_v2_STR: str = erp_base_url_segment
    BASE_UPLOAD_FOLDER: str = base_upload_folder
    # BASEURL: str = base_url
    BASE_DIR = base_dir
    SALT_KEY: str = "A0322A@B&H@R!!akLLo012VSzXycAA1"
    PASS_CODE: str = "ERP_Enc_Dec_Pass"
    SECRET_KEY: str = ""
    BREAK_ID: int = break_id  # Local
    DATA_BASE: str = data_base
    # BASE_DOMAIN: str = base_domain
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 2
    BASE_DOMAIN_URL: str = base_domain_url
    API_DOC_PATH: str = api_doc_path
    otp_resend_remaining_sec: int = 120
    tz_IN = pytz.timezone("Asia/Kolkata")
    ApiKey = "fa526904-5c64-4efc-b6b5-eeb40cbedc0e"
    ClientId = "1ade59f7-1b0c-4287-b170-bb9c94d3c142"
    SenderId = "TKTMJL"

    SERVER_NAME: str = "SERVICE mAINTENANCE"
    ROOT_SERVER_BASE_URL: str = ""
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:8000",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        # "https://cbe.themaestro.in",
        # "http://cbe.themaestro.in",
    ]

    PROJECT_NAME: str = "Service Maintenance"

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v

        return data_base


settings = Settings()
