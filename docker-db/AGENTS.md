# Database Setup

## Purpose

Database setup and initialization SQL for CVBooster.

Used during local deployment or external database setup.

## Ownership

- Database/schema owner
- Owns `docker-db/setup.sql`
- Defines required tables, extensions, and initial schema

## Local Contracts

- `setup.sql` contains the authoritative database initialization script
- SQL is run manually in the target database or during local setup
- Do not include secrets in SQL scripts

## Work Guidance

- Update `setup.sql` when database schema changes
- Keep scripts idempotent where possible
- Document required extensions or privileges if they change

## Verification

- Review `docker-db/setup.sql` for syntax before running
- Run in a disposable/local database when changing schema

## Child DOX Index

No child DOX files yet.
