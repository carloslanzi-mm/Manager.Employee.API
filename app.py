"""This is the main file of the lambda application

This module contains the handler method
"""
import base64
import os

import boot
from flask import request as flask_request, jsonify, Response
from flambda_app.aws.s3 import S3
from flambda_app import APP_NAME, APP_VERSION, http_helper, helper
from flambda_app.config import get_config
from flambda_app.enums.messages import MessagesEnum
from flambda_app.exceptions import ApiException, CustomException, ValidationException
from flambda_app.flambda import Flambda
from flambda_app.helper import open_vendor_file, print_routes
from flambda_app.http_helper import (CUSTOM_DEFAULT_HEADERS, get_favicon_16x16_data,
                                     get_favicon_32x32_data, set_hateos_links, set_hateos_meta)
from flambda_app.http_resources.request import ApiRequest
from flambda_app.http_resources.response import ApiResponse
from flambda_app.logging import get_logger, set_debug_mode
from flambda_app.openapi import api_schemas, generate_openapi_yml, get_doc, spec
from flambda_app.services.company_manager import CompanyManager
from flambda_app.services.employee_manager import EmployeeManager
from flambda_app.services.healthcheck_manager import HealthCheckManager
from flambda_app.services.report_manager import ReportManager
from flambda_app.services.upload_manager import UploadManager
from flambda_app.services.v1.company_service import CompanyService
from flambda_app.services.v1.employee_service import EmployeeService
from flambda_app.services.v1.report_service import ReportService
from flambda_app.services.v1.upload_service import UploadService

# load directly by boot
ENV = boot.get_environment()
boot.load_dot_env(ENV)

# config
CONFIG = get_config()
# debug
DEBUG = helper.debug_mode()

# keep in this order, the app generic stream handler will be removed
APP = Flambda(APP_NAME)
# Logger
LOGGER = get_logger(force=True)
# override the APP logger
APP.logger = LOGGER
# override the log configs
if DEBUG:
    # override to the level desired
    set_debug_mode(LOGGER)

s3 = S3(config=CONFIG, logger=LOGGER)
s3.connect()
s3.create_bucket(CONFIG.get('APP_BUCKET'))

API_ROOT = os.environ['API_ROOT'] if 'API_ROOT' in os.environ else ''
API_ROOT_ENDPOINT = API_ROOT if API_ROOT != '' or API_ROOT is None else '/'

LOGGER.info("API_ROOT_ENDPOINT: {}".format(API_ROOT_ENDPOINT))


@APP.route(API_ROOT_ENDPOINT)
def index():
    """
    API Root path

    :return: Returns the name and the current version of the project

    # pylint: disable=line-too-long
    See: https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/
    2244149708/WIP+-+Guidelines+-+RESTful+e+HATEOS#Raiz-do-projeto

    :rtype: flask.Response
    """
    body = {"app": f'{APP_NAME}:{APP_VERSION}'}
    return http_helper.create_response(body=body, status_code=200)


@APP.route(API_ROOT + '/alive')
def alive():
    """
    Health check path

    return Returns an intelligent healthcheck that describe what resource are working or not.

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2226749441/
    Guidelines+para+projetos#Health-Check

    # pylint: disable=line-too-long
    See https://docs.microsoft.com/en-us/dotnet/architecture/microservices/
    implement-resilient-applications/monitor-app-health

    :rtype: flask.Response

    ---

        get:
            summary: Service Health Method
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: HealthCheckSchema
                424:
                    description: Failed dependency response
                    content:
                        application/json:
                            schema: HealthCheckSchema
                503:
                    description: Service unavailable response
                    content:
                        application/json:
                            schema: HealthCheckSchema
        """
    service = HealthCheckManager()
    return service.check()


