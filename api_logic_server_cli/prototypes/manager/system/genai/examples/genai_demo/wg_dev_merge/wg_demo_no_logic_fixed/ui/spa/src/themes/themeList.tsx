import { createTheme } from '@mui/material/styles';
import gennedTheme from './gennedTheme';
import greenTheme from './greenTheme.tsx';
import pastelTheme from './pastel.tsx';
import defaultTheme from './default.tsx';

export const themes = {
    default: createTheme(defaultTheme),
    purple: createTheme(gennedTheme),
    green: createTheme(greenTheme),
    pastel: createTheme(pastelTheme),
};
