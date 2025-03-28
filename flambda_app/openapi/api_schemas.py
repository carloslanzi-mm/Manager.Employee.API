"""
API Schemas Module for Flambda APP
Version: 1.0.0
"""
from marshmallow import Schema, fields, validate

from flambda_app.enums.messages import MessagesEnum
from flambda_app.openapi.schemas import (DefaultResponseSchema, DeletionSchema, ErrorSchema,
                                         HateosDefaultListResponseSchema,
                                         HateosDefaultResponseSchema, LinkSchema, MetaSchema,
                                         RequestControlSchema)


# ***************************
# Event
# ***************************
class EventSchema(Schema):
    type = fields.Str()
    data = fields.Dict()
    date = fields.DateTime(example="2021-05-03T19:41:36.315842-03:00")
    hash = fields.Str(example="406cce9743906f7b8d7dd5d5c5d8c95d820eeefd72a3a554a4a726d022d8fa19")


class OcorenSchema(Schema):
    chavenfe = fields.Str(example="32210206107255000134550010001712551245826554")
    ocor = fields.Str(example="MOTIVO DO CANCELAMENTO")
    origem = fields.Str(example="SAC/EAGLE")
    pedido = fields.Str(example="Z1223321")


class EventCreateRequestSchema(OcorenSchema):
    pass


class EventUpdateRequestSchema(EventCreateRequestSchema):
    pass


class EventListResponseSchema(DefaultResponseSchema):
    data = fields.List(fields.Nested(EventSchema))
    control = fields.Nested(RequestControlSchema)
    meta = fields.Nested(MetaSchema)
    links = fields.List(fields.Nested(LinkSchema))


class EventListErrorResponseSchema(ErrorSchema):
    pass


class EventGetResponseSchema(Schema):
    data = fields.Nested(EventSchema)
    control = fields.Nested(RequestControlSchema)
    meta = fields.Nested(MetaSchema)
    links = fields.List(fields.Nested(LinkSchema))


class EventCreateResponseSchema(Schema):
    result = fields.Bool(example=True)
    event_hash = fields.Str(
        example="c82bf3ee20dd2f4ae7109e52d313a3190f1a85ba3362c54d3eb6257bd0c4d69d")
    code = fields.Int(example=MessagesEnum.EVENT_REGISTERED_WITH_SUCCESS.code)
    label = fields.String(example=MessagesEnum.EVENT_REGISTERED_WITH_SUCCESS.label)
    message = fields.String(example=MessagesEnum.EVENT_REGISTERED_WITH_SUCCESS.message)
    params = fields.List(fields.Str())


class EventCreateErrorResponseSchema(Schema):
    result = fields.Bool(example=False)
    event_hash = fields.Str(example=None)
    code = fields.Int(example=MessagesEnum.EVENT_TYPE_UNKNOWN_ERROR.code)
    label = fields.String(example=MessagesEnum.EVENT_TYPE_UNKNOWN_ERROR.label)
    message = fields.String(example=MessagesEnum.EVENT_TYPE_UNKNOWN_ERROR.message)
    params = fields.List(fields.Str())


class EventUpdateResponseSchema(EventGetResponseSchema):
    pass


class EventDeleteResponseSchema(EventGetResponseSchema):
    data = fields.Nested(DeletionSchema)


def register():
    # simple function only to force the import of the script on app.py
    pass


# ***************************
# Company
# ***************************
class CompanySchema(Schema):
    id = fields.Int(example=1)
    name = fields.Str(example="Empresa 1")
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    deleted_at = fields.DateTime()
    uuid = fields.UUID(example="4bcad46b-6978-488f-8153-1c49f8a45244")
    active = fields.Int(validate=validate.OneOf([0, 1]))


class HateosCompanyListResponseSchema(HateosDefaultListResponseSchema):
    data = fields.List(fields.Nested(CompanySchema))
    control = fields.Nested(RequestControlSchema)


class CompanyListResponseSchema(DefaultResponseSchema):
    data = fields.List(fields.Nested(CompanySchema))
    control = fields.Nested(RequestControlSchema)


class CompanyListErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.LIST_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.LIST_ERROR.label)
    message = fields.Str(example=MessagesEnum.LIST_ERROR.message)


class CompanyGetResponseSchema(DefaultResponseSchema):
    data = fields.Nested(CompanySchema)


class HateosCompanyGetResponseSchema(HateosDefaultResponseSchema):
    data = fields.Nested(CompanySchema)


class CompanyGetErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.FIND_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.FIND_ERROR.label)
    message = fields.Str(example=MessagesEnum.FIND_ERROR.message)


class CompanyCreateRequestSchema(Schema):
    name = fields.Str(example="Empresa 1")
    active = fields.Int(validate=validate.OneOf([0, 1]))


class CompanyCreateResponseSchema(DefaultResponseSchema):
    data = fields.Nested(CompanySchema)


class CompanyCreateErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.CREATE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.CREATE_ERROR.label)
    message = fields.Str(example=MessagesEnum.CREATE_ERROR.message)