@APP.route(API_ROOT + '/favicon-32x32.png')
def favicon():
    """
    Favicon path

    return Returns a favicon for the browser with size 32x32
    :rtype: flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "image/png"
    data = get_favicon_32x32_data()

    if helper.is_running_on_lambda():
        data_b64 = {
            'headers': headers,
            'statusCode': 200,
            'body': data,
            'isBase64Encoded': True
        }
        data = helper.to_json(data_b64)
        headers = {"Content-Type": "application/json"}
    else:
        data = base64.b64decode(data)

    return http_helper.create_response(body=data, status_code=200, headers=headers)


@APP.route(API_ROOT + '/favicon-16x16.png')
def favicon16():
    """
    Favicon path

    return Returns a favicon for the browser with size 16x16
    :rtype: flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "image/png"
    data = get_favicon_16x16_data()

    if helper.is_running_on_lambda():
        data_b64 = {
            'headers': headers,
            'statusCode': 200,
            'body': data,
            'isBase64Encoded': True
        }
        data = helper.to_json(data_b64)
        headers = {"Content-Type": "application/json"}
    else:
        data = base64.b64decode(data)

    return http_helper.create_response(body=data, status_code=200, headers=headers)


@APP.route(API_ROOT + '/docs')
def docs():
    """
    Swagger OpenApi documentation

    return Returns the Swagger UI interface for test operations

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2226749441/
    Guidelines+para+projetos#Swagger

    rtype flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "text/html"
    html_file = open_vendor_file('./public/swagger/index.html', 'r')
    html = html_file.read()
    return http_helper.create_response(
        body=html, status_code=200, headers=headers)


@APP.route(API_ROOT + '/openapi.yml')
def openapi():
    """
    Swagger OpenApi documentation route

    return Returns the openapi.yml generated the API specification file

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2226749441/
    Guidelines+para+projetos#Swagger

    rtype flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "text/yaml"
    html_file = open_vendor_file('./public/swagger/openapi.yml', 'r')
    html = html_file.read()
    return http_helper.create_response(
        body=html, status_code=200, headers=headers)


# *************
# company
# *************


@APP.route(f"{API_ROOT}/v1/report/<int:report_id>", methods=["POST"])
def send_email_report(report_id: int):
    # REFATORAR QUANDO O PO (DIEGO) TRAZER MAIS INFORMAÇÕES SOBRE O RELATÓRIO
    # REFATORAR PARA O FLUXO PADRÃO: APP.PY -> MANAGER.PY -> SERVICE.PY -> MANAGER.PY -> APP.PY
    from flambda_app.services.v1.email_service import EmailService
    from flambda_app.repositories.v1.mysql.report_repository import ReportRepository
    from flambda_app.reports.generator import ReportGenerator
    from flambda_app.reports.headers import REPORT_HEADERS
    from flambda_app.vos.report import Report

    data = flask_request.get_json()
    emails = data.get("emails", [])
    company_ids = data.get("company_ids", [])
    generate_xlsx = data.get("generate_xlsx", False)

    if report_id not in REPORT_HEADERS:
        return jsonify({"status": "erro", "mensagem": "report_id inválido"}), 400

    if not emails or not isinstance(emails, list):
        return jsonify({"status": "erro", "mensagem": "Lista de emails inválida"}), 400

    emails_validos = EmailService.validate_emails(emails)

    if len(emails_validos) != len(emails):
        return jsonify({
            "status": "erro",
            "mensagem": "Todos os emails devem ser do domínio @madeiramadeira.com"
        }), 400

    repo = ReportRepository()
    body = repo.list_entity_report(company_ids)

    gerador = ReportGenerator(report_id, body)
    report_file_path = gerador.generate_xlsx() if generate_xlsx else gerador.generate_pdf()
    report_file_name = os.path.basename(report_file_path)

    bucket_name = CONFIG.get("APP_BUCKET")
    s3_key = f"reports/{report_file_name}"

    # Upload do arquivo para o S3 (ou localstack)
    with open(report_file_path, "rb") as f:
        s3.upload_filedata(bucket_name, f, s3_key)

    file_url = s3.get_public_url(bucket_name, s3_key)

    report_obj = Report(report_type_id=report_id, url=file_url, status='completed')
    repo.create_entity(report_obj, 'reports', 'id')

    try:
        subject = "📊 Seu relatório está pronto!"
        body = f"""Olá,

O relatório solicitado está pronto. Você pode acessá-lo aqui: 🔗 {file_url}

Atenciosamente,
Sistema de Relatórios
"""

        EmailService.send(subject, body, emails_validos)

        return jsonify({
            "status": "ok",
            "mensagem": "Emails enviados com sucesso!",
            "emails_enviados": emails_validos,
            "url": file_url
        })

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


