# Low-Level Design Document (LLD)
## Data Modification Program

### 1. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GUI Layer (View)                     │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │ File     │ Unit     │ Data     │ Visualization    │ │
│  │ Loader   │ Config   │ Selection│ Panel            │ │
│  │ Widget   │ Widget   │ Widget   │ Widget           │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│              Controller Layer (Logic)                   │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │ File     │ Data     │ Unit     │ Graph            │ │
│  │ Handler  │ Processor│ Converter│ Generator        │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                 Model Layer (Data)                      │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │ Data     │ Config   │ History  │ Export           │ │
│  │ Manager  │ Manager  │ Manager  │ Manager          │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

### 2. Module Design

#### 2.1 GUI Layer Modules

##### 2.1.1 MainWindow (`main_window.py`)
```python
class MainWindow:
    """
    Main application window with MVC pattern
    """
    def __init__(self):
        self.root = tk.Tk()
        self.controller = ApplicationController()
        self.setup_ui()

    def setup_ui(self):
        # Initialize all widget panels

    def run(self):
        self.root.mainloop()
```

##### 2.1.2 FileLoaderWidget (`widgets/file_loader.py`)
```python
class FileLoaderWidget(tk.Frame):
    """
    File loading interface
    Components:
    - Browse button
    - File path display
    - Data preview table
    """
    def __init__(self, parent, controller):
        self.controller = controller
        self.file_path = tk.StringVar()

    def browse_file(self):
        # Open file dialog

    def load_file(self):
        # Trigger controller to load file

    def display_preview(self, data):
        # Show data in table widget
```

##### 2.1.3 UnitConfigWidget (`widgets/unit_config.py`)
```python
class UnitConfigWidget(tk.Frame):
    """
    Unit configuration interface
    Components:
    - Original unit dropdown/entry
    - Target unit dropdown/entry
    - Conversion factor display
    """
    def __init__(self, parent, controller):
        self.original_unit = tk.StringVar()
        self.target_unit = tk.StringVar()
        self.conversion_factor = tk.DoubleVar()

    def update_conversion_factor(self):
        # Calculate and display conversion factor
```

##### 2.1.4 DataSelectionWidget (`widgets/data_selection.py`)
```python
class DataSelectionWidget(tk.Frame):
    """
    Data range selection interface
    Components:
    - Column checkboxes
    - Row range selector
    - Selection preview
    """
    def __init__(self, parent, controller):
        self.selected_columns = []
        self.row_start = tk.IntVar()
        self.row_end = tk.IntVar()

    def get_selection(self):
        # Return selected data range
```

##### 2.1.5 ModificationWidget (`widgets/modification.py`)
```python
class ModificationWidget(tk.Frame):
    """
    Modification method interface
    Components:
    - Method dropdown (multiply, divide, add, subtract, convert)
    - Value input
    - Preview button
    - Execute button
    """
    def __init__(self, parent, controller):
        self.method = tk.StringVar()
        self.value = tk.DoubleVar()

    def preview_modification(self):
        # Show preview of modifications

    def execute_modification(self):
        # Apply modifications
```

##### 2.1.6 VisualizationWidget (`widgets/visualization.py`)
```python
class VisualizationWidget(tk.Frame):
    """
    Graph and statistics display
    Components:
    - Matplotlib canvas
    - Before/after comparison
    - Statistics table
    """
    def __init__(self, parent, controller):
        self.figure = plt.Figure()
        self.canvas = FigureCanvasTkAgg(self.figure, self)

    def plot_comparison(self, before_data, after_data):
        # Create before/after comparison graphs

    def display_statistics(self, stats):
        # Show statistical summary
```

##### 2.1.7 SaveWidget (`widgets/save_panel.py`)
```python
class SaveWidget(tk.Frame):
    """
    Save and export interface
    Components:
    - Save button
    - Export graph button
    - Format selection
    """
    def __init__(self, parent, controller):
        self.save_format = tk.StringVar(value='xlsx')

    def save_data(self):
        # Save modified data

    def export_graph(self):
        # Export visualization as image
```

---

#### 2.2 Controller Layer Modules

##### 2.2.1 ApplicationController (`controllers/app_controller.py`)
```python
class ApplicationController:
    """
    Main application controller
    Coordinates all operations
    """
    def __init__(self):
        self.data_manager = DataManager()
        self.file_handler = FileHandler()
        self.data_processor = DataProcessor()
        self.unit_converter = UnitConverter()
        self.graph_generator = GraphGenerator()

    def load_file(self, file_path):
        # Load file and update data manager

    def apply_modification(self, method, params):
        # Process data modification

    def save_file(self, file_path, format):
        # Save modified data
```

