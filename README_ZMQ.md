患者刷卡（相当于登录操作，系统记录token）

患者提出问题，LLM（大型语言模型）选择调用函数

参数组织（token作为每个函数的第一个参数，无需LLM传输）

后端api服务根据token拿到患者的基本信息

根据这些信息完成数据查询

LLM根据返回选择下一步是否给出最终答案

场景一：我刚做了体检，结果出来了吗，帮我更新一下体检报告。
场景二：我觉得自己感冒了，上次拿的什么药，帮我查一下，找不到的话帮我挂一下门诊。
场景三：我最近的血压有些高，去年是多少？。
场景四：我需要为家里人更新健康保险，需要拿到他们的健康报告和处方记录。
场景五：我想预约下周的普职体检，帮我看下检查的流程和准备的事项。如果可以的话，帮我看下下周几人少。
场景六：开药方的医生说的啥我忘记了，有啥忌口，跟之前的药不能一起吃，你帮我看一下，(实际是扫码，这里用id代替)。
场景七：昨天晚上肚子特别难受，我应该挂什么科室啊？
场景八：帮我看下我家里两个小孩的疫苗接种记录，还有几针没打完？今年还需要打别的什么疫苗吗？


### 场景二：查询药品记录和挂号服务

**API 1: 查询药品记录**

- 名称: `getMedicationHistory`
- 参数:
  - `patientId`: 患者ID
- 返回数据:
  - 药品名称
  - 开药日期
  - 药品剂量
  - 服用频率

要查询患者的药品记录，首先需要一个patients表

![image-20240108154125440](C:\Users\86159\AppData\Roaming\Typora\typora-user-images\image-20240108154125440.png)



其次需要一个病人的药品记录表（这里要创建一个药品表和一个病人和药品连接的中间表）

药品表 medication

![image-20240108154311015](C:\Users\86159\AppData\Roaming\Typora\typora-user-images\image-20240108154311015.png)

中间表 patients_medication_records

![image-20240108154359056](C:\Users\86159\AppData\Roaming\Typora\typora-user-images\image-20240108154359056.png)



分别定义好对应的models包下的实体类和schemes包中的模型

models包使用ORM对象关系映射，允许将python类映射到数据库表

这些类定义了表的结构。这些类直接和数据库交互，反映了数据库的实际状态

schemas包 通常包含pydantic模型，用于请求和响应数据的验证和序列化。这些模型定义了api接口的输入输出数据格式

这些模型通常作为DTO（数据传输对象）用于在应用程序的不同部分之间传输数据，如从数据库到客户端，这有助于保持内部数据

（如数据库模型）和外部数据（如客户端请求和响应）的隔离



首先为了提高复用的效率，先为三张表创建对应的简单crud

```python
from sqlalchemy.orm import Session

from db.models.patients import Patients

"""
    病人表操作
"""

skip: int = 0
limit: int = 100


def query_patients_all_info(db: Session):
    """
    查询所有的患者信息
    :param db:
    :return:
    """
    return db.query(Patients).offset(skip).limit(limit).all()


def query_patients_info_by_id(db: Session, patient_id: int) -> Patients:
    """
    根据ID查询单个患者的信息
    :param db:
    :param patient_id:
    :return:
    """
    return db.query(Patients).filter(Patients.id == patient_id).first()


def query_patients_by_username(db: Session, username: str) -> Patients:
    """
    Query Patients based on username
    :param db:
    :param username:
    :return:
    """
    return db.query(Patients).filter(Patients.username == username).first()



```



```python
fastapi的路由
def mount_app_routes(_app: FastAPI):
    from api import get_medication_history, get_blood_pressureHistory
    from api.patient.patient_information import db_query
    from api.auth.auth_controller import login
    # Tag: register apis
    _app.get("/api/get_medication_history/{patientId}",
             tags=["获取患者药品记录"],
             response_model=BaseResponse,
             summary="获取患者药品记录",
             )(get_medication_history)
    _app.get("/api/get_blood_pressure_history",
             tags=["查询历史血压记录"],
             response_model=BaseResponse,
             summary="get_medication_history",
             )(get_blood_pressureHistory)

    _app.get("/api/db_query",
             tags=["查询数据库"],
             response_model=BaseResponse,
             summary="get_db",
             )(db_query)
    _app.post("/api/login",
              tags=["用户登录"],
              response_model=BaseResponse,
              summary="login",
              )(login)

```



代码测试   首先登录生成token

![image-20240108184330180](C:\Users\86159\AppData\Roaming\Typora\typora-user-images\image-20240108184330180.png)



**API 2: 挂号服务**

- 名称: `makeAppointment`
- 参数:
  - `patientId`: 患者ID
  - `department`: 科室名称
  - `preferredDate`: 优先日期
- 返回数据:
  - 预约确认
  - 预约时间
  - 预约科室

## 场景思考

我有心脏病，你能给我推荐心脏病相关的专家吗？

我日常需要服用哮喘病药物，你能帮我查看这个药物我能购买的数量和库存吗？

我已经输液两天了，你能帮我看一下我接下来还要输液的次数和时间吗？

我患有高血糖，你能给我一些饮食和生活习惯建议吗？

我想了解一下医院拔牙的价格，能给我一个价目表吗？