# Department Tree View Feature

## Overview
The Department component now supports two view modes:
1. **List View** - Traditional table view showing all departments
2. **Tree View** - Hierarchical view showing department relationships

## Features

### View Toggle
- Switch between List and Tree views using the toggle buttons in the top-right corner
- List view shows departments in a traditional table format
- Tree view shows departments in a hierarchical structure

### Tree View Functionality
- **Hierarchical Display**: Shows parent-child relationships between departments
- **Expandable Nodes**: Click the expand/collapse icons to show/hide sub-departments
- **Clickable Department Names**: Click on any department name to view its details
- **Split View**: When a department is selected, its details appear in a panel to the right
- **Security Level Display**: Shows security level next to each department name

### Split View Details Panel
When a department is clicked in tree view, the right panel shows:
- Department basic information (Security Level, ID)
- List of sub-departments (if any)
- List of employees in that department (up to 5, with count if more)
- Close button to hide the details panel

### Enhanced Forms
- **Create Department**: Now includes parent department selection
- **Edit Department**: Can change parent department relationships
- **Show Department**: Displays parent department information and has tabs for:
  - Sub-Departments: Shows child departments with add button
  - Employee List: Shows employees in this department

## Technical Implementation

### Dependencies Added
- `@mui/x-tree-view`: Provides TreeView and TreeItem components
- Enhanced MUI components for better UI

### Key Components
- `DepartmentTreeView`: Main tree component
- `DepartmentTreeItem`: Recursive tree item for hierarchy
- `DepartmentDetails`: Details panel for split view
- `AddSubDepartmentButton`: Button to create sub-departments

### API Integration
- Uses `useGetList` hook to fetch department hierarchies
- Filters departments by `DepartmentId` to build tree structure
- Supports real-time data updates

## Usage
1. Navigate to the Departments section
2. Use the toggle buttons to switch between List and Tree views
3. In Tree view:
   - Expand/collapse departments to explore hierarchy
   - Click department names to view details
   - Use the split view to see department information
   - Create sub-departments using the "Add Sub-Department" button

## Benefits
- **Better Organization**: Visualize department hierarchy clearly
- **Improved Navigation**: Quick access to related departments
- **Enhanced UX**: Split view allows comparing departments
- **Efficient Management**: Easy creation of sub-departments