class CompanyCompleteUpdateRequestSchema(CompanyCreateRequestSchema):
    pass


class CompanyUpdateResponseSchema(CompanyCreateResponseSchema):
    pass


class CompanyUpdateErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.UPDATE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.UPDATE_ERROR.label)
    message = fields.Str(example=MessagesEnum.UPDATE_ERROR.message)


class CompanySoftUpdateRequestSchema(Schema):
    field = fields.Str(example="value")


class CompanySoftDeleteResponseSchema(DefaultResponseSchema):
    data = fields.Dict(example={"deleted": True})


class CompanyDeleteResponseSchema(Schema):
    data = fields.Dict(example={"deleted": True})


class CompanySoftDeleteErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.SOFT_DELETE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.SOFT_DELETE_ERROR.label)
    message = fields.Str(example=MessagesEnum.SOFT_DELETE_ERROR.message)


class CompanyDeleteErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.DELETE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.DELETE_ERROR.label)
    message = fields.Str(example=MessagesEnum.DELETE_ERROR.message)


# ***************************
# Employee
# ***************************
class EmployeeSchema(Schema):
    id = fields.Int(example=1)
    sku = fields.Int(example=657705)
    name = fields.Str(
        example="Guarda Roupa Casal com Espelho 3 Portas de Correr Lara Espresso Móveis")
    description = fields.Str(
        example="Guarda Roupa com maior resistência, durabilidade e acabamento, revestimento "
                "interno e externo. Pintura em estufas modernas com UV (ultra violeta). "
                "Modelo com corrediça metálica em aço, 4 gavetas espaçosas, perfil em alumínio, "
                "roldanas de aço carbono com rolamento, divisão ele/ela")
    supplier_id = fields.Int(example=1)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    deleted_at = fields.DateTime()
    active = fields.Int(validate=validate.OneOf([0, 1]))
    uuid = fields.UUID(example="4bcad46b-6978-488f-8153-1c49f8a45244")


class EmployeeSchema(Schema):
    id = fields.Int(example=1)
    uuid = fields.UUID(example="4bcad46b-6978-488f-8153-1c49f8a45244")
    company_id = fields.Int(example=1001)
    name = fields.Str(example="John Wick")
    hourly_rate = fields.Float(example=25.50)
    is_admin = fields.Int(validate=validate.OneOf([0, 1]))
    is_active = fields.Int(validate=validate.OneOf([0, 1]))
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    deleted_at = fields.DateTime()


class HateosEmployeeListResponseSchema(HateosDefaultListResponseSchema):
    data = fields.List(fields.Nested(EmployeeSchema))
    control = fields.Nested(RequestControlSchema)


class EmployeeListResponseSchema(DefaultResponseSchema):
    data = fields.List(fields.Nested(EmployeeSchema))
    control = fields.Nested(RequestControlSchema)


class EmployeeListErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.LIST_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.LIST_ERROR.label)
    message = fields.Str(example=MessagesEnum.LIST_ERROR.message)


class EmployeeGetResponseSchema(DefaultResponseSchema):
    data = fields.Nested(EmployeeSchema)


class HateosEmployeeGetResponseSchema(HateosDefaultResponseSchema):
    data = fields.Nested(EmployeeSchema)


class EmployeeGetErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.FIND_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.FIND_ERROR.label)
    message = fields.Str(example=MessagesEnum.FIND_ERROR.message)


class EmployeeCreateRequestSchema(Schema):
    company_id = fields.Int(example=1001)
    name = fields.Str(example="John Wick")
    hourly_rate = fields.Float(example=25.50)
    is_admin = fields.Int(validate=validate.OneOf([0, 1]))
    is_active = fields.Int(validate=validate.OneOf([0, 1]))


class EmployeeCreateResponseSchema(DefaultResponseSchema):
    data = fields.Nested(EmployeeSchema)


class EmployeeCreateErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.CREATE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.CREATE_ERROR.label)
    message = fields.Str(example=MessagesEnum.CREATE_ERROR.message)


class EmployeeCompleteUpdateRequestSchema(EmployeeCreateRequestSchema):
    pass


class EmployeeUpdateResponseSchema(EmployeeCreateResponseSchema):
    pass


class EmployeeUpdateErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.UPDATE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.UPDATE_ERROR.label)
    message = fields.Str(example=MessagesEnum.UPDATE_ERROR.message)


class EmployeeSoftUpdateRequestSchema(Schema):
    field = fields.Str(example="value")


class EmployeeSoftDeleteResponseSchema(DefaultResponseSchema):
    data = fields.Dict(example={"deleted": True})


class EmployeeDeleteResponseSchema(Schema):
    data = fields.Dict(example={"deleted": True})


class EmployeeSoftDeleteErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.SOFT_DELETE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.SOFT_DELETE_ERROR.label)
    message = fields.Str(example=MessagesEnum.SOFT_DELETE_ERROR.message)


class EmployeeDeleteErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.DELETE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.DELETE_ERROR.label)
    message = fields.Str(example=MessagesEnum.DELETE_ERROR.message)
