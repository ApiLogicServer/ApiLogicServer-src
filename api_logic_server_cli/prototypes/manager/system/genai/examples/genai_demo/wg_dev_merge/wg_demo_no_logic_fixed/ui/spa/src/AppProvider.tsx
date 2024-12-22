// AppContext.tsx
import React, { createContext, useState, useContext, ReactNode } from 'react';
import { ThemeProvider as MuiThemeProvider, Theme } from '@mui/material/styles';
import { themes } from './themes/themeList';

// Define a type for the context value
interface AppContextType {
    appId: string;
    setAppId: React.Dispatch<React.SetStateAction<string>>;
    appName: string;
    setAppName: React.Dispatch<React.SetStateAction<string>>;
    appVersion: number;
    setAppVersion: any;
    theme: Theme;
    setTheme: (themeName: string) => void;
}

// Create a context for the appId, appName, and theme
const AppContext = createContext<AppContextType | null>(null);

// Create a provider component
const AppProvider = ({ children }: { children: ReactNode }) => {
    const [appId, setAppId] = useState('');
    const [appName, setAppName] = useState('');
    const [appVersion, setAppVersion2] = useState<number>(0);
    const [theme, setTheme] = useState<Theme>(themes.default);

    const setAppVersion = (value: number) => {
        console.log('setAppVersion', value);
        setAppVersion2(value);
        return value;
    };

    const changeTheme = (themeName: string) => {
        setTheme(themes[themeName]);
    };

    return (
        <AppContext.Provider value={{ appId, setAppId, appName, setAppName, appVersion, setAppVersion, theme, setTheme: changeTheme }}>
            <MuiThemeProvider theme={theme}>
                {children}
            </MuiThemeProvider>
        </AppContext.Provider>
    );
};

// Custom hook to use the AppContext
const useAppContext = () => {
    return useContext(AppContext);
};

export { AppProvider, useAppContext };