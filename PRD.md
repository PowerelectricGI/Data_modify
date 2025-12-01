# Product Requirements Document (PRD)
## Data Modification Program

### 1. Product Overview

**Product Name**: Data Modification Tool
**Version**: 1.0.0
**Target Platform**: Windows Desktop Application (.exe)
**Technology Stack**: Python (GUI + Data Processing)

**Purpose**: A desktop application that allows users to load data files, convert units, modify data ranges, visualize changes, and save results.

---

### 2. Target Users

- **Primary Users**: Data analysts, researchers, engineers
- **Use Cases**:
  - Time unit conversion for temporal data
  - Bulk data transformation
  - Time-series data preprocessing
  - Quality assurance and data validation

---

### 3. Core Features

#### 3.1 Data Loading
- **FR-1.1**: Support Excel files (.xlsx, .xls)
- **FR-1.2**: Support CSV and text files (.csv, .txt)
- **FR-1.3**: Display loaded data in table format
- **FR-1.4**: Show data preview with column headers
- **FR-1.5**: Validate file format before loading

#### 3.2 Unit Configuration (Time-Based Only)
- **FR-2.1**: Input field for original data unit
- **FR-2.2**: Input field for target unit
- **FR-2.3**: Support time unit types only:
  - 초 (second)
  - 분 (minute)
  - 시간 (hour)
  - 일 (day)
  - Custom time factor (user-defined conversion factor)
- **FR-2.4**: Auto-suggest time unit conversions
- **FR-2.5**: Display conversion factor between time units

#### 3.3 Data Range Selection
- **FR-3.1**: Select specific columns for modification
- **FR-3.2**: Select specific rows (range or all)
- **FR-3.3**: Visual selection interface (checkbox/dropdown)
- **FR-3.4**: Preview selected data range
- **FR-3.5**: Support multiple column selection

#### 3.4 Modification Methods
- **FR-4.1**: Multiplication by factor
- **FR-4.2**: Division by factor
- **FR-4.3**: Addition of constant
- **FR-4.4**: Subtraction of constant
- **FR-4.5**: Unit conversion (automatic calculation)
- **FR-4.6**: Custom formula input
- **FR-4.7**: Rounding options (decimal places)

#### 3.5 Execution and Visualization
- **FR-5.1**: Execute button to apply modifications
- **FR-5.2**: Before/after comparison table
- **FR-5.3**: Before/after comparison graph:
  - Line chart for time series data
  - Bar chart for categorical data
  - Scatter plot for distribution comparison
- **FR-5.4**: Statistical summary (min, max, mean, std dev)
- **FR-5.5**: Undo/Redo functionality
- **FR-5.6**: Real-time preview of modifications

#### 3.6 Save Functionality
- **FR-6.1**: Save button to export modified data
- **FR-6.2**: Save as Excel (.xlsx)
- **FR-6.3**: Save as CSV (.csv)
- **FR-6.4**: Save with timestamp in filename
- **FR-6.5**: Preserve original file option
- **FR-6.6**: Export graph as image (PNG, PDF)

---

### 4. Non-Functional Requirements

#### 4.1 Performance
- **NFR-1.1**: Load files up to 100MB within 5 seconds
- **NFR-1.2**: Process data modifications within 2 seconds for 10,000 rows
- **NFR-1.3**: Graph rendering within 1 second

#### 4.2 Usability
- **NFR-2.1**: Intuitive GUI with clear workflow
- **NFR-2.2**: Korean language support (primary)
- **NFR-2.3**: Tooltips and help text for all features
- **NFR-2.4**: Error messages in user-friendly language

#### 4.3 Reliability
- **NFR-3.1**: Data validation to prevent invalid operations
- **NFR-3.2**: Error handling for file I/O operations
- **NFR-3.3**: Automatic backup before modifications
- **NFR-3.4**: Crash recovery mechanism

#### 4.4 Deployment
- **NFR-4.1**: Single .exe file (no installation required)
- **NFR-4.2**: Windows 10/11 compatibility
- **NFR-4.3**: File size < 100MB
- **NFR-4.4**: No external dependencies (bundled)

---

### 5. User Interface Requirements

#### 5.1 Main Window Layout
```
┌─────────────────────────────────────────────┐
│  Data Modification Tool           [_][□][X] │
├─────────────────────────────────────────────┤
│  1. Data Load                               │
│     [Load File]  [File Path Display]        │
│                                             │
│  2. Unit Configuration                      │
│     Original Unit: [____]  Target: [____]   │
│                                             │
│  3. Data Range Selection                    │
│     Columns: [Dropdown/Checkboxes]          │
│     Rows: [Range Selection]                 │
│                                             │
│  4. Modification Method                     │
│     Method: [Dropdown]  Value: [____]       │
│                                             │
│  5. Preview                                 │
│     [Data Table Preview]                    │
│                                             │
│     [Execute]  [Reset]                      │
│                                             │
│  6. Results                                 │
│     [Before/After Comparison Graph]         │
│     [Statistics Summary]                    │
│                                             │
│     [Save]  [Export Graph]                  │
└─────────────────────────────────────────────┘
```

#### 5.2 Color Scheme
- Primary: Professional blue (#2196F3)
- Secondary: Gray (#757575)
- Success: Green (#4CAF50)
- Warning: Orange (#FF9800)
- Error: Red (#F44336)

---

### 6. Data Requirements

#### 6.1 Supported Data Types
- Numeric: integers, floats
- Text: strings (for headers)
- Date/Time: ISO format support

#### 6.2 Data Constraints
- Maximum rows: 1,000,000
- Maximum columns: 100
- File size limit: 100MB

---

### 7. Technical Constraints

#### 7.1 Libraries to Use
- **GUI**: tkinter or PyQt5
- **Data Processing**: pandas, numpy
- **Visualization**: matplotlib, seaborn
- **File I/O**: openpyxl, csv
- **Packaging**: PyInstaller or cx_Freeze

#### 7.2 Python Version
- Python 3.8 or higher

---

### 8. Success Criteria

1. Users can load data files successfully with 99% success rate
2. Unit conversions are accurate to 6 decimal places
3. GUI is responsive (no freezing during operations)
4. Graphs are clear and informative
5. Save functionality preserves data integrity
6. .exe file runs on clean Windows systems without errors

---

### 9. Future Enhancements (Out of Scope for v1.0)

- Batch processing multiple files
- Cloud storage integration
- Advanced statistical analysis
- Multi-language support (English, Japanese)
- Plugin system for custom transformations
- Database connectivity

---

### 10. Acceptance Criteria

- [ ] All FR requirements implemented and tested
- [ ] All NFR requirements met
- [ ] .exe file generated successfully
- [ ] User testing completed with positive feedback
- [ ] Documentation complete (user manual)
- [ ] No critical bugs in testing phase

---

**Document Version**: 1.1
**Last Updated**: 2025-11-27
**Revision Notes**:
- Changed unit system to time-based only (초, 분, 시간, 일)
- .txt file support already included in FR-1.2
**Status**: Draft → Review → Approved
