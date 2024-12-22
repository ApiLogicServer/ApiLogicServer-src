import { createTheme } from '@mui/material/styles';

const customPalette = {
    "palette": {
        "primary": {
            "main": "#4caf50", // Primary color for buttons, links, etc.
            "light": "rgb(102, 187, 106)", // Lighter shade of primary color
            "dark": "rgb(56, 142, 60)", // Darker shade of primary color
            "contrastText": "#fff" // Text color on primary color background
        },
        "secondary": {
            "main": "#ff9800", // Secondary color for buttons, links, etc.
            "light": "rgb(255, 183, 77)", // Lighter shade of secondary color
            "dark": "rgb(230, 81, 0)", // Darker shade of secondary color
            "contrastText": "rgba(0, 0, 0, 0.87)" // Text color on secondary color background
        },
        "background": {
            "default": "#f0f4c3", // Default background color
            "paper": "#ffffff" // Background color for paper components
        },
        "text": {
            "primary": "#222222", // Primary text color
            "secondary": "#388e3c", // Secondary text color
            "disabled": "rgba(0, 0, 0, 0.38)" // Disabled text color
        },
        "error": {
            "main": "#f44336", // Error color
            "light": "#e57373", // Lighter shade of error color
            "dark": "#d32f2f", // Darker shade of error color
            "contrastText": "#fff" // Text color on error color background
        },
        "warning": {
            "main": "#ff9800", // Warning color
            "light": "#ffb74d", // Lighter shade of warning color
            "dark": "#f57c00", // Darker shade of warning color
            "contrastText": "#fff" // Text color on warning color background
        },
        "info": {
            "main": "#2196f3", // Info color
            "light": "#64b5f6", // Lighter shade of info color
            "dark": "#1976d2", // Darker shade of info color
            "contrastText": "#fff" // Text color on info color background
        },
        "success": {
            "main": "#4caf50", // Success color
            "light": "#81c784", // Lighter shade of success color
            "dark": "#388e3c", // Darker shade of success color
            "contrastText": "#fff" // Text color on success color background
        },
        "grey": {
            "50": "#fafafa", // Lightest grey
            "100": "#f5f5f5", // Very light grey
            "200": "#eeeeee", // Light grey
            "300": "#e0e0e0", // Medium light grey
            "400": "#bdbdbd", // Medium grey
            "500": "#9e9e9e", // Medium dark grey
            "600": "#757575", // Dark grey
            "700": "#616161", // Darker grey
            "800": "#424242", // Very dark grey
            "900": "#212121", // Darkest grey
            "A100": "#f5f5f5", // Light grey (alternative)
            "A200": "#eeeeee", // Light grey (alternative)
            "A400": "#bdbdbd", // Medium grey (alternative)
            "A700": "#616161" // Dark grey (alternative)
        },
        "divider": "rgba(0, 0, 0, 0.12)", // Divider color
        "action": {
            "active": "rgba(0, 0, 0, 0.54)", // Active action color
            "hover": "rgba(0, 0, 0, 0.04)", // Hover action color
            "hoverOpacity": 0.04, // Hover opacity
            "selected": "rgba(0, 0, 0, 0.08)", // Selected action color
            "selectedOpacity": 0.08, // Selected opacity
            "disabled": "rgba(0, 0, 0, 0.26)", // Disabled action color
            "disabledBackground": "rgba(0, 0, 0, 0.12)", // Disabled background color
            "disabledOpacity": 0.38, // Disabled opacity
            "focus": "rgba(0, 0, 0, 0.12)", // Focus action color
            "focusOpacity": 0.12, // Focus opacity
            "activatedOpacity": 0.12 // Activated opacity
        }
    },
    "typography": {
        "h1": {
            "color": "#1b5e20" // Color for h1 headers
        },
        "h2": {
            "color": "#1b5e20" // Color for h2 headers
        },
        "h3": {
            "color": "#1b5e20" // Color for h3 headers
        },
        "h4": {
            "color": "#1b5e20" // Color for h4 headers
        },
        "h5": {
            "color": "#1b5e20" // Color for h5 headers
        },
        "h6": {
            "color": "#1b5e20" // Color for h6 headers
        },
        "body1": {
            "color": "#000000" // Color for body1 text
        },
        "body2": {
            "color": "#000000" // Color for body2 text
        }
    }
};

export default customPalette;