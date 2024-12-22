import React, { useEffect, useState, Suspense } from 'react';
import { Box, Typography, Button, useMediaQuery, useTheme } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import ErrorBoundary from '../ErrorBoundary';
import { SectionBox } from './Section';
import { useTour } from '@reactour/tour'
import { TourProvider } from '@reactour/tour'
import {steps} from './steps.tsx'


const HeroSection = ({ section }) => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
    const [HighLight, setHighLight] = useState<any>(null);
    const { setIsOpen, isOpen } = useTour()

    useEffect(() => {
        
        if(! localStorage.getItem('doneTour')){
            setIsOpen(true)
        }
        localStorage.setItem('doneTour', 'true');
        
        const loadComponent = async () => {
            // Dynamic import of the HighLight component because it's AI-generated and untested
            try {
                const { default: Component } = await import('./HighLight');
                setHighLight(<ErrorBoundary><Component /></ErrorBoundary>);
            } catch (error) {
                console.error('Failed to load the dynamic component:', error);
                setHighLight(<div>Failed to load the highlight component.</div>);
            }
        };
        loadComponent();
    }, []);

    useEffect(() => {
        if (!isOpen) {
            window.scrollTo(0, 0);
        }
    }, [isOpen]);

    const handleClick = () => {
        sessionStorage.removeItem('raSpa');
        window.location.href = window.location.href.split('#')[0];
    };

    console.log("HeroSection", section);

    return (
        <>
            <SectionBox display="flex" flexDirection={isMobile ? 'column' : 'row'} height="90vh">
        
                {/* Left Pane */}
                <Box
                    flex={1}
                    display="flex"
                    justifyContent="center"
                    alignItems="center"
                    sx={{ width: isMobile ? '100%' : '30%', padding: isMobile ? '1em' : '0' }}
                >
                    <div>
                        <Typography variant="h2">
                            {section.title}
                            <Typography sx={{ fontStyle: 'italic', fontSize: '1.1rem' }}>
                                {section.subtitle}
                                <Button
                                    className="first-step"
                                    variant="contained"
                                    color="primary"
                                    href="#contact"
                                    onClick={handleClick}
                                    sx={{
                                        width: isMobile ? '100%' : '92%',
                                        padding: '8px',
                                        marginTop: '1em',
                                        marginBlockEnd: '0.67em',
                                        fontStyle: 'normal'
                                    }}
                                >   Backend Admin
                                </Button>
                            </Typography>
                        </Typography>

                        <Box mt={2} style={{ marginTop: '2em', fontSize: '0.75rem', marginBlockEnd: '0.67em' }}>
                            <ReactMarkdown>{section.content}</ReactMarkdown>
                        </Box>
                    </div>
                </Box>

                {/* Right Pane */}
                <Box
                    flex={2}
                    onClick={handleClick}
                    sx={{
                        backgroundImage: `url('${section.background}')`,
                        backgroundSize: 'cover',
                        backgroundPosition: 'center',
                        backgroundRepeat: 'no-repeat',
                        width: isMobile ? '100%' : '70%',
                        height: isMobile ? '50vh' : '100%',
                    }}
                ></Box>

            </SectionBox>
            <SectionBox flex={1} sx={{paddingBottom: "4em", paddingTop:"2em"}} className="second-step">
                <Suspense fallback={<div>Loading...</div>}>{HighLight || <div>Loading component...</div>}</Suspense>
            </SectionBox>
            
        </>
    );
};

const HeroTour = (props:any) => {
    return (
        <TourProvider steps={steps}>
            <HeroSection {...props}/>
        </TourProvider>
    );
}

export default HeroTour;