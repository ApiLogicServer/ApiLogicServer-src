import { createTheme } from '@mui/material/styles';
import { AppBar, Toolbar } from '@mui/material';
import { styled } from '@mui/system';
import fullDefaultTheme from './fullDefaultTheme.tsx';
import gennedTheme from './gennedTheme.tsx';

function deepMerge(target, source) {
    for (const key in source) {
        if (source.hasOwnProperty(key)) {
            if (source[key] instanceof Object && key in target) {
                Object.assign(source[key], deepMerge(target[key], source[key]));
            }
        }
    }
    Object.assign(target || {}, source);
    return target;
}

const blueishTheme = createTheme({
    palette: {
        primary: {
            main: '#2196f3', // Blue
        },
        secondary: {
            main: '#64b5f6', // Light Blue
        },
        background: {
            default: '#e3f2fd', // Light Blue Grey
            paper: '#ffffff', // White
        },
        text: {
            primary: '#0d47a1', // Dark Blue
            secondary: '#1976d2', // Medium Blue
        },
    },
    typography: {
        fontFamily: 'Roboto, Arial, sans-serif',
        h1: {
            fontSize: '2.5rem',
            fontWeight: 500,
            color: '#0d47a1',
        },
        h2: {
            fontSize: '2rem',
            fontWeight: 500,
            color: '#0d47a1',
        },
        h3: {
            fontSize: '1.75rem',
            fontWeight: 500,
            color: '#0d47a1',
        },
        h4: {
            fontSize: '1.5rem',
            fontWeight: 500,
            color: '#0d47a1',
        },
        h5: {
            fontSize: '1.25rem',
            fontWeight: 500,
            color: '#0d47a1',
        },
        h6: {
            fontSize: '1rem',
            fontWeight: 500,
            color: '#0d47a1',
        },
        body1: {
            fontSize: '1rem',
            color: '#1976d2',
        },
        body2: {
            fontSize: '0.875rem',
            color: '#1976d2',
        },
    },
    shape: {
        borderRadius: 8,
    },
    spacing: 8,
});


export const StyledAppBar = styled(AppBar)(({ theme }) => ({
    position: 'fixed',
    backgroundColor: theme.palette.primary.main, // Use theme color
    height: '4.5em',
}));

export const StyledToolBar = styled(Toolbar)(({ theme }) => ({
    display: 'flex',
    justifyContent: 'space-between',
    padding: '0 16px',
}));

const baseTheme = createTheme({});
//deepMerge(baseTheme, gennedTheme);


export default baseTheme;