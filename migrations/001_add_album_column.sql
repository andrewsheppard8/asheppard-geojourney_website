-- Migration 001: add album column to pictures

ALTER TABLE pictures
ADD COLUMN album TEXT;