# Claude Project Planning - Data Modification Tool

## Project Overview
**Project Name**: Data Modification Tool
**Technology**: Python (tkinter/PyQt5 + pandas + matplotlib)
**Deployment**: Windows .exe (PyInstaller)
**Status**: Planning Phase
**Created**: 2025-11-27

---

## Project Goals
1. Create a desktop application for data modification with GUI
2. Support data loading (Excel, CSV, TXT)
3. Implement unit conversion functionality
4. Provide data modification operations (multiply, divide, add, subtract)
5. Visualize before/after comparison with graphs
6. Export modified data and graphs
7. Package as standalone .exe for Windows distribution

---

## Documentation Structure
- **PRD.md**: Product Requirements Document (완료 ✅)
- **LLD.md**: Low-Level Design Document (완료 ✅)
- **Claude.md**: This planning management document (완료 ✅)

---

## Development Phases

### Phase 1: Planning & Design ✅
- [x] Analyze requirements from PDF
- [x] Create PRD.md with functional/non-functional requirements
- [x] Create LLD.md with architecture and module design
- [x] Define project structure and file organization

**Status**: Completed
**Completion Date**: 2025-11-27

---

### Phase 2: Environment Setup (Next)
- [ ] Set up Python virtual environment
- [ ] Install required dependencies (pandas, numpy, matplotlib, openpyxl, tkinter/PyQt5)
- [ ] Create project directory structure
- [ ] Set up version control (.gitignore for Python)
- [ ] Create requirements.txt

**Dependencies to Install**:
```
pandas>=1.5.0
numpy>=1.24.0
matplotlib>=3.7.0
openpyxl>=3.1.0
pyinstaller>=5.0.0
```

**Estimated Time**: 1 hour

---

### Phase 3: Model Layer Implementation
- [ ] Implement DataManager (models/data_manager.py)
- [ ] Implement ConfigManager (models/config_manager.py)
- [ ] Implement HistoryManager (models/history_manager.py)
- [ ] Implement ExportManager (models/export_manager.py)
- [ ] Create unit tests for model layer

**Key Deliverables**:
- In-memory data structure
- Configuration management
- Undo/redo functionality
- Export functionality

**Estimated Time**: 6-8 hours

---

### Phase 4: Controller Layer Implementation
- [ ] Implement FileHandler (controllers/file_handler.py)
- [ ] Implement DataProcessor (controllers/data_processor.py)
- [ ] Implement UnitConverter (controllers/unit_converter.py)
- [ ] Implement GraphGenerator (controllers/graph_generator.py)
- [ ] Implement ApplicationController (controllers/app_controller.py)
- [ ] Create unit tests for controller layer

**Key Deliverables**:
- File I/O operations (Excel, CSV, TXT)
- Data modification algorithms
- Unit conversion logic
- Graph generation functionality

**Estimated Time**: 10-12 hours

---

### Phase 5: GUI Layer Implementation
- [ ] Choose GUI framework (tkinter vs PyQt5)
- [ ] Implement MainWindow (gui/main_window.py)
- [ ] Implement FileLoaderWidget (gui/widgets/file_loader.py)
- [ ] Implement UnitConfigWidget (gui/widgets/unit_config.py)
- [ ] Implement DataSelectionWidget (gui/widgets/data_selection.py)
- [ ] Implement ModificationWidget (gui/widgets/modification.py)
- [ ] Implement VisualizationWidget (gui/widgets/visualization.py)
- [ ] Implement SaveWidget (gui/widgets/save_panel.py)
- [ ] Integrate all widgets into MainWindow

**Key Deliverables**:
- Complete GUI interface
- Widget integration
- Event handling
- User input validation

**Estimated Time**: 15-20 hours

---

### Phase 6: Integration & Testing
- [ ] Integrate all layers (Model-Controller-View)
- [ ] Test complete workflows:
  - [ ] Load Excel → Modify → Save
  - [ ] Load CSV → Unit Convert → Visualize → Export
  - [ ] Undo/Redo functionality
  - [ ] Error handling scenarios
