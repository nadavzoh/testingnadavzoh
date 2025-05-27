# Lotus Application Architecture

## Overview

Lotus is a GUI application built with PyQt5 for managing and analyzing configuration files used in circuit design. The application focuses on Activity Factor (AF) and Mutual Exclusivity (Mutex) configuration files, providing a user-friendly interface to edit, validate, and analyze these files.

This document outlines the architectural design of the Lotus application, its component structure, design patterns employed, data flow, and the relationships between different modules.

## Core Architecture

The application follows a layered architecture with clear separation of concerns, primarily based on the Model-View-Controller (MVC) pattern:

- **Models**: Responsible for data representation and business logic
- **Views**: Handle the UI components and user interaction
- **Controllers**: Coordinate between Models and Views, implementing application logic

Additionally, several supporting layers provide specialized functionality:

- **Services**: Common utilities that provide core functionality across the application
- **Managers**: Handle specific aspects of the application like files, UI, tabs, and actions
- **Widgets**: Custom UI components used throughout the application
- **Factories**: Create complex objects according to specified requirements
- **Utils**: Utility functions and helper classes

## Directory Structure and Component Responsibilities

### Models (src/models/)

Models represent the data structures and business logic of the application:

- **AbstractLineModel.py**: Base class defining the interface for line models
- **AbstractDialogModel.py**: Base class for dialog models
- **AfLineModel.py**: Represents and validates a line in an AF configuration file
- **AfLineListModel.py**: Handles collections of AF lines for list views
- **AfDialogModel.py**: Model for the Activity Factor dialog, manages AF data and logic
- **DocumentModel.py**: Primary model representing a document file with line-based operations
- **MutexDialogModel.py**: Model for Mutex relationships dialog
- **LazyLoadingListModel.py**: Custom model for efficiently handling large datasets

### Views (src/views/)

Views represent the user interface components:

- **AbstractDialogView.py**: Base class defining common behaviors for dialog views
- **AfDialogView.py**: UI for Activity Factor configuration dialog
- **DocumentListView.py**: Displays document content as a list of lines
- **MutexDialogView.py**: UI for Mutex Configuration dialog

### Controllers (src/controllers/)

Controllers coordinate interactions between models and views:

- **AbstractDialogController.py**: Base controller for dialog interaction
- **AfDialogController.py**: Controller for the AF dialog, handling user interactions
- **DocumentController.py**: Main controller managing document operations
- **MutexDialogController.py**: Controller for the Mutex dialog interactions

### Managers (src/managers/)

Managers handle specific aspects of application functionality:

- **LotusFilesManager.py**: Manages file operations and paths
- **LotusActionManager.py**: Coordinates application actions and commands
- **LotusTabManager.py**: Controls tab-based navigation
- **LotusThemeManager.py**: Handles application theming
- **LotusUIManager.py**: Manages UI components and layouts

### Services (src/services/)

Services provide core functionality used across the application:

- **PatternMatcher.py**: Core service for pattern matching operations
- **LotusConfig.py**: Configuration settings and constants
- **LotusUtisls.py**: General utility functions

### Widgets (src/widgets/)

Custom UI components:

- **LotusHeader.py**: Header widget for the application
- **MatchResultsListView.py**: Specialized list view for pattern matching results

### Factories (src/factories/)

Create complex objects:

- **TabFactory.py**: Creates and configures application tabs

## Design Patterns

The Lotus application employs several design patterns:

### 1. Model-View-Controller (MVC)

The core architecture follows the MVC pattern, separating data (Models), user interface (Views), and application logic (Controllers).

**Example**:
- `AfLineModel` (Model) represents an AF configuration line
- `AfDialogView` (View) displays the UI for AF configuration
- `AfDialogController` (Controller) manages user interactions with the AF dialog

### 2. Abstract Factory

The `TabFactory` implements the Abstract Factory pattern to create families of related objects.

**Example**:
- `TabFactory` creates different tab types with consistent interfaces

### 3. Singleton

Used for services that should have only one instance throughout the application.

**Example**:
- `PatternMatcher` is a singleton to ensure consistent pattern matching

### 4. Observer

Implemented through PyQt's signals and slots mechanism to notify components of state changes.

**Example**:
- Views emit signals when user actions occur
- Controllers connect to these signals to respond to user actions

### 5. Command

Used in the undo/redo functionality to encapsulate operations as objects.

**Example**:
- `DocumentModel` tracks actions for undo/redo operations

### 6. Strategy

Different strategies for handling different configuration file types.

**Example**:
- Different line model classes provide specific validation strategies

## Data Flow

The application's data flow follows these general patterns:

1. **User Input Flow**:
   - User interacts with a View component
   - View emits a signal
   - Controller receives the signal and updates the Model
   - Model performs business logic and updates its state
   - View reflects the updated state

2. **File Operation Flow**:
   - Controller requests file operation from LotusFilesManager
   - Files are loaded into appropriate Models
   - Models parse and validate the content
   - Views are updated to reflect the loaded data

3. **Pattern Matching Flow**:
   - User inputs search criteria in a View
   - Controller sends matching request to PatternMatcher service
   - PatternMatcher performs the search
   - Results are returned to the Controller
   - Controller updates the Model with matches
   - View displays the matching results

## Component Relationships

### Main Application Flow

1. The application entry point is `main.py`, which initializes the Qt application and creates the main Lotus window
2. `Lotus.py` creates and connects the core components:
   - `LotusUIManager` builds the main window UI
   - `LotusFilesManager` handles file operations
   - `LotusTabManager` manages application tabs
   - `LotusActionManager` coordinates application actions

### Dialog Management

1. Dialog controllers (`AfDialogController`, `MutexDialogController`) are created by the tab factory
2. Each controller creates and connects its corresponding model and view
3. Models interact with services like `PatternMatcher` to perform operations
4. Views update the UI based on model state changes

### Document Handling

1. `DocumentController` manages a `DocumentModel` representing a configuration file
2. `DocumentListView` displays the document content
3. Line models validate individual lines
4. Changes trigger updates through the MVC pattern


## Configuration Management

Application configuration is managed through:

1. `LotusConfig` provides application-wide settings
2. Command-line arguments set initial paths and parameters
3. Configuration files define specific behavior

## File Formats

The application handles the following file formats:

1. **Spice Files (.sp)**:
   - Circuit netlist in standard SPICE format

2. **Activity Factor Files (.af.dcfg)**:
   - Configuration format: `{template:net} AF_VALUE [flags]`
   - Examples of flags: `template-regexp`, `net-regexp`, `_em`, `_sh`


## Performance Considerations

Several strategies are employed to ensure good performance:

1. **Lazy Loading**:
   - `LazyLoadingListModel` provides efficient handling of large datasets
   - Only visible items are processed and rendered

2. **Caching**:
   - `PatternMatcher` caches results to avoid redundant calculations
   - The `lru_cache` decorator is used for function-level caching


