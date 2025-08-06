# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- N/A

### Changed

- Minor code refactoring

### Removed

- N/A

### Fixed

- Wait for Zwift to start on Windows and Linux

## [0.1.1] - 2025-08-03

Fixed path bug on Windows.

### Fixed

- Fixed path bug on Windows preventing activities being found.

## [0.1.0] - 2025-08-02

This is the initial pre-release with minimum functionality needed to
be useful. It has been tested to work on Linux and Windows.

### Added

- Authorise via callback server and automatically renew thereafter.
- Support both Linux (Zwift on Linux) and Windows.
- Upload activities and maintain a JSON-based database of them.
- Runs in either Terminal or Command Line. Needs to be launched from
the Terminal on Linux.
