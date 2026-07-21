from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from modules.inference.models.kb_model import KBCountermeasure, KBVulnerability, VulnerabilityFilter


async def seed_knowledge_base() -> int:
    existing = await KBVulnerability.find({}).count()
    if existing > 0:
        return 0

    vulns = [
        KBVulnerability(cve_id="CWE-287", title="Improper Authentication", title_pt="Autenticação Inadequada", title_en="Improper Authentication", description="O sistema não valida adequadamente a identidade do usuário antes de conceder acesso.", description_pt="O sistema não valida adequadamente a identidade do usuário antes de conceder acesso.", description_en="The system does not properly validate user identity before granting access.", cvss_score=8.1, cwe="CWE-287", affected_components=["user", "api", "gateway", "identity_provider"], tags=["authentication", "access-control"]),
        KBVulnerability(cve_id="CWE-89", title="SQL Injection", title_pt="Injeção SQL", title_en="SQL Injection", description="Injeção de comandos SQL através de inputs não sanitizados.", description_pt="Injeção de comandos SQL através de inputs não sanitizados.", description_en="SQL command injection through unsanitized inputs.", cvss_score=9.0, cwe="CWE-89", affected_components=["database", "api"], tags=["injection", "database"]),
        KBVulnerability(cve_id="CWE-79", title="Cross-Site Scripting (XSS)", title_pt="Cross-Site Scripting (XSS)", title_en="Cross-Site Scripting (XSS)", description="Injeção de scripts maliciosos em páginas web.", description_pt="Injeção de scripts maliciosos em páginas web.", description_en="Injection of malicious scripts into web pages.", cvss_score=6.1, cwe="CWE-79", affected_components=["api", "user"], tags=["xss", "injection"]),
        KBVulnerability(cve_id="CWE-400", title="Uncontrolled Resource Consumption", title_pt="Consumo Descontrolado de Recursos", title_en="Uncontrolled Resource Consumption", description="O sistema não limita adequadamente o consumo de recursos.", description_pt="O sistema não limita adequadamente o consumo de recursos.", description_en="The system does not properly limit resource consumption.", cvss_score=7.5, cwe="CWE-400", affected_components=["server", "api", "load_balancer", "message_queue"], tags=["dos", "resource"]),
        KBVulnerability(cve_id="CWE-200", title="Information Exposure", title_pt="Exposição de Informações", title_en="Information Exposure", description="Exposição de informações sensíveis.", description_pt="Exposição de informações sensíveis.", description_en="Exposure of sensitive information.", cvss_score=5.3, cwe="CWE-200", affected_components=["server", "api", "database", "storage"], tags=["information-disclosure", "privacy"]),
        KBVulnerability(cve_id="CWE-269", title="Improper Privilege Management", title_pt="Gestão Inadequada de Privilégios", title_en="Improper Privilege Management", description="Falha na gestão adequada de privilégios.", description_pt="Falha na gestão adequada de privilégios.", description_en="Failure in proper privilege management.", cvss_score=8.4, cwe="CWE-269", affected_components=["server", "api", "container", "identity_provider"], tags=["privilege-escalation", "access-control"]),
        KBVulnerability(cve_id="CWE-306", title="Missing Authentication for Critical Function", title_pt="Autenticação Ausente em Função Crítica", title_en="Missing Authentication for Critical Function", description="Funções críticas não exigem autenticação.", description_pt="Funções críticas não exigem autenticação.", description_en="Critical functions do not require authentication.", cvss_score=7.5, cwe="CWE-306", affected_components=["api", "gateway", "microservice"], tags=["authentication", "access-control"]),
        KBVulnerability(cve_id="CWE-798", title="Use of Hard-coded Credentials", title_pt="Uso de Credenciais Fixas", title_en="Use of Hard-coded Credentials", description="Uso de credenciais fixas no código-fonte.", description_pt="Uso de credenciais fixas no código-fonte.", description_en="Use of hard-coded credentials in source code.", cvss_score=7.3, cwe="CWE-798", affected_components=["server", "database", "api"], tags=["credentials", "secrets"]),
        KBVulnerability(cve_id="CWE-862", title="Missing Authorization", title_pt="Autorização Ausente", title_en="Missing Authorization", description="O sistema não verifica permissões adequadamente.", description_pt="O sistema não verifica permissões adequadamente.", description_en="The system does not properly verify permissions.", cvss_score=6.5, cwe="CWE-862", affected_components=["api", "microservice", "gateway"], tags=["authorization", "access-control"]),
        KBVulnerability(cve_id="CWE-502", title="Deserialization of Untrusted Data", title_pt="Desserialização de Dados Não Confiáveis", title_en="Deserialization of Untrusted Data", description="Desserialização de dados não confiáveis.", description_pt="Desserialização de dados não confiáveis.", description_en="Deserialization of untrusted data.", cvss_score=8.8, cwe="CWE-502", affected_components=["server", "api", "message_queue"], tags=["deserialization", "rce"]),
        KBVulnerability(cve_id="CWE-22", title="Path Traversal", title_pt="Path Traversal", title_en="Path Traversal", description="Acesso a arquivos fora do diretório restrito.", description_pt="Acesso a arquivos fora do diretório restrito.", description_en="Access to files outside the restricted directory.", cvss_score=7.5, cwe="CWE-22", affected_components=["server", "api", "storage"], tags=["path-traversal", "file-access"]),
        KBVulnerability(cve_id="CWE-918", title="Server-Side Request Forgery (SSRF)", title_pt="Falsificação de Requisição no Servidor (SSRF)", title_en="Server-Side Request Forgery (SSRF)", description="O servidor pode ser induzido a fazer requisições internas.", description_pt="O servidor pode ser induzido a fazer requisições internas.", description_en="The server can be tricked into making internal requests.", cvss_score=8.8, cwe="CWE-918", affected_components=["server", "api", "microservice"], tags=["ssrf", "server-side"]),
        KBVulnerability(cve_id="CWE-276", title="Incorrect Default Permissions", title_pt="Permissões Padrão Incorretas", title_en="Incorrect Default Permissions", description="Permissões padrão muito permissivas.", description_pt="Permissões padrão muito permissivas.", description_en="Default permissions are too permissive.", cvss_score=6.5, cwe="CWE-276", affected_components=["storage", "container", "database"], tags=["permissions", "misconfiguration"]),
    ]
    await KBVulnerability.insert_many(vulns)

    countermeasures = [
        KBCountermeasure(title="Implementar Autenticação Multifator (MFA)", title_pt="Implementar Autenticação Multifator (MFA)", title_en="Implement Multi-Factor Authentication (MFA)", description="Adicionar camadas extras de verificação de identidade.", description_pt="Adicionar camadas extras de verificação de identidade.", description_en="Add extra layers of identity verification.", priority="critical", implementation_guide="Integrar provedor OAuth 2.0 / SAML e exigir MFA para acessos administrativos.", implementation_guide_pt="Integrar provedor OAuth 2.0 / SAML e exigir MFA para acessos administrativos.", implementation_guide_en="Integrate OAuth 2.0 / SAML provider and require MFA for admin access.", references=["https://owasp.org/www-community/Authentication_Cheat_Sheet"], vulnerability_cwe_ids=["CWE-287", "CWE-306", "CWE-798"]),
        KBCountermeasure(title="Sanitização de Inputs (Consultas Parametrizadas)", title_pt="Sanitização de Inputs (Consultas Parametrizadas)", title_en="Input Sanitization (Parameterized Queries)", description="Utilizar consultas parametrizadas para prevenir injeção.", description_pt="Utilizar consultas parametrizadas para prevenir injeção.", description_en="Use parameterized queries to prevent injection.", priority="critical", implementation_guide="Substituir concatenação por consultas parametrizadas.", implementation_guide_pt="Substituir concatenação por consultas parametrizadas.", implementation_guide_en="Replace string concatenation with parameterized queries.", references=["https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"], vulnerability_cwe_ids=["CWE-89"]),
        KBCountermeasure(title="Content Security Policy (CSP)", title_pt="Política de Segurança de Conteúdo (CSP)", title_en="Content Security Policy (CSP)", description="Implementar cabeçalhos CSP para mitigar XSS.", description_pt="Implementar cabeçalhos CSP para mitigar XSS.", description_en="Implement CSP headers to mitigate XSS.", priority="high", implementation_guide="Configurar header Content-Security-Policy.", implementation_guide_pt="Configurar cabeçalho Content-Security-Policy.", implementation_guide_en="Configure Content-Security-Policy header.", references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"], vulnerability_cwe_ids=["CWE-79"]),
        KBCountermeasure(title="Rate Limiting e Throttling", title_pt="Limitação de Taxa e Throttling", title_en="Rate Limiting and Throttling", description="Limitar requisições para prevenir DoS.", description_pt="Limitar requisições para prevenir ataques de negação de serviço.", description_en="Limit requests to prevent denial of service attacks.", priority="high", implementation_guide="Implementar middleware de rate limiting com Redis.", implementation_guide_pt="Implementar middleware de limitação de taxa com Redis.", implementation_guide_en="Implement rate limiting middleware with Redis.", references=["https://owasp.org/www-community/DoS_Attack_Defenses"], vulnerability_cwe_ids=["CWE-400"]),
        KBCountermeasure(title="Criptografia em Trânsito e Repouso", title_pt="Criptografia em Trânsito e Repouso", title_en="Encryption in Transit and at Rest", description="Criptografar dados sensíveis.", description_pt="Criptografar dados sensíveis.", description_en="Encrypt sensitive data.", priority="critical", implementation_guide="Exigir HTTPS e criptografar campos sensíveis no banco.", implementation_guide_pt="Exigir HTTPS e criptografar campos sensíveis no banco.", implementation_guide_en="Require HTTPS and encrypt sensitive fields in the database.", references=["https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html"], vulnerability_cwe_ids=["CWE-200"]),
        KBCountermeasure(title="Princípio do Menor Privilégio (RBAC)", title_pt="Princípio do Menor Privilégio (RBAC)", title_en="Principle of Least Privilege (RBAC)", description="Implementar controle de acesso baseado em papéis.", description_pt="Implementar controle de acesso baseado em papéis funcionais.", description_en="Implement role-based access control.", priority="critical", implementation_guide="Mapear endpoints e atribuir permissões mínimas.", implementation_guide_pt="Mapear endpoints e atribuir permissões mínimas necessárias.", implementation_guide_en="Map endpoints and assign minimum required permissions.", references=["https://owasp.org/www-community/Access_Control_Cheat_Sheet"], vulnerability_cwe_ids=["CWE-269", "CWE-862", "CWE-276"]),
        KBCountermeasure(title="Validação e Sanitização de Uploads", title_pt="Validação e Sanitização de Uploads", title_en="Upload Validation and Sanitization", description="Validar tipo e conteúdo de arquivos.", description_pt="Validar tipo e conteúdo de arquivos enviados.", description_en="Validate uploaded file type and content.", priority="high", implementation_guide="Verificar magic numbers e extensão.", implementation_guide_pt="Verificar magic numbers (bytes de cabeçalho) e extensão do arquivo.", implementation_guide_en="Check magic header bytes and file extension.", references=["https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload"], vulnerability_cwe_ids=["CWE-22", "CWE-502"]),
        KBCountermeasure(title="Proteção SSRF (Listas de Permissão)", title_pt="Proteção SSRF (Listas de Permissão)", title_en="SSRF Protection (Allow Lists)", description="Restringir destinos de requisições internas.", description_pt="Restringir destinos permitidos para requisições internas do servidor.", description_en="Restrict allowed destinations for internal server requests.", priority="high", implementation_guide="Implementar validação de URLs e allow list.", implementation_guide_pt="Implementar validação de URLs e lista de destinos permitidos.", implementation_guide_en="Implement URL validation and allow list of permitted destinations.", references=["https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html"], vulnerability_cwe_ids=["CWE-918"]),
        KBCountermeasure(title="Segurança de Containers (Imagens Escaneadas)", title_pt="Segurança de Containers (Imagens Verificadas)", title_en="Container Security (Scanned Images)", description="Escanear imagens por vulnerabilidades.", description_pt="Escaneie imagens de containers em busca de vulnerabilidades conhecidas.", description_en="Scan container images for known vulnerabilities.", priority="high", implementation_guide="Integrar Trivy ou Snyk no CI/CD.", implementation_guide_pt="Integrar Trivy ou Snyk no pipeline de CI/CD.", implementation_guide_en="Integrate Trivy or Snyk into your CI/CD pipeline.", references=["https://docs.docker.com/engine/scan/"], vulnerability_cwe_ids=["CWE-276", "CWE-269"]),
        KBCountermeasure(title="Gestão Segura de Credenciais (Cofre)", title_pt="Gestão Segura de Credenciais (Cofre de Senhas)", title_en="Secure Credential Management (Vault)", description="Usar gerenciador de segredos.", description_pt="Utilize um gerenciador centralizado de segredos e credenciais.", description_en="Use a centralized secrets manager for credentials.", priority="critical", implementation_guide="Migrar credenciais para HashiCorp Vault.", implementation_guide_pt="Migrar todas as credenciais para um cofre seguro como HashiCorp Vault.", implementation_guide_en="Migrate all credentials to a secure vault like HashiCorp Vault.", references=["https://cheatsheetseries.owasp.org/cheatsheets/Credential_Management_Cheat_Sheet.html"], vulnerability_cwe_ids=["CWE-798"]),
    ]
    await KBCountermeasure.insert_many(countermeasures)

    return len(vulns) + len(countermeasures)


async def list_vulnerabilities(
    filter_by: Optional[VulnerabilityFilter] = None,
    skip: int = 0,
    limit: int = 50,
    lang: str = "pt-BR",
) -> Tuple[List[KBVulnerability], int]:
    query: Dict = {}
    if filter_by:
        if filter_by.component:
            query["affected_components"] = filter_by.component
        if filter_by.cwe:
            query["cwe"] = filter_by.cwe
        if filter_by.min_cvss is not None:
            query["cvss_score"] = {"$gte": filter_by.min_cvss}
        if filter_by.search:
            query["$or"] = [
                {"title": {"$regex": filter_by.search, "$options": "i"}},
                {"description": {"$regex": filter_by.search, "$options": "i"}},
            ]

    total = await KBVulnerability.find(query).count()
    items = (
        await KBVulnerability.find(query)
        .sort(-KBVulnerability.created_at)
        .skip(skip)
        .limit(limit)
        .to_list()
    )
    return items, total


async def list_countermeasures(
    cwe_ids: Optional[List[str]] = None,
    skip: int = 0,
    limit: int = 50,
    lang: str = "pt-BR",
) -> Tuple[List[KBCountermeasure], int]:
    query: Dict = {}
    if cwe_ids:
        query["vulnerability_cwe_ids"] = {"$in": cwe_ids}

    total = await KBCountermeasure.find(query).count()
    items = (
        await KBCountermeasure.find(query)
        .sort(-KBCountermeasure.created_at)
        .skip(skip)
        .limit(limit)
        .to_list()
    )
    return items, total


async def get_vulnerabilities_for_component(label: str) -> List[KBVulnerability]:
    items, _ = await list_vulnerabilities(
        filter_by=VulnerabilityFilter(component=label),
        limit=100,
    )
    return items


async def get_countermeasures_for_vulnerabilities(vulns: List[KBVulnerability]) -> List[KBCountermeasure]:
    cwe_ids = [v.cwe for v in vulns if v.cwe]
    if not cwe_ids:
        return []
    items, _ = await list_countermeasures(cwe_ids=cwe_ids, limit=100)
    return items
