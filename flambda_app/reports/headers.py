REPORT_HEADERS = {
    7: [  # Relatório Empresa Completo
        "nome_empresa", "data_criacao_empresa", "ultima_atualizacao_empresa",
        "rua", "numero", "bairro", "cep", "ultima_atualizacao_endereco",
        "nome_documento", "link_documento", "inicio_documento", "fim_documento",
        "ultima_atualizacao_documento", "tipo_documento", "status_tipo_documento",
        "ultima_atualizacao_tipo_documento", "nome_arquivo", "link_arquivo",
        "ultima_atualizacao_arquivo", "tipo_arquivo", "status_tipo_arquivo",
        "ultima_atualizacao_tipo_arquivo"
    ],
    2: [  # Relatório Empresa Simplificado
        "nome_empresa", "data_criacao_empresa", "rua", "cep"
    ],
    3: [  # Relatório de Arquivos
        "nome_arquivo", "link_arquivo", "tipo_arquivo", "status_tipo_arquivo"
    ]
}