- [ ] Performance testing with large files
- [ ] UI/UX testing and refinement

**Test Scenarios**:
1. Small file (< 1MB, 100 rows)
2. Medium file (10MB, 10K rows)
3. Large file (50MB, 100K rows)
4. Invalid file formats
5. Division by zero
6. Invalid unit conversions

**Estimated Time**: 8-10 hours

---

### Phase 7: Configuration & Assets
- [ ] Create config/units.json (unit conversion data)
- [ ] Create config/app_config.json (application settings)
- [ ] Design application icon (icon.ico)
- [ ] Create README.md for users
- [ ] Create user manual (Korean)

**Estimated Time**: 4-5 hours

---

### Phase 8: Build & Packaging
- [ ] Create build.spec for PyInstaller
- [ ] Test .exe build process
- [ ] Optimize executable size
- [ ] Test on clean Windows machine
- [ ] Create installer (optional)

**Build Command**:
```bash
pyinstaller build.spec
```

**Target**:
- Single .exe file
- Size < 100MB
- No external dependencies required

**Estimated Time**: 3-4 hours

---

### Phase 9: Documentation & Deployment
- [ ] Finalize user manual
- [ ] Create installation guide
- [ ] Prepare release notes
- [ ] Version 1.0.0 release

**Estimated Time**: 2-3 hours

---

## Total Estimated Development Time
**50-65 hours** (approximately 1-2 weeks full-time or 2-4 weeks part-time)

---

## Technical Decisions

### GUI Framework Decision
**Options**:
1. **tkinter** (Recommended)
   - Pros: Built-in, lightweight, simple
   - Cons: Less modern UI, limited widgets
2. **PyQt5**
   - Pros: Modern UI, rich widgets, professional look
   - Cons: Larger .exe size, licensing considerations

**Decision**: To be determined in Phase 5
**Recommendation**: tkinter for simplicity and smaller .exe size

---

### Unit Conversion Strategy (Time Units Only)
**Approach**: Direct conversion between time units
- **Supported Units**: 초 (second), 분 (minute), 시간 (hour), 일 (day)
- **Conversion Examples**:
  - 초 → 분: value / 60
  - 분 → 시간: value / 60
  - 시간 → 일: value / 24
  - 일 → 초: value * 86400

**Advantages**:
- Simple and intuitive time conversions
- Clear conversion factors
- Easy to validate and test
- Focused scope reduces complexity

---

### Data Validation Strategy
**Validation Points**:
1. File loading: format, size, structure
2. User input: numeric values, unit compatibility
3. Modification operations: division by zero, overflow
4. Save operations: file permissions, disk space

**Error Handling**:
- Custom exception hierarchy
- User-friendly error messages in Korean
- Logging for debugging

---

## Risk Management

### Identified Risks

#### 1. Large File Performance
**Risk**: Slow performance with files > 50MB
**Mitigation**:
- Implement chunking for large files
- Add progress bars
- Use pandas optimization techniques
- Consider memory-mapped files

#### 2. .exe Size Too Large
**Risk**: Executable > 100MB
**Mitigation**:
- Use UPX compression
- Exclude unnecessary modules
- Consider PyInstaller optimization options

#### 3. Cross-Platform Compatibility
**Risk**: .exe only works on some Windows versions
**Mitigation**:
- Test on Windows 10 and 11
- Use compatible Python version (3.8+)
- Bundle all dependencies

#### 4. User Input Errors
**Risk**: Users enter invalid data
**Mitigation**:
- Input validation at every step
- Clear error messages
- Tooltips and help text
- Example values in placeholders

---

## Quality Assurance Checklist

### Functional Testing
- [ ] Data loading works for Excel, CSV, TXT
- [ ] Unit conversion calculations are accurate
- [ ] All modification operations work correctly
- [ ] Graphs display correctly (before/after comparison)
- [ ] Save functionality preserves data integrity
- [ ] Undo/Redo works properly
- [ ] Error handling displays appropriate messages

