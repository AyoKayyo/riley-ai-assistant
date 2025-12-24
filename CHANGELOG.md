# Changelog

All notable changes to Riley AI Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-24

### Added
- Initial release of Riley AI Assistant
- Conversational AI companion powered by llama3.1:8b
- Multi-agent architecture (Coder, Researcher, Executor, Vision)
- Code Generator UI with 8 language support
- Research Tool with web search and markdown export
- Terminal Widget for command execution
- Chat history database (SQLite)
- Settings panel for configuration
- File attachment support (PDF, images, text)
- Pure black & white UI design
- MIT License
- Professional README and documentation
- GitHub Actions for CI/CD and automated backups

### Technical Details
- Model: llama3.1:8b for conversation (4.9GB)
- Model: qwen2.5-coder:7b for code generation (4.7GB)
- Response time: 3-4 seconds
- Privacy: 100% local execution (except optional Gemini Architect)
- Platform: macOS (tested on M-series)

## [Unreleased]

### Planned
- Optimize deep memory (ChromaDB) for faster responses
- Keyboard shortcuts (Cmd+K, Cmd+Enter)
- Drag-drop file upload
- Export conversations as Markdown
- Voice input/output
- Custom agent marketplace
