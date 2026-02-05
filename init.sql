-- Script de inicialização do banco de dados
-- Usado para inicializar configurações do banco

USE glpi_manutencao;

-- Garantir character set UTF-8
ALTER DATABASE glpi_manutencao CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- As tabelas serão criadas automaticamente pelo SQLAlchemy
-- Este arquivo existe apenas para garantir configurações iniciais

SELECT 'Database glpi_manutencao initialized successfully' AS message;
