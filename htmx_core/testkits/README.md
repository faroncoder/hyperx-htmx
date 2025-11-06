# S5Portal TestKits Framework

## Overview

The S5Portal TestKits Framework provides comprehensive testing tools for Django applications, with specialized focus on HTMX Core components. This framework transforms previous analysis scripts into proper, reusable TestKit classes with enhanced reporting and visualization capabilities.

## Features

- **🔍 Discovery TestKit**: Component discovery and functionality testing using os.walk()
- **📊 Analysis TestKit**: Key component integration testing and health assessment
- **🗑️ Orphaned Files TestKit**: File usage analysis and cleanup detection
- **📋 Comprehensive Reporting**: JSON and Markdown reports with visualization
- **🚀 Easy Execution**: Multiple ways to run tests with flexible configuration

## Quick Start

### 1. Run All TestKits
```bash
python run_testkits.py all
```

### 2. Run Specific TestKit
```bash
python run_testkits.py discovery
python run_testkits.py analysis  
python run_testkits.py orphaned
```

### 3. List Available TestKits
```bash
python run_testkits.py list
```

## TestKits Available

### HTMX Core Discovery Kit
- **Purpose**: Comprehensive component discovery and functionality testing
- **Features**: File discovery using os.walk(), component analysis, import testing, class instantiation
- **Based on**: Original `test_htmx_core_discovery.py`

### HTMX Core Analysis Kit  
- **Purpose**: Enhanced analysis focusing on key component integration
- **Features**: Critical component loading, TabRegistry testing, XTabSystem validation, middleware integration
- **Based on**: Original `htmx_core_analysis.py`

### Orphaned Files Detection Kit
- **Purpose**: File usage analysis and cleanup detection
- **Features**: Import graph analysis, usage pattern detection, cleanup recommendations
- **Based on**: Original `detect_orphaned_files.py`

## Advanced Usage

### Using the TestKit Runner Directly
```python
from testkits.runner import TestKitRunner

runner = TestKitRunner()
runner.run_all()  # Run all TestKits
runner.run_specific(['discovery', 'analysis'])  # Run specific TestKits
```

### Using Individual TestKits
```python
import unittest
from testkits.htmx_core.discovery_kit import HTMXCoreDiscoveryKit

# Create and run test suite
suite = unittest.TestLoader().loadTestsFromTestCase(HTMXCoreDiscoveryKit)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
```

## Reports and Output

### Report Files
All TestKit runs generate reports in `testkits/reports/`:
- **JSON Reports**: Machine-readable test results and metrics
- **Markdown Reports**: Human-readable summaries and analysis
- **Summary Reports**: Cross-TestKit analysis and trends

### Report Structure
Each report includes:
- Test execution summary
- Individual test results  
- Performance metrics
- Component analysis
- Recommendations and insights

## Framework Architecture

```
testkits/
├── __init__.py                 # Main package
├── config.py                   # Configuration settings
├── runner.py                   # Main TestKit runner
├── common/                     # Shared utilities
│   ├── base_testkit.py        # Base TestKit class
│   └── reporter.py            # Advanced reporting
├── htmx_core/                 # HTMX-specific TestKits
│   ├── discovery_kit.py       # Discovery TestKit
│   ├── analysis_kit.py        # Analysis TestKit
│   └── orphaned_files_kit.py  # Orphaned Files TestKit
└── reports/                   # Generated reports
```

## Configuration

Edit `testkits/config.py` to customize:
- File discovery patterns
- Analysis thresholds
- Report settings
- TestKit-specific options

## Requirements

- Python 3.7+
- Django (configured in project)
- Standard library modules (unittest, ast, pathlib, etc.)
- Optional: matplotlib, seaborn for advanced visualizations

## Example Output

```
🧪 S5PORTAL TESTKITS - COMPREHENSIVE TESTING SUITE
==================================================================
🚀 RUNNING TESTKIT: DISCOVERY
==================================================================
🔍 Starting HTMX Core file discovery...
📊 Analyzing components in discovered files...
📦 Testing module imports...
🏗️ Testing class instantiation...
🔧 Testing function discovery...
⚡ Testing critical components...

============================================================
📋 HTMX CORE DISCOVERY SUMMARY
============================================================
Total Files Discovered: 51
Total Classes Found: 26  
Total Functions Found: 232
Working Classes: 15
Working Functions: 178
Import Success Rate: 73.2%
Overall Success Rate: 68.4%
System Health: Good
============================================================
```

## Contributing

To add new TestKits:

1. Create new TestKit class inheriting from `BaseTestKit`
2. Implement test methods following naming convention `test_*`
3. Add TestKit to runner's `available_kits` dictionary
4. Update documentation

## License

Part of the S5Portal project. See project license for details.