@APP.route(f"{API_ROOT_ENDPOINT}multiple-uploads/<int:company_id>/<storage_type>",
           methods=["POST"])
def upload_files(company_id: int, storage_type: str):
    manager = UploadManager(logger=LOGGER, upload_service=UploadService(logger=LOGGER))
    manager.debug(DEBUG)
    response, status_code = manager.process_file_upload(flask_request, company_id, storage_type, s3)
    return jsonify(response), status_code


@APP.route(f"{API_ROOT_ENDPOINT}multiple-uploads/<int:company_id>/<storage_type>",
           methods=["DELETE"])
def delete_uploaded_files2(company_id: int, storage_type: str):
    manager = UploadManager(logger=LOGGER, upload_service=UploadService(logger=LOGGER))
    manager.debug(DEBUG)
    data = flask_request.get_json()
    result, status = manager.process_file_deletion(data, company_id, storage_type)
    return jsonify(result), status


@APP.route(API_ROOT + '/v1/report/types', methods=['GET'])
def report_type_list() -> Response:
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(True)

    manager = ReportManager(logger=LOGGER, report_service=ReportService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        data = manager.list_report_type(request)
        response.set_data(data)
        response.set_total(manager.count(request))

        # hateos
        response.links = None
        set_hateos_meta(request, response)
        # LOGGER.info(data)
        # LOGGER.info(response.data)
    except CustomException as err:
        LOGGER.error(err)
        error = ApiException(MessagesEnum.LIST_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route(API_ROOT + '/v1/report', methods=['GET'])
def report_list() -> Response:
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(True)

    manager = ReportManager(logger=LOGGER, report_service=ReportService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        data = manager.list(request)
        response.set_data(data)
        response.set_total(manager.count(request))

        # hateos
        response.links = None
        set_hateos_meta(request, response)
        # LOGGER.info(data)
        # LOGGER.info(response.data)
    except CustomException as err:
        LOGGER.error(err)
        error = ApiException(MessagesEnum.LIST_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route(f"{API_ROOT}/v1/company", methods=["POST"])
def create_company_with_address():
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(False)

    manager = CompanyManager(
        logger=LOGGER,
        company_service=CompanyService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        response.set_data(manager.create(request))

    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.CREATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)

    # Pre script para gravar os dados
    # from flambda_app.vos.company import CompanyVO
    # from flambda_app.vos.address import Address
    # from flambda_app.repositories.v1.mysql.company_repository import CompanyRepository
    # try:
    #     data = request.get_json()
    #
    #     # Extraindo dados da empresa
    #     company_data = data.get("company")
    #     if not company_data:
    #         return jsonify({"error": "Dados da empresa são obrigatórios."}), 400
    #
    #     # Extraindo dados do endereço
    #     address_data = data.get("address")
    #     if not address_data:
    #         return jsonify({"error": "Dados do endereço são obrigatórios."}), 400
    #
    #     # Criando objetos VO
    #     company = CompanyVO(**company_data)
    #     address = Address(**address_data)
    #
    #     # Criando a empresa e endereço
    #     company_repo = CompanyRepository()
    #     success, company_id = company_repo.create_with_address(company, address)
    #
    #     if success:
    #         return jsonify({"success": True, "company_id": company_id}), 201
    #     else:
    #         return jsonify({'error': 'Erro ao salvar os dados.'}), 500
    #
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500


@APP.route('/v1/company/<company_id>', methods=['PATCH'])
def company_update(company_id: str) -> Response:
    """
    Company update route

    return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2244149708/
    WIP+-+Guidelines+-+RESTful+e+HATEOS

    rtype flask.Response
        ---
        put:
            summary: Complete Company Update
            parameters:
            - in: path
              name: uuid
              description: "Company id"
              required: true
              schema:
                type: string
                format: uuid
                example: 4bcad46b-6978-488f-8153-1c49f8a45244
            requestBody:
                description: 'Company to be updated'
                required: true
                content:
                    application/json:
                        schema: CompanyCompleteUpdateRequestSchema
            responses:
                200:
                    content:
                        application/json:
                            schema: CompanyUpdateResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: CompanyUpdateErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: CompanyUpdateErrorResponseSchema
            """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(False)

    manager = CompanyManager(logger=LOGGER, company_service=CompanyService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        response.set_data(manager.update(request, company_id))
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.UPDATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route(API_ROOT + '/v1/company', methods=['GET'])
def company_list() -> Response:
    """
    Company list route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2244149708/
    WIP+-+Guidelines+-+RESTful+e+HATEOS

    :rtype flask.Response

        ---
        get:
            summary: Company List
            parameters:
            - name: limit
              in: query
              description: "List limit"
              required: false
              schema:
                type: int
                example: 20
            - name: offset
              in: query
              description: "List offset"
              required: false
              schema:
                type: int
                example: 0
            - name: fields
              in: query
              description: "Filter fields with comma"
              required: false
              schema:
                type: string
                example:
            - name: order_by
              in: query
              description: "Ordination of list"
              required: false
              schema:
                type: string
                enum:
                 - "asc"
                 - "desc"
            - name: sort_by
              in: query
              description: "Sorting of the list"
              required: false
              schema:
                type: string
                example: id
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: HateosCompanyListResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: CompanyListErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: CompanyListErrorResponseSchema
        """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(True)

    manager = CompanyManager(logger=LOGGER, company_service=CompanyService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        data = manager.list(request)
        response.set_data(data)
        response.set_total(manager.count(request))

        # hateos
        response.links = None
        set_hateos_meta(request, response)
        # LOGGER.info(data)
        # LOGGER.info(response.data)
    except CustomException as err:
        LOGGER.error(err)
        error = ApiException(MessagesEnum.LIST_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route(API_ROOT + '/v1/company/<company_id>', methods=['GET'])
def company_get(company_id: str) -> Response:
    """
    Company get route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2244149708/
    WIP+-+Guidelines+-+RESTful+e+HATEOS

    :rtype flask.Response
        ---
        get:
            summary: Company Get
            parameters:
            - in: path
              name: uuid
              description: "Company Id"
              required: true
              schema:
                type: string
                format: uuid
                example: 4bcad46b-6978-488f-8153-1c49f8a45244
            - name: fields
              in: query
              description: "Filter fields with comma"
              required: false
              schema:
                type: string
                example:
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: HateosCompanyGetResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: CompanyGetErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: CompanyGetErrorResponseSchema
    """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(True)

    manager = CompanyManager(logger=LOGGER, company_service=CompanyService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        response.set_data(manager.get(request, company_id))

        # hateos
        set_hateos_links(request, response, company_id)
        set_hateos_meta(request, response, company_id)

    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.FIND_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route('/v1/company/<company_id>', methods=['DELETE'])
def company_delete(company_id: str) -> Response:
    """
    Company delete route

    return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2244149708/
    WIP+-+Guidelines+-+RESTful+e+HATEOS

    rtype flask.Response
            ---
            delete:
                summary: Soft Company Delete
                parameters:
                - in: path
                  name: uuid
                  description: "Company d"
                  required: true
                  schema:
                    type: string
                    format: uuid
                    example: 4bcad46b-6978-488f-8153-1c49f8a45244
                responses:
                    200:
                        description: Success response
                        content:
                            application/json:
                                schema: CompanySoftDeleteResponseSchema
                    4xx:
                        description: Error response
                        content:
                            application/json:
                                schema: CompanySoftDeleteErrorResponseSchema
                    5xx:
                        description: Service fail response
                        content:
                            application/json:
                                schema: CompanySoftDeleteErrorResponseSchema
                    """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(False)

    manager = CompanyManager(logger=LOGGER, company_service=CompanyService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        data = {"deleted": manager.delete(request, company_id)}
        response.set_data(data)
        # response.set_total(manager.count(request))
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.DELETE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


# *************
# employee
# *************
@APP.route(API_ROOT + '/v1/employee', methods=['POST'])
def employee_create() -> Response:
    """
    Company create route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2244149708/
    WIP+-+Guidelines+-+RESTful+e+HATEOS

    :rtype flask.Response
        ---
        post:
            summary: Company Create
            requestBody:
                description: 'Company to be created'
                required: true
                content:
                    application/json:
                        schema: CompanyCreateRequestSchema
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: CompanyCreateResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: CompanyCreateErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: CompanyCreateErrorResponseSchema
    """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(False)

    manager = EmployeeManager(logger=LOGGER, employee_service=EmployeeService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        created_employee = manager.create(request)
        response.set_data(created_employee)

    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.CREATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route('/v1/employee/<employee_id>', methods=['PATCH'])
def employee_update(employee_id: str) -> Response:
    """
    Employee update route

    return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2244149708/
    WIP+-+Guidelines+-+RESTful+e+HATEOS

    rtype flask.Response
        ---
        put:
            summary: Complete Employee Update
            parameters:
            - in: path
              name: uuid
              description: "Employee id"
              required: true
              schema:
                type: string
                format: uuid
                example: 4bcad46b-6978-488f-8153-1c49f8a45244
            requestBody:
                description: 'Employee to be updated'
                required: true
                content:
                    application/json:
                        schema: EmployeeCompleteUpdateRequestSchema
            responses:
                200:
                    content:
                        application/json:
                            schema: EmployeeUpdateResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: EmployeeUpdateErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: EmployeeUpdateErrorResponseSchema
            """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(False)

    manager = EmployeeManager(logger=LOGGER, employee_service=EmployeeService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        updated_employee = manager.update(request, employee_id)
        response.set_data(updated_employee)
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.UPDATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route(API_ROOT + '/v1/employee', methods=['GET'])
def employee_list() -> Response:
    """
    Employee list route

    return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2244149708/
    WIP+-+Guidelines+-+RESTful+e+HATEOS

    rtype flask.Response

        ---
        get:
            summary: Employee List
            parameters:
            - name: limit
              in: query
              description: "List limit"
              required: false
              schema:
                type: int
                example: 20
            - name: offset
              in: query
              description: "List offset"
              required: false
              schema:
                type: int
                example: 0
            - name: fields
              in: query
              description: "Filter fields with comma"
              required: false
              schema:
                type: string
                example:
            - name: order_by
              in: query
              description: "Ordination of list"
              required: false
              schema:
                type: string
                enum:
                 - "asc"
                 - "desc"
            - name: sort_by
              in: query
              description: "Sorting of the list"
              required: false
              schema:
                type: string
                example: id
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: HateosEmployeeListResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: EmployeeListErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: EmployeeListErrorResponseSchema
        """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(True)

    manager = EmployeeManager(logger=LOGGER, employee_service=EmployeeService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        data = manager.list(request)
        response.set_data(data)
        response.set_total(manager.count(request))

        # hateos
        response.links = None
        set_hateos_meta(request, response)
        # LOGGER.info(data)
        # LOGGER.info(response.data)
    except CustomException as err:
        LOGGER.error(err)
        error = ApiException(MessagesEnum.LIST_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route(API_ROOT + '/v1/employee/<employee_id>', methods=['GET'])
def employee_get(employee_id: str) -> Response:
    """
    Employee get route

    return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2244149708/
    WIP+-+Guidelines+-+RESTful+e+HATEOS

    rtype flask.Response
        ---
        get:
            summary: Employee Get
            parameters:
            - in: path
              name: uuid
              description: "Employee id"
              required: true
              schema:
                type: string
                format: uuid
                example: 4bcad46b-6978-488f-8153-1c49f8a45244
            - name: fields
              in: query
              description: "Filter fields with comma"
              required: false
              schema:
                type: string
                example:
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: HateosEmployeeGetResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: EmployeeGetErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: EmployeeGetErrorResponseSchema
    """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(True)

    manager = EmployeeManager(logger=LOGGER, employee_service=EmployeeService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        response.set_data(manager.get(request, employee_id))

        # hateos
        set_hateos_links(request, response, employee_id)
        set_hateos_meta(request, response, employee_id)

    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.FIND_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route('/v1/employee/<employee_id>', methods=['DELETE'])
def employee_delete(employee_id: str) -> Response:
    """
    Employee delete route

    return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://madeiramadeira.atlassian.net/wiki/spaces/CAR/pages/2244149708/
    WIP+-+Guidelines+-+RESTful+e+HATEOS

    rtype flask.Response
            ---
            delete:
                summary: Soft Employee Delete
                parameters:
                - in: path
                  name: uuid
                  description: "Employee id"
                  required: true
                  schema:
                    type: string
                    format: uuid
                    example: 4bcad46b-6978-488f-8153-1c49f8a45244
                responses:
                    200:
                        description: Success response
                        content:
                            application/json:
                                schema: EmployeeSoftDeleteResponseSchema
                    4xx:
                        description: Error response
                        content:
                            application/json:
                                schema: EmployeeSoftDeleteErrorResponseSchema
                    5xx:
                        description: Service fail response
                        content:
                            application/json:
                                schema: EmployeeSoftDeleteErrorResponseSchema
                    """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')
    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(False)

    manager = EmployeeManager(logger=LOGGER, employee_service=EmployeeService(logger=LOGGER))
    manager.debug(DEBUG)
    try:
        # Tavares
        data = {"deleted": manager.delete(request, employee_id)}
        response.set_data(data)
        # response.set_total(manager.count(request))
        # Primeiro obtém os dados do funcionário antes de deletar

        # employee_data = manager.get(request.to_dict(), employee_id)

        # Deleta o funcionário
        # result = manager.delete(request, employee_id)
        # response.set_data({"deleted": result})

    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.DELETE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


# *************
# doc
# *************
spec.path(view=alive, path=API_ROOT + "/alive", operations=get_doc(alive))

# *************
# company
# *************
spec.path(view=company_list,
          path="/v1/company", operations=get_doc(company_list))
spec.path(view=company_get,
          path="/v1/company/{uuid}", operations=get_doc(company_get))
spec.path(view=create_company_with_address,
          path="/v1/company", operations=get_doc(create_company_with_address))
spec.path(view=company_update,
          path="/v1/company/{uuid}", operations=get_doc(company_update))
spec.path(view=company_delete,
          path="/v1/company/{uuid}", operations=get_doc(company_delete))

# *************
# employee
# *************
spec.path(view=employee_list,
          path="/v1/employee", operations=get_doc(employee_list))
spec.path(view=employee_get,
          path="/v1/employee/{uuid}", operations=get_doc(employee_get))
spec.path(view=employee_create,
          path="/v1/employee", operations=get_doc(employee_create))
spec.path(view=employee_update,
          path="/v1/employee/{uuid}", operations=get_doc(employee_update))
spec.path(view=employee_delete,
          path="/v1/employee/{uuid}", operations=get_doc(employee_delete))

print_routes(APP, LOGGER)
LOGGER.info(f'Running at {ENV}')

# generate de openapi.yml
generate_openapi_yml(spec, LOGGER, force=True)

api_schemas.register()