##### 2.2.2 FileHandler (`controllers/file_handler.py`)
```python
class FileHandler:
    """
    File I/O operations
    """
    def load_excel(self, file_path):
        # Load Excel file using pandas

    def load_csv(self, file_path):
        # Load CSV file using pandas

    def save_excel(self, data, file_path):
        # Save to Excel

    def save_csv(self, data, file_path):
        # Save to CSV

    def validate_file(self, file_path):
        # Check file format and integrity
```

##### 2.2.3 DataProcessor (`controllers/data_processor.py`)
```python
class DataProcessor:
    """
    Data modification operations
    """
    def multiply(self, data, factor):
        # Multiply data by factor

    def divide(self, data, divisor):
        # Divide data by divisor

    def add(self, data, constant):
        # Add constant to data

    def subtract(self, data, constant):
        # Subtract constant from data

    def apply_custom_formula(self, data, formula):
        # Apply custom formula

    def round_data(self, data, decimals):
        # Round to specified decimal places
```

##### 2.2.4 UnitConverter (`controllers/unit_converter.py`)
```python
class UnitConverter:
    """
    Unit conversion logic
    """
    def __init__(self):
        self.conversion_table = self._load_conversion_table()

    def convert(self, value, from_unit, to_unit):
        # Convert value between units

    def get_conversion_factor(self, from_unit, to_unit):
        # Get conversion factor

    def _load_conversion_table(self):
        # Load predefined time unit conversion factors
        return {
            'time': {
                '초': {'분': 1/60, '시간': 1/3600, '일': 1/86400},
                '분': {'초': 60, '시간': 1/60, '일': 1/1440},
                '시간': {'초': 3600, '분': 60, '일': 1/24},
                '일': {'초': 86400, '분': 1440, '시간': 24}
            }
        }
```

##### 2.2.5 GraphGenerator (`controllers/graph_generator.py`)
```python
class GraphGenerator:
    """
    Visualization generation
    """
    def create_comparison_graph(self, before_data, after_data, chart_type):
        # Create before/after comparison

    def create_line_chart(self, data1, data2):
        # Line chart for time series

    def create_bar_chart(self, data1, data2):
        # Bar chart for categorical data

    def create_scatter_plot(self, data1, data2):
        # Scatter plot for distribution

    def calculate_statistics(self, data):
        # Calculate min, max, mean, std dev
        return {
            'min': data.min(),
            'max': data.max(),
            'mean': data.mean(),
            'std': data.std()
        }
```

---

#### 2.3 Model Layer Modules

##### 2.3.1 DataManager (`models/data_manager.py`)
```python
class DataManager:
    """
    Central data storage and state management
    """
    def __init__(self):
        self.original_data = None
        self.modified_data = None
        self.selected_columns = []
        self.selected_rows = (0, -1)
        self.current_file_path = None

    def set_data(self, data):
        # Set original data

    def get_data(self):
        # Get current data

    def get_selected_data(self):
        # Get data based on selection

    def update_modified_data(self, data):
        # Update modified data
```

##### 2.3.2 ConfigManager (`models/config_manager.py`)
```python
class ConfigManager:
    """
    Application configuration
    """
    def __init__(self):
        self.config = self._load_default_config()

    def _load_default_config(self):
        return {
            'max_file_size_mb': 100,
            'max_rows': 1000000,
            'max_columns': 100,
            'default_decimals': 2,
            'graph_dpi': 100,
            'theme': 'default'
        }

    def get(self, key):
        # Get configuration value

    def set(self, key, value):
        # Set configuration value
```

##### 2.3.3 HistoryManager (`models/history_manager.py`)
```python
class HistoryManager:
    """
    Undo/Redo functionality
    """
    def __init__(self):
        self.history = []
        self.current_index = -1

    def add_state(self, data):
        # Add data state to history

    def undo(self):
        # Revert to previous state

    def redo(self):
        # Move forward in history

    def can_undo(self):
        # Check if undo is available

    def can_redo(self):
        # Check if redo is available
```

##### 2.3.4 ExportManager (`models/export_manager.py`)
```python
class ExportManager:
    """
    Export functionality management
    """
    def export_data(self, data, file_path, format):
        # Export data to file

    def export_graph(self, figure, file_path, format):
        # Export matplotlib figure

    def generate_filename(self, base_name, extension):
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base_name}_{timestamp}.{extension}"
```

---

### 3. Data Flow

#### 3.1 File Loading Flow
```
User clicks Browse
    → FileLoaderWidget.browse_file()
    → ApplicationController.load_file(path)
    → FileHandler.load_excel(path) or load_csv(path)
    → DataManager.set_data(data)
    → FileLoaderWidget.display_preview(data)
```

