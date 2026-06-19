/* ============================================================
   Canal de Denúncias Corporativo — Midrah Investimentos
   Estrutura para SQL Server (migração do servidor "depois")
   Atende à Lei nº 14.457/2022 e à LGPD (Lei nº 13.709/2018):
   sigilo, denúncia anônima ou identificada, protocolo, status
   da apuração, registro de tratativas e LOG DE ACESSOS.
   ============================================================ */

------------------------------------------------------------
-- 0) Banco / schema dedicado (opcional, recomendado)
------------------------------------------------------------
-- CREATE DATABASE CanalDenuncias;
-- GO
-- USE CanalDenuncias;
-- GO

IF SCHEMA_ID('denuncia') IS NULL
    EXEC('CREATE SCHEMA denuncia');
GO

------------------------------------------------------------
-- 1) Tabela principal de denúncias
------------------------------------------------------------
IF OBJECT_ID('denuncia.Denuncias','U') IS NULL
CREATE TABLE denuncia.Denuncias
(
    DenunciaId        INT IDENTITY(1,1)   NOT NULL PRIMARY KEY,
    Protocolo         VARCHAR(20)         NOT NULL UNIQUE,          -- ex.: MID-2026-000001
    RegistradoEm      DATETIME2(0)        NOT NULL CONSTRAINT DF_Den_RegEm DEFAULT (SYSDATETIME()),

    -- Modo da denúncia
    Anonima           BIT                 NOT NULL CONSTRAINT DF_Den_Anon DEFAULT (1),

    -- Dados da ocorrência (obrigatórios no formulário)
    TipoOcorrencia    NVARCHAR(80)        NOT NULL,                 -- Assédio sexual / moral / Discriminação / ...
    DataOcorrencia    DATE                NULL,
    LocalSetor        NVARCHAR(200)       NULL,
    PessoasEnvolvidas NVARCHAR(MAX)       NOT NULL,
    Descricao         NVARCHAR(MAX)       NOT NULL,

    -- Identificação do denunciante (OPCIONAL — pode ser nula/anônima)
    Nome              NVARCHAR(200)       NULL,
    Email             NVARCHAR(200)       NULL,
    Telefone          NVARCHAR(40)        NULL,
    CargoSetor        NVARCHAR(120)       NULL,

    -- Controle da apuração
    Status            VARCHAR(20)         NOT NULL CONSTRAINT DF_Den_Status DEFAULT ('Recebida'),
                                          -- Recebida | Em apuração | Concluída | Arquivada | Improcedente
    Responsavel       NVARCHAR(200)       NULL,
    DataConclusao     DATE                NULL,
    Observacoes       NVARCHAR(MAX)       NULL,

    CONSTRAINT CK_Den_Status CHECK
        (Status IN ('Recebida','Em apuração','Concluída','Arquivada','Improcedente'))
);
GO

------------------------------------------------------------
-- 2) Anexos / evidências (1 denúncia : N anexos)
------------------------------------------------------------
IF OBJECT_ID('denuncia.DenunciaAnexos','U') IS NULL
CREATE TABLE denuncia.DenunciaAnexos
(
    AnexoId       INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    DenunciaId    INT               NOT NULL,
    NomeArquivo   NVARCHAR(260)     NOT NULL,
    TipoMime      NVARCHAR(120)     NULL,
    TamanhoBytes  BIGINT            NULL,
    Caminho       NVARCHAR(500)     NULL,        -- caminho em disco/servidor de arquivos...
    Conteudo      VARBINARY(MAX)    NULL,        -- ...ou guarde o binário aqui (escolha um)
    CriadoEm      DATETIME2(0)      NOT NULL CONSTRAINT DF_Anx_Em DEFAULT (SYSDATETIME()),
    CONSTRAINT FK_Anx_Den FOREIGN KEY (DenunciaId)
        REFERENCES denuncia.Denuncias(DenunciaId) ON DELETE CASCADE
);
GO

------------------------------------------------------------
-- 3) Tratativas / histórico da apuração (auditoria das ações)
------------------------------------------------------------
IF OBJECT_ID('denuncia.DenunciaTratativas','U') IS NULL
CREATE TABLE denuncia.DenunciaTratativas
(
    TratativaId   INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    DenunciaId    INT               NOT NULL,
    DataHora      DATETIME2(0)      NOT NULL CONSTRAINT DF_Trt_Em DEFAULT (SYSDATETIME()),
    Usuario       NVARCHAR(200)     NOT NULL,   -- quem registrou a ação (RH/Diretoria)
    StatusNovo    VARCHAR(20)       NULL,
    Acao          NVARCHAR(MAX)     NOT NULL,   -- descrição da tratativa realizada
    CONSTRAINT FK_Trt_Den FOREIGN KEY (DenunciaId)
        REFERENCES denuncia.Denuncias(DenunciaId) ON DELETE CASCADE
);
GO

------------------------------------------------------------
-- 4) LOG DE ACESSOS (exigência: registro de histórico de acessos)
--    Registra quem ABRIU/visualizou cada denúncia. NÃO registra IP
--    do denunciante, para preservar a anonimidade.
------------------------------------------------------------
IF OBJECT_ID('denuncia.LogAcessos','U') IS NULL
CREATE TABLE denuncia.LogAcessos
(
    LogId       BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    DenunciaId  INT                  NULL,        -- nulo = listagem geral
    Usuario     NVARCHAR(200)        NOT NULL,
    Acao        VARCHAR(30)          NOT NULL,    -- VISUALIZOU | EXPORTOU | EDITOU | ...
    DataHora    DATETIME2(0)         NOT NULL CONSTRAINT DF_Log_Em DEFAULT (SYSDATETIME())
);
GO

------------------------------------------------------------
-- 5) Controle de acesso por perfil (RH e Diretoria)
--    Crie um role e conceda permissão APENAS a esse role.
------------------------------------------------------------
IF DATABASE_PRINCIPAL_ID('RH_Diretoria') IS NULL
    CREATE ROLE RH_Diretoria;
GO
GRANT SELECT, INSERT, UPDATE ON SCHEMA::denuncia TO RH_Diretoria;
-- Exemplo: adicionar usuários autorizados ao role
-- ALTER ROLE RH_Diretoria ADD MEMBER [DOMINIO\usuario.rh];
-- ALTER ROLE RH_Diretoria ADD MEMBER [DOMINIO\diretor];
GO

------------------------------------------------------------
-- 6) View resumida para acompanhamento (esconde a descrição completa)
------------------------------------------------------------
IF OBJECT_ID('denuncia.vw_Painel','V') IS NOT NULL DROP VIEW denuncia.vw_Painel;
GO
CREATE VIEW denuncia.vw_Painel AS
SELECT  Protocolo, RegistradoEm,
        CASE WHEN Anonima = 1 THEN 'Anônima' ELSE 'Identificada' END AS Modo,
        TipoOcorrencia, DataOcorrencia, Status, Responsavel, DataConclusao
FROM    denuncia.Denuncias;
GO

/* ============================================================
   INSERT de exemplo (como o backend grava cada denúncia):

   INSERT INTO denuncia.Denuncias
     (Protocolo, Anonima, TipoOcorrencia, DataOcorrencia, LocalSetor,
      PessoasEnvolvidas, Descricao, Nome, Email, Telefone, CargoSetor)
   VALUES
     ('MID-2026-000001', 1, N'Assédio moral', '2026-06-10', N'Setor comercial',
      N'Descrição das pessoas...', N'Relato dos fatos...', NULL, NULL, NULL, NULL);
   ============================================================ */