### Non-Functional Testing
- [ ] Loading 10MB file < 5 seconds
- [ ] Processing 10K rows < 2 seconds
- [ ] Graph rendering < 1 second
- [ ] .exe file size < 100MB
- [ ] No crashes on clean Windows 10/11

### UI/UX Testing
- [ ] All Korean text displays correctly
- [ ] Buttons and widgets are responsive
- [ ] Tooltips provide helpful information
- [ ] Workflow is intuitive
- [ ] Error messages are clear and actionable

---

## Milestones

### Milestone 1: Planning Complete ✅
**Date**: 2025-11-27
**Deliverables**: PRD.md, LLD.md, Claude.md

### Milestone 2: Core Functionality
**Target**: End of Week 1
**Deliverables**: Model + Controller layers working

### Milestone 3: GUI Complete
**Target**: End of Week 2
**Deliverables**: Full GUI with all widgets functional

### Milestone 4: Alpha Release
**Target**: End of Week 3
**Deliverables**: Integrated application, all features working

### Milestone 5: Beta Release
**Target**: End of Week 3.5
**Deliverables**: Tested .exe, documentation complete

### Milestone 6: v1.0 Release
**Target**: End of Week 4
**Deliverables**: Final .exe, user manual, deployment ready

---

## Next Actions

### Immediate Next Steps (Phase 2)
1. Create virtual environment: `python -m venv venv`
2. Activate environment: `venv\Scripts\activate` (Windows)
3. Create requirements.txt
4. Install dependencies: `pip install -r requirements.txt`
5. Create project directory structure
6. Initialize git repository

### Commands to Run
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Create requirements.txt
# (paste dependencies listed in Phase 2)

# Install dependencies
pip install -r requirements.txt

# Create directory structure
mkdir src\gui\widgets
mkdir src\controllers
mkdir src\models
mkdir src\utils
mkdir config
mkdir assets
mkdir tests

# Initialize git
git init
# Create .gitignore for Python
```

---

## Notes & Reminders

### Important Considerations
- All user-facing text should be in Korean
- Use consistent coding style (PEP 8)
- Add docstrings to all classes and methods
- Keep functions small and focused
- Write unit tests for all business logic

### Future Enhancements (v2.0)
- Batch processing multiple files
- Cloud storage integration (Google Drive, OneDrive)
- Advanced statistical analysis
- Multi-language support (English, Japanese)
- Plugin system for custom transformations
- Database connectivity (SQL, MongoDB)

---

## Session Log

### Session 1: 2025-11-27 (Initial Planning)
**Activities**:
- Analyzed PDF requirements document
- Created PRD.md with comprehensive requirements
- Created LLD.md with system architecture and module design
- Created Claude.md for project planning

**Outcomes**:
- Planning phase complete ✅
- Clear roadmap established
- Ready to begin implementation

---

### Session 2: 2025-11-27 (Requirements Update)
**Activities**:
- Updated unit system to time-based only (초, 분, 시간, 일)
- Confirmed .txt file support already included
- Updated PRD.md v1.1 with time unit specifications
- Updated LLD.md v1.1 with simplified conversion logic
- Updated Claude.md with new unit conversion strategy

**Changes Made**:
- ✅ Removed all non-time units (length, weight, temperature, volume)
- ✅ Simplified to 4 time units: 초, 분, 시간, 일
- ✅ Updated conversion algorithms and configuration files
- ✅ Reduced system complexity

**Outcomes**:
- Simplified scope ✅
- Clearer requirements ✅
- Reduced development complexity ✅

**Next Session**:
- Start Phase 2: Environment Setup
- Create project structure
- Install dependencies

---

## Contact & Support
**Developer**: Claude (AI Assistant)
**Project Repository**: C:\Users\kom69\Documents\GitHub\Data_modify
**Documentation**: PRD.md, LLD.md, Claude.md

---

**Last Updated**: 2025-11-27
**Document Version**: 1.1
**Revision Notes**:
- Updated requirements to time-based units only
- Simplified conversion strategy
- Session 2 updates incorporated