#### 3.2 Modification Flow
```
User selects modification method and value
    → ModificationWidget.execute_modification()
    → ApplicationController.apply_modification(method, params)
    → DataManager.get_selected_data()
    → DataProcessor.[method](data, value)
    → DataManager.update_modified_data(result)
    → HistoryManager.add_state(original_data)
    → VisualizationWidget.plot_comparison(before, after)
    → VisualizationWidget.display_statistics(stats)
```

#### 3.3 Unit Conversion Flow
```
User sets original and target units
    → UnitConfigWidget.update_conversion_factor()
    → UnitConverter.get_conversion_factor(from, to)
    → UnitConfigWidget displays factor
User clicks Execute
    → UnitConverter.convert(data, from, to)
    → DataProcessor applies conversion
```

#### 3.4 Save Flow
```
User clicks Save
    → SaveWidget.save_data()
    → ApplicationController.save_file(path, format)
    → ExportManager.export_data(modified_data, path, format)
    → FileHandler.save_excel() or save_csv()
    → Success notification
```

---

### 4. Database/Storage Schema

#### 4.1 In-Memory Data Structure
```python
# DataManager internal structure
{
    'original_data': pd.DataFrame,
    'modified_data': pd.DataFrame,
    'metadata': {
        'file_name': str,
        'file_path': str,
        'load_time': datetime,
        'row_count': int,
        'column_count': int
    },
    'selection': {
        'columns': List[str],
        'rows': Tuple[int, int]
    },
    'units': {
        'original': str,
        'target': str,
        'conversion_factor': float
    }
}
```

#### 4.2 History Stack Structure
```python
# HistoryManager internal structure
[
    {
        'timestamp': datetime,
        'action': str,  # 'multiply', 'convert', etc.
        'data': pd.DataFrame,  # snapshot before action
        'params': dict  # action parameters
    },
    # ... more states
]
```

---

### 5. Algorithm Design

#### 5.1 Unit Conversion Algorithm (Time Units)
```python
def convert(value, from_unit, to_unit):
    """
    Direct conversion between time units
    Examples:
    - 초 → 분: value / 60
    - 분 → 시간: value / 60
    - 시간 → 일: value / 24
    - 일 → 초: value * 86400
    """
    # Direct lookup from conversion table
    conversion_factor = conversion_table['time'][from_unit][f'to_{to_unit}']

    # Apply conversion
    target_value = value * conversion_factor

    return target_value
```

#### 5.2 Data Validation Algorithm
```python
def validate_modification(data, method, value):
    """
    Validate modification parameters
    """
    # Check for numeric data
    if not pd.api.types.is_numeric_dtype(data):
        raise ValueError("Data must be numeric")

    # Check for division by zero
    if method == 'divide' and value == 0:
        raise ValueError("Cannot divide by zero")

    # Check for overflow
    if method == 'multiply':
        max_result = data.max() * value
        if max_result > sys.float_info.max:
            raise ValueError("Result would overflow")

    return True
```

#### 5.3 Graph Auto-Selection Algorithm
```python
def select_chart_type(data):
    """
    Auto-select appropriate chart type
    """
    # Check if data has datetime index
    if isinstance(data.index, pd.DatetimeIndex):
        return 'line_chart'

    # Check if data is categorical
    elif data.dtype == 'object' or data.dtype.name == 'category':
        return 'bar_chart'

    # Default to scatter for numeric data
    else:
        return 'scatter_plot'
```

---

### 6. Error Handling Strategy

#### 6.1 Error Categories
```python
class DataModificationError(Exception):
    """Base exception for data modification errors"""
    pass

class FileLoadError(DataModificationError):
    """File loading errors"""
    pass

class DataValidationError(DataModificationError):
    """Data validation errors"""
    pass

class ConversionError(DataModificationError):
    """Unit conversion errors"""
    pass

class ExportError(DataModificationError):
    """Data export errors"""
    pass
```

#### 6.2 Error Handling Flow
```python
def load_file_with_error_handling(file_path):
    try:
        data = pd.read_excel(file_path)
        return data
    except FileNotFoundError:
        show_error("파일을 찾을 수 없습니다.")
    except PermissionError:
        show_error("파일 접근 권한이 없습니다.")
    except Exception as e:
        show_error(f"파일 로드 중 오류 발생: {str(e)}")
        log_error(e)
    return None
```

---

### 7. Configuration Files

#### 7.1 Unit Conversion Configuration (`config/units.json`)
```json
{
  "time": {
    "초": {
      "base_factor": 1.0,
      "display": "초",
      "to_분": 0.016666667,
      "to_시간": 0.000277778,
      "to_일": 0.000011574
    },
    "분": {
      "base_factor": 60.0,
      "display": "분",
      "to_초": 60,
      "to_시간": 0.016666667,
      "to_일": 0.000694444
    },
    "시간": {
      "base_factor": 3600.0,
      "display": "시간",
      "to_초": 3600,
      "to_분": 60,
      "to_일": 0.041666667
    },
    "일": {
      "base_factor": 86400.0,
      "display": "일",
      "to_초": 86400,
      "to_분": 1440,
      "to_시간": 24
    }
  }
}
```

