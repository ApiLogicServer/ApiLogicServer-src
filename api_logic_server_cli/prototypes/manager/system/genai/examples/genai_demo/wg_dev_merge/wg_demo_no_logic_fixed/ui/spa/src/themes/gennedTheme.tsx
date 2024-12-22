import { createTheme } from '@mui/material/styles';

const customPalette = {
    "palette": {
        "primary": {
            "main": "#3f51b5", // Indigo
            "light": "#757de8", // Light Indigo
            "dark": "#002984", // Dark Indigo
            "contrastText": "#fff" // Text color on primary color background
        },
        "secondary": {
            "main": "#f50057", // Pink
            "light": "#ff5983", // Light Pink
            "dark": "#bb002f", // Dark Pink
            "contrastText": "#fff" // Text color on secondary color background
        },
        "background": {
            "default": "#e0f7fa", // Light Cyan
            "paper": "#ffffff" // Background color for paper components
        },
        "text": {
            "primary": "#000000", // Primary text color
            "secondary": "#757575", // Secondary text color
            "disabled": "rgba(0, 0, 0, 0.38)" // Disabled text color
        },
        "error": {
            "main": "#d32f2f", // Error color
            "light": "#ef5350", // Lighter shade of error color
            "dark": "#c62828", // Darker shade of error color
            "contrastText": "#fff" // Text color on error color background
        },
        "warning": {
            "main": "#ffa000", // Warning color
            "light": "#ffb74d", // Lighter shade of warning color
            "dark": "#f57c00", // Darker shade of warning color
            "contrastText": "#fff" // Text color on warning color background
        },
        "info": {
            "main": "#1976d2", // Info color
            "light": "#64b5f6", // Lighter shade of info color
            "dark": "#1565c0", // Darker shade of info color
            "contrastText": "#fff" // Text color on info color background
        },
        "success": {
            "main": "#388e3c", // Success color
            "light": "#81c784", // Lighter shade of success color
            "dark": "#2e7d32", // Darker shade of success color
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
            "color": "#3f51b5" // Indigo for h1 headers
        },
        "h2": {
            "color": "#3f51b5" // Indigo for h2 headers
        },
        "h3": {
            "color": "#3f51b5" // Indigo for h3 headers
        },
        "h4": {
            "color": "#3f51b5" // Indigo for h4 headers
        },
        "h5": {
            "color": "#3f51b5" // Indigo for h5 headers
        },
        "h6": {
            "color": "#3f51b5" // Indigo for h6 headers
        },
        "body1": {
            "color": "#000000" // Black for body1 text
        },
        "body2": {
            "color": "#000000" // Black for body2 text
        }
    }
};

const theme = createTheme(customPalette);

export default theme;