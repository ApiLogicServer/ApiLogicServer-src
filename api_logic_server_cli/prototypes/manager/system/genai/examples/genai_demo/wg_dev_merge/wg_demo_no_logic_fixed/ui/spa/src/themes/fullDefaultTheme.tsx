const fullDefaultTheme = {  
    "breakpoints": {
        "keys": [
            "xs",
            "sm",
            "md",
            "lg",
            "xl"
        ],
        "values": {
            "xs": 0,
            "sm": 600,
            "md": 900,
            "lg": 1200,
            "xl": 1536
        },
        "unit": "px"
    },
    "direction": "ltr",
    "components": {},
    "palette": {
        "mode": "light",
        "primary": {
            "main": "#2196f3",
            "light": "rgb(77, 171, 245)",
            "dark": "rgb(23, 105, 170)",
            "contrastText": "#fff"
        },
        "secondary": {
            "main": "#64b5f6",
            "light": "rgb(131, 195, 247)",
            "dark": "rgb(70, 126, 172)",
            "contrastText": "rgba(0, 0, 0, 0.87)"
        },
        "background": {
            "default": "#e3f2fd",
            "paper": "#ffffff"
        },
        "text": {
            "primary": "#0d47a1",
            "secondary": "#1976d2",
            "disabled": "rgba(0, 0, 0, 0.38)"
        },
        "common": {
            "black": "#000",
            "white": "#fff"
        },
        "error": {
            "main": "#d32f2f",
            "light": "#ef5350",
            "dark": "#c62828",
            "contrastText": "#fff"
        },
        "warning": {
            "main": "#ed6c02",
            "light": "#ff9800",
            "dark": "#e65100",
            "contrastText": "#fff"
        },
        "info": {
            "main": "#0288d1",
            "light": "#03a9f4",
            "dark": "#01579b",
            "contrastText": "#fff"
        },
        "success": {
            "main": "#2e7d32",
            "light": "#4caf50",
            "dark": "#1b5e20",
            "contrastText": "#fff"
        },
        "grey": {
            "50": "#fafafa",
            "100": "#f5f5f5",
            "200": "#eeeeee",
            "300": "#e0e0e0",
            "400": "#bdbdbd",
            "500": "#9e9e9e",
            "600": "#757575",
            "700": "#616161",
            "800": "#424242",
            "900": "#212121",
            "A100": "#f5f5f5",
            "A200": "#eeeeee",
            "A400": "#bdbdbd",
            "A700": "#616161"
        },
        "contrastThreshold": 3,
        "tonalOffset": 0.2,
        "divider": "rgba(0, 0, 0, 0.12)",
        "action": {
            "active": "rgba(0, 0, 0, 0.54)",
            "hover": "rgba(0, 0, 0, 0.04)",
            "hoverOpacity": 0.04,
            "selected": "rgba(0, 0, 0, 0.08)",
            "selectedOpacity": 0.08,
            "disabled": "rgba(0, 0, 0, 0.26)",
            "disabledBackground": "rgba(0, 0, 0, 0.12)",
            "disabledOpacity": 0.38,
            "focus": "rgba(0, 0, 0, 0.12)",
            "focusOpacity": 0.12,
            "activatedOpacity": 0.12
        }
    },
    "shape": {
        "borderRadius": 8
    },
    "typography": {
        "fontFamily": "Roboto, Arial, sans-serif",
        "h1": {
            "fontSize": "2.5rem",
            "fontWeight": 500,
            "color": "#0d47a1",
            "fontFamily": "Roboto, Arial, sans-serif",
            "lineHeight": 1.167
        },
        "h2": {
            "fontSize": "2rem",
            "fontWeight": 500,
            "color": "#0d47a1",
            "fontFamily": "Roboto, Arial, sans-serif",
            "lineHeight": 1.2
        },
        "h3": {
            "fontSize": "1.75rem",
            "fontWeight": 500,
            "color": "#0d47a1",
            "fontFamily": "Roboto, Arial, sans-serif",
            "lineHeight": 1.167
        },
        "h4": {
            "fontSize": "1.5rem",
            "fontWeight": 500,
            "color": "#0d47a1",
            "fontFamily": "Roboto, Arial, sans-serif",
            "lineHeight": 1.235
        },
        "h5": {
            "fontSize": "1.25rem",
            "fontWeight": 500,
            "color": "#0d47a1",
            "fontFamily": "Roboto, Arial, sans-serif",
            "lineHeight": 1.334
        },
        "h6": {
            "fontSize": "1rem",
            "fontWeight": 500,
            "color": "#0d47a1",
            "fontFamily": "Roboto, Arial, sans-serif",
            "lineHeight": 1.6
        },
        "body1": {
            "fontSize": "1rem",
            "color": "#1976d2",
            "fontFamily": "Roboto, Arial, sans-serif",
            "fontWeight": 400,
            "lineHeight": 1.5
        },
        "body2": {
            "fontSize": "0.875rem",
            "color": "#1976d2",
            "fontFamily": "Roboto, Arial, sans-serif",
            "fontWeight": 400,
            "lineHeight": 1.43
        },
        "htmlFontSize": 16,
        "fontSize": 14,
        "fontWeightLight": 300,
        "fontWeightRegular": 400,
        "fontWeightMedium": 500,
        "fontWeightBold": 700,
        "subtitle1": {
            "fontFamily": "Roboto, Arial, sans-serif",
            "fontWeight": 400,
            "fontSize": "1rem",
            "lineHeight": 1.75
        },
        "subtitle2": {
            "fontFamily": "Roboto, Arial, sans-serif",
            "fontWeight": 500,
            "fontSize": "0.875rem",
            "lineHeight": 1.57
        },
        "button": {
            "fontFamily": "Roboto, Arial, sans-serif",
            "fontWeight": 500,
            "fontSize": "0.875rem",
            "lineHeight": 1.75,
            "textTransform": "uppercase"
        },
        "caption": {
            "fontFamily": "Roboto, Arial, sans-serif",
            "fontWeight": 400,
            "fontSize": "0.75rem",
            "lineHeight": 1.66
        },
        "overline": {
            "fontFamily": "Roboto, Arial, sans-serif",
            "fontWeight": 400,
            "fontSize": "0.75rem",
            "lineHeight": 2.66,
            "textTransform": "uppercase"
        },
        "inherit": {
            "fontFamily": "inherit",
            "fontWeight": "inherit",
            "fontSize": "inherit",
            "lineHeight": "inherit",
            "letterSpacing": "inherit"
        }
    },
    "sidebar": {
        "width": 240,
        "closedWidth": 50
    },
    "unstable_sxConfig": {
        "border": {
            "themeKey": "borders"
        },
        "borderTop": {
            "themeKey": "borders"
        },
        "borderRight": {
            "themeKey": "borders"
        },
        "borderBottom": {
            "themeKey": "borders"
        },
        "borderLeft": {
            "themeKey": "borders"
        },
        "borderColor": {
            "themeKey": "palette"
        },
        "borderTopColor": {
            "themeKey": "palette"
        },
        "borderRightColor": {
            "themeKey": "palette"
        },
        "borderBottomColor": {
            "themeKey": "palette"
        },
        "borderLeftColor": {
            "themeKey": "palette"
        },
        "outline": {
            "themeKey": "borders"
        },
        "outlineColor": {
            "themeKey": "palette"
        },
        "borderRadius": {
            "themeKey": "shape.borderRadius"
        },
        "color": {
            "themeKey": "palette"
        },
        "bgcolor": {
            "themeKey": "palette",
            "cssProperty": "backgroundColor"
        },
        "backgroundColor": {
            "themeKey": "palette"
        },
        "p": {},
        "pt": {},
        "pr": {},
        "pb": {},
        "pl": {},
        "px": {},
        "py": {},
        "padding": {},
        "paddingTop": {},
        "paddingRight": {},
        "paddingBottom": {},
        "paddingLeft": {},
        "paddingX": {},
        "paddingY": {},
        "paddingInline": {},
        "paddingInlineStart": {},
        "paddingInlineEnd": {},
        "paddingBlock": {},
        "paddingBlockStart": {},
        "paddingBlockEnd": {},
        "m": {},
        "mt": {},
        "mr": {},
        "mb": {},
        "ml": {},
        "mx": {},
        "my": {},
        "margin": {},
        "marginTop": {},
        "marginRight": {},
        "marginBottom": {},
        "marginLeft": {},
        "marginX": {},
        "marginY": {},
        "marginInline": {},
        "marginInlineStart": {},
        "marginInlineEnd": {},
        "marginBlock": {},
        "marginBlockStart": {},
        "marginBlockEnd": {},
        "displayPrint": {
            "cssProperty": false
        },
        "display": {},
        "overflow": {},
        "textOverflow": {},
        "visibility": {},
        "whiteSpace": {},
        "flexBasis": {},
        "flexDirection": {},
        "flexWrap": {},
        "justifyContent": {},
        "alignItems": {},
        "alignContent": {},
        "order": {},
        "flex": {},
        "flexGrow": {},
        "flexShrink": {},
        "alignSelf": {},
        "justifyItems": {},
        "justifySelf": {},
        "gap": {},
        "rowGap": {},
        "columnGap": {},
        "gridColumn": {},
        "gridRow": {},
        "gridAutoFlow": {},
        "gridAutoColumns": {},
        "gridAutoRows": {},
        "gridTemplateColumns": {},
        "gridTemplateRows": {},
        "gridTemplateAreas": {},
        "gridArea": {},
        "position": {},
        "zIndex": {
            "themeKey": "zIndex"
        },
        "top": {},
        "right": {},
        "bottom": {},
        "left": {},
        "boxShadow": {
            "themeKey": "shadows"
        },
        "width": {},
        "maxWidth": {},
        "minWidth": {},
        "height": {},
        "maxHeight": {},
        "minHeight": {},
        "boxSizing": {},
        "font": {
            "themeKey": "font"
        },
        "fontFamily": {
            "themeKey": "typography"
        },
        "fontSize": {
            "themeKey": "typography"
        },
        "fontStyle": {
            "themeKey": "typography"
        },
        "fontWeight": {
            "themeKey": "typography"
        },
        "letterSpacing": {},
        "textTransform": {},
        "lineHeight": {},
        "textAlign": {},
        "typography": {
            "cssProperty": false,
            "themeKey": "typography"
        }
    },
    "mixins": {
        "toolbar": {
            "minHeight": 56,
            "@media (min-width:0px)": {
                "@media (orientation: landscape)": {
                    "minHeight": 48
                }
            },
            "@media (min-width:600px)": {
                "minHeight": 64
            }
        }
    },
    "shadows": [
        "none",
        "0px 2px 1px -1px rgba(0,0,0,0.2),0px 1px 1px 0px rgba(0,0,0,0.14),0px 1px 3px 0px rgba(0,0,0,0.12)",
        "0px 3px 1px -2px rgba(0,0,0,0.2),0px 2px 2px 0px rgba(0,0,0,0.14),0px 1px 5px 0px rgba(0,0,0,0.12)",
        "0px 3px 3px -2px rgba(0,0,0,0.2),0px 3px 4px 0px rgba(0,0,0,0.14),0px 1px 8px 0px rgba(0,0,0,0.12)",
        "0px 2px 4px -1px rgba(0,0,0,0.2),0px 4px 5px 0px rgba(0,0,0,0.14),0px 1px 10px 0px rgba(0,0,0,0.12)",
        "0px 3px 5px -1px rgba(0,0,0,0.2),0px 5px 8px 0px rgba(0,0,0,0.14),0px 1px 14px 0px rgba(0,0,0,0.12)",
        "0px 3px 5px -1px rgba(0,0,0,0.2),0px 6px 10px 0px rgba(0,0,0,0.14),0px 1px 18px 0px rgba(0,0,0,0.12)",
        "0px 4px 5px -2px rgba(0,0,0,0.2),0px 7px 10px 1px rgba(0,0,0,0.14),0px 2px 16px 1px rgba(0,0,0,0.12)",
        "0px 5px 5px -3px rgba(0,0,0,0.2),0px 8px 10px 1px rgba(0,0,0,0.14),0px 3px 14px 2px rgba(0,0,0,0.12)",
        "0px 5px 6px -3px rgba(0,0,0,0.2),0px 9px 12px 1px rgba(0,0,0,0.14),0px 3px 16px 2px rgba(0,0,0,0.12)",
        "0px 6px 6px -3px rgba(0,0,0,0.2),0px 10px 14px 1px rgba(0,0,0,0.14),0px 4px 18px 3px rgba(0,0,0,0.12)",
        "0px 6px 7px -4px rgba(0,0,0,0.2),0px 11px 15px 1px rgba(0,0,0,0.14),0px 4px 20px 3px rgba(0,0,0,0.12)",
        "0px 7px 8px -4px rgba(0,0,0,0.2),0px 12px 17px 2px rgba(0,0,0,0.14),0px 5px 22px 4px rgba(0,0,0,0.12)",
        "0px 7px 8px -4px rgba(0,0,0,0.2),0px 13px 19px 2px rgba(0,0,0,0.14),0px 5px 24px 4px rgba(0,0,0,0.12)",
        "0px 7px 9px -4px rgba(0,0,0,0.2),0px 14px 21px 2px rgba(0,0,0,0.14),0px 5px 26px 4px rgba(0,0,0,0.12)",
        "0px 8px 9px -5px rgba(0,0,0,0.2),0px 15px 22px 2px rgba(0,0,0,0.14),0px 6px 28px 5px rgba(0,0,0,0.12)",
        "0px 8px 10px -5px rgba(0,0,0,0.2),0px 16px 24px 2px rgba(0,0,0,0.14),0px 6px 30px 5px rgba(0,0,0,0.12)",
        "0px 8px 11px -5px rgba(0,0,0,0.2),0px 17px 26px 2px rgba(0,0,0,0.14),0px 6px 32px 5px rgba(0,0,0,0.12)",
        "0px 9px 11px -5px rgba(0,0,0,0.2),0px 18px 28px 2px rgba(0,0,0,0.14),0px 7px 34px 6px rgba(0,0,0,0.12)",
        "0px 9px 12px -6px rgba(0,0,0,0.2),0px 19px 29px 2px rgba(0,0,0,0.14),0px 7px 36px 6px rgba(0,0,0,0.12)",
        "0px 10px 13px -6px rgba(0,0,0,0.2),0px 20px 31px 3px rgba(0,0,0,0.14),0px 8px 38px 7px rgba(0,0,0,0.12)",
        "0px 10px 13px -6px rgba(0,0,0,0.2),0px 21px 33px 3px rgba(0,0,0,0.14),0px 8px 40px 7px rgba(0,0,0,0.12)",
        "0px 10px 14px -6px rgba(0,0,0,0.2),0px 22px 35px 3px rgba(0,0,0,0.14),0px 8px 42px 7px rgba(0,0,0,0.12)",
        "0px 11px 14px -7px rgba(0,0,0,0.2),0px 23px 36px 3px rgba(0,0,0,0.14),0px 9px 44px 8px rgba(0,0,0,0.12)",
        "0px 11px 15px -7px rgba(0,0,0,0.2),0px 24px 38px 3px rgba(0,0,0,0.14),0px 9px 46px 8px rgba(0,0,0,0.12)"
    ],
    "transitions": {
        "easing": {
            "easeInOut": "cubic-bezier(0.4, 0, 0.2, 1)",
            "easeOut": "cubic-bezier(0.0, 0, 0.2, 1)",
            "easeIn": "cubic-bezier(0.4, 0, 1, 1)",
            "sharp": "cubic-bezier(0.4, 0, 0.6, 1)"
        },
        "duration": {
            "shortest": 150,
            "shorter": 200,
            "short": 250,
            "standard": 300,
            "complex": 375,
            "enteringScreen": 225,
            "leavingScreen": 195
        }
    },
    "zIndex": {
        "mobileStepper": 1000,
        "fab": 1050,
        "speedDial": 1050,
        "appBar": 1100,
        "drawer": 1200,
        "modal": 1300,
        "snackbar": 1400,
        "tooltip": 1500
    }
}


export default fullDefaultTheme;