#### 7.2 Application Configuration (`config/app_config.json`)
```json
{
  "window": {
    "width": 1200,
    "height": 800,
    "title": "Data Modification Tool",
    "resizable": true
  },
  "limits": {
    "max_file_size_mb": 100,
    "max_rows": 1000000,
    "max_columns": 100
  },
  "defaults": {
    "decimal_places": 2,
    "graph_dpi": 100,
    "save_format": "xlsx"
  }
}
```

---

### 8. Build Configuration

#### 8.1 PyInstaller Spec File (`build.spec`)
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('assets', 'assets')
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'matplotlib',
        'openpyxl',
        'tkinter'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DataModificationTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)
```

---

### 9. Project File Structure

```
Data_modify/
├── main.py                      # Application entry point
├── build.spec                   # PyInstaller configuration
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
├── PRD.md                       # Product Requirements Document
├── LLD.md                       # Low-Level Design Document
├── Claude.md                    # Planning management
│
├── config/                      # Configuration files
│   ├── units.json              # Unit conversion data
│   └── app_config.json         # Application settings
│
├── assets/                      # Static resources
│   ├── icon.ico                # Application icon
│   └── images/                 # UI images
│
├── src/                        # Source code
│   ├── __init__.py
│   │
│   ├── gui/                    # GUI layer
│   │   ├── __init__.py
│   │   ├── main_window.py     # Main window
│   │   └── widgets/           # UI widgets
│   │       ├── __init__.py
│   │       ├── file_loader.py
│   │       ├── unit_config.py
│   │       ├── data_selection.py
│   │       ├── modification.py
│   │       ├── visualization.py
│   │       └── save_panel.py
│   │
│   ├── controllers/            # Controller layer
│   │   ├── __init__.py
│   │   ├── app_controller.py
│   │   ├── file_handler.py
│   │   ├── data_processor.py
│   │   ├── unit_converter.py
│   │   └── graph_generator.py
│   │
│   ├── models/                 # Model layer
│   │   ├── __init__.py
│   │   ├── data_manager.py
│   │   ├── config_manager.py
│   │   ├── history_manager.py
│   │   └── export_manager.py
│   │
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── validators.py      # Data validation
│       ├── logger.py          # Logging utilities
│       └── exceptions.py      # Custom exceptions
│
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── test_file_handler.py
│   ├── test_data_processor.py
│   ├── test_unit_converter.py
│   └── test_graph_generator.py
│
└── dist/                       # Build output directory
    └── DataModificationTool.exe
```

---

### 10. API Documentation

#### 10.1 DataProcessor API
```python
class DataProcessor:
    def multiply(self, data: pd.Series, factor: float) -> pd.Series:
        """
        Multiply data by a factor

        Args:
            data: Pandas Series with numeric data
            factor: Multiplication factor

        Returns:
            Modified Pandas Series

        Raises:
            DataValidationError: If data is not numeric
        """
        pass
```

#### 10.2 UnitConverter API
```python
class UnitConverter:
    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert value between units

        Args:
            value: Numeric value to convert
            from_unit: Source unit (e.g., 'cm')
            to_unit: Target unit (e.g., 'm')

        Returns:
            Converted value

        Raises:
            ConversionError: If units are incompatible
        """
        pass
```

---

### 11. Performance Optimization

#### 11.1 Data Processing Optimization
- Use pandas vectorized operations instead of loops
- Implement lazy loading for large files
- Use chunking for files > 50MB
- Cache frequently accessed data

#### 11.2 GUI Optimization
- Use threading for long operations
- Implement progress bars for file loading
- Lazy render graphs (only when visible)
- Debounce user input events

#### 11.3 Memory Management
- Clear data from memory after save
- Limit history stack to 10 states
- Release matplotlib figures after export
- Use garbage collection for large data

---

### 12. Testing Strategy

#### 12.1 Unit Testing
- Test each controller method independently
- Mock file I/O operations
- Test edge cases (empty data, invalid units, etc.)
- Validate error handling

#### 12.2 Integration Testing
- Test complete workflows (load → modify → save)
- Test GUI interactions
- Validate data integrity throughout process

#### 12.3 Performance Testing
- Test with files of various sizes (1KB to 100MB)
- Measure operation times
- Validate memory usage

---

**Document Version**: 1.1
**Last Updated**: 2025-11-27
**Revision Notes**:
- Updated unit conversion system to time-based only (초, 분, 시간, 일)
- Simplified conversion table and algorithm
- Updated configuration files to reflect time units
**Status**: Draft → Review → Approved
