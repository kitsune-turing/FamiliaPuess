-- Permitir que un dispositivo exista sin sede asignada (auto-registro).
ALTER TABLE dispositivo ALTER COLUMN id_sede DROP NOT NULL;
