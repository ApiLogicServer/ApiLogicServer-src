import { createTheme } from '@mui/material/styles';
import { AppBar, Toolbar } from '@mui/material';
import { styled } from '@mui/system';

const theme0 = createTheme({
    palette: {
        primary: {
            main: '#6200ea', // Deep Purple
        },
        secondary: {
            main: '#03dac6', // Teal
        },
        background: {
            default: '#f5f5f5', // Light Grey
            paper: '#ffffff', // White
        },
        text: {
            primary: '#212121', // Dark Grey
            secondary: '#757575', // Medium Grey
        },
    },
    typography: {
        fontFamily: 'Roboto, Arial, sans-serif',
        h1: {
            fontSize: '2.5rem',
            fontWeight: 500,
            color: '#212121',
        },
        h2: {
            fontSize: '2rem',
            fontWeight: 500,
            color: '#212121',
        },
        h3: {
            fontSize: '1.75rem',
            fontWeight: 500,
            color: '#212121',
        },
        h4: {
            fontSize: '1.5rem',
            fontWeight: 500,
            color: '#212121',
        },
        h5: {
            fontSize: '1.25rem',
            fontWeight: 500,
            color: '#212121',
        },
        h6: {
            fontSize: '1rem',
            fontWeight: 500,
            color: '#212121',
        },
        body1: {
            fontSize: '1rem',
            color: '#757575',
        },
        body2: {
            fontSize: '0.875rem',
            color: '#757575',
        },
    },
    shape: {
        borderRadius: 8,
    },
    spacing: 8,
});

const theme = createTheme({});

export const StyledAppBar = styled(AppBar)({
    position: 'fixed',
    backgroundColor: '#222',
    height: '4.5em',
});

export const StyledToolBar = styled(Toolbar)({
    display: 'flex',
    justifyContent: 'space-between',
});



export default theme;