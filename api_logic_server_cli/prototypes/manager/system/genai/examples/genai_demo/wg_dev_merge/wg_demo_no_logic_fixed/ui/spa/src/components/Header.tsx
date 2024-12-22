import { Typography, Box, Button, IconButton, Menu, MenuItem, Link } from '@mui/material';
import { ISection } from '../interfaces.tsx';
import SettingsIcon from '@mui/icons-material/Settings';
import React, { useState } from 'react';
import { StyledAppBar, StyledToolBar } from '../themes/default.tsx';
import { useTheme } from '@mui/material/styles'
import { useTour } from '@reactour/tour'
import { TourProvider } from '@reactour/tour'
import {steps} from './sections/steps.tsx'



const Settings = () => {
    const theme = useTheme();
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const { setIsOpen } = useTour()

    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const pageRoot = document.location.href.split('#')[0];

    return (
        <div className="third-step">
            <IconButton edge="end" color="inherit" onClick={handleClick}>
                <SettingsIcon  sx={{color: `rgba(${theme.palette.primary.main}, 0.8)`}}/>
            </IconButton>
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleClose}
            >
                <MenuItem onClick={handleClose}>
                    <Link href={`${pageRoot}#/dev`} color="inherit" underline="none">AI Dev</Link>
                </MenuItem>
                <MenuItem onClick={handleClose}>
                    <Link href="#" color="inherit" underline="none">Backend Admin</Link>
                </MenuItem>
                <MenuItem onClick={handleClose}>
                    <Link href="/admin-app/#/Home" color="inherit" underline="none">User Settings</Link>
                </MenuItem>
                <MenuItem onClick={handleClose}>
                    <Link onClick={() => setIsOpen(true)} color="inherit" underline="none">Help</Link>
                </MenuItem>
            </Menu>
        </div>
    );
};

const Header = ({ title, SectionList }: { title: string; SectionList: ISection[] | undefined }) => {
    const theme = useTheme();
    const contrastColor = theme.palette.primary.contrastText
    const SRAappBarId = 'SRAheader';

    const scrollTo = (section: ISection) => {
        const element = document.getElementById(section.id);
        element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    if (!SectionList) return null;

    const sections = SectionList.sort((a: ISection, b: ISection) => a.order - b.order)
        .map((section: ISection) => {
            if((section.label || section.name).toLowerCase() === 'footer'){
                return null;
            }
            if((section.label || section.name).toLowerCase() === 'hero'){
                section.label = 'Home';
            }
            return <Button key={section.id} color="inherit" onClick={() => scrollTo(section)}>
                    {section.label || section.name}
                    </Button>;
            }
        );

    return (
        <StyledAppBar id={SRAappBarId}>
            <StyledToolBar>
                <Typography variant="h6" sx={{color:contrastColor}}>{title}</Typography>
                <Box sx={{ flexGrow: 1 }} />
                {sections}
                <Settings />
            </StyledToolBar>
        </StyledAppBar>
    );
};



const HeaderTour = (props:any) => {
    return (
        <TourProvider steps={steps}>
            <Header {...props}/>
        </TourProvider>
    );
}

export default HeaderTour;