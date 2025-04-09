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
