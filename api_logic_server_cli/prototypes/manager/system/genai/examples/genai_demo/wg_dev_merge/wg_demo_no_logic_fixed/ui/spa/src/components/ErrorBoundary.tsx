import React, { Component, ErrorInfo } from 'react';
import { Typography, Link } from '@mui/material';

interface ErrorBoundaryProps {
    children: React.ReactNode;
}

interface ErrorBoundaryState {
    hasError: boolean;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error) {
        // Update state so the next render will show the fallback UI.
        return { hasError: true };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        // Log the error to an error reporting service
        console.error("Error caught by Error Boundary:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            // Fallback UI
            return <>
            <Typography variant='h4'>Something went wrong.</Typography>
            <Link component="button" onClick={() => document.location.reload()}>Reload</Link>

            </>
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
