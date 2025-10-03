# -*- coding: utf-8 -*-
"""
Ponto de entrada da aplicação para o servidor WSGI (Gunicorn).
"""

import os
from nutriede import create_app

# Cria a instância da aplicação utilizando a 'Application Factory'
app = create_app()

# Este bloco é executado apenas quando o script é chamado diretamente (para desenvolvimento local)
if __name__ == '__main__':
    # Usa a porta definida pelo ambiente ou 8080 como padrão
    port = int(os.environ.get("PORT", 8080))
    # Executa o app. O debug=False é importante para produção.
    # Para desenvolvimento, pode-se alterar para debug=True.
    app.run(host='0.0.0.0', port=port, debug=False)