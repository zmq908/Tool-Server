import argparse
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from utils import BaseResponse
from utils.log import setup_logging


def create_app():
    _app = FastAPI(
        title="Tool Server",
        version="v1.0.0"
    )
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_logging()
    mount_app_routes(_app)
    return _app


def mount_app_routes(_app: FastAPI):
    from api.auth.auth_controller import login
    from api import get_latest_health_check_record
    from api.patient.blood_pressure_records import get_blood_pressureHistory
    from api.patient.medication_records import get_medication_history
    from api.patient.employment_inspection import employment_inspection
    from api.auth.auth_controller import register
    from api.patient.vaccination_controller import get_vaccination_record
    from api.patient.registration_service import get_department_info_by_name,patients_registration
    # Tag: register apis
    _app.get("/api/get_medication_history",
             tags=["获取患者药品记录"],
             response_model=BaseResponse,
             summary="get_medication_history",
             )(get_medication_history)
    _app.get("/api/get_blood_pressure_history",
             tags=["查询历史血压记录"],
             response_model=BaseResponse,
             summary="get_medication_history",
             )(get_blood_pressureHistory)
    _app.get("/api/employment_inspection",
             tags=["体检预约查询"],
             response_model=BaseResponse,
             summary="employment_inspection",
             )(employment_inspection),
    _app.post("/api/login",
              tags=["用户登录"],
              response_model=BaseResponse,
              summary="login",
              )(login)
    _app.get("/api/health_records",
             tags=["查询体检记录"],
             response_model=BaseResponse,
             summary="health_records"
             )(get_latest_health_check_record)
    _app.post("/api/register",
              tags=["用户注册"],
              response_model=BaseResponse,
              summary="register"
              )(register)

    _app.get("/api/get_vaccination_record",
             tags=["查询疫苗接种记录"],
             response_model=BaseResponse,
             summary="get_vaccination_record",
             )(get_vaccination_record)
    _app.get("/api/get_department_info",
             tags=["获取医院科室基本信息"],
             response_model=BaseResponse,
             summary="get_department_info"
             )(get_department_info_by_name)
    _app.get("/api/registration",
             tags=["挂号服务"],
             response_model=BaseResponse,
             summary="patients_registration"
             )(patients_registration)


def run_api(host, port, **kwargs):
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7861)
    args = parser.parse_args()
    app = create_app()
    run_api(
        host=args.host,
        port=args.port
    